#!/usr/bin/env python3
"""Generate integration catalogs (JSON/YAML only).

For documentation generation, see generate-docs.py.
"""

import json
import re
import shutil
import subprocess
import yaml
from pathlib import Path
from typing import Dict

from manifest_utils import (
    CURRENT_BRANCH, BASE_URL,
    build_url, find_vendors, generate_vendor_manifest, parse_function_metadata, scan_case_templates, scan_dashboards,
    scan_notifications, scan_workflows
)


def _group_by(integrations: list, key: str, default: str = 'Other') -> Dict:
    grouped = {}
    for item in integrations:
        value = item.get(key, default)
        grouped.setdefault(value, []).append(item)
    return grouped


def generate_light_manifest(all_manifests: Dict) -> Dict:
    """Lightweight manifest for website/frontend consumption.

    Filters to displayOnWebsite=true, flattens logo, merges subscription fields.
    """
    light = {}

    for vendor_id, vendor in all_manifests.items():
        if not vendor.get('displayOnWebsite', False):
            continue

        raw_cat = vendor.get('category', '')
        category = raw_cat if isinstance(raw_cat, list) else ([raw_cat] if raw_cat else [])

        logo_obj = vendor.get('logo', {})
        logo_url = logo_obj.get('url', '') if isinstance(logo_obj, dict) else ''

        # Merge subscription booleans (handle arrays from mixed analyzer/responder values)
        def _resolve_bool(val):
            return any(val) if isinstance(val, list) else bool(val)

        old_stats = vendor.get('stats', {})

        light[vendor_id] = {
            'id': vendor.get('id', vendor_id),
            'name': vendor.get('name', vendor_id),
            'description': vendor.get('description', ''),
            'category': category,
            'tags': vendor.get('tags', []),
            'homepage': vendor.get('homepage', ''),
            'logo_url': logo_url,
            'visibility': vendor.get('visibility', 100),
            'subscription': {
                'required': _resolve_bool(vendor.get('registration_required', False)),
                'free': _resolve_bool(vendor.get('free_subscription', False)),
                'paid': _resolve_bool(vendor.get('subscription_required', False)),
            },
            'vendor_internal_page_content_url': f"{BASE_URL}/.generated/docs/vendors/{vendor_id}/overview.md",
            'stats': {
                'totalAnalyzers': old_stats.get('totalAnalyzers', 0),
                'totalResponders': old_stats.get('totalResponders', 0),
                'totalFunctions': old_stats.get('totalFunctions', 0),
                'totalUseCases': old_stats.get('totalUseCases', 0),
                'totalExternalIntegrations': old_stats.get('totalExternalIntegrations', 0),
                'totalNotifiers': old_stats.get('totalNotifiers', 0),
                'totalFlow': old_stats.get('totalFlow', 0),
                'totalWorkflows': old_stats.get('totalWorkflows', 0),
                'total': old_stats.get('total', 0),
            },
        }

    return light


def generate_visibility_sorted_catalog(all_manifests: Dict) -> Dict:
    """Catalog sorted by visibility tiers, then alphabetically."""
    catalog = {'high': [], 'medium': [], 'low': []}

    def _tier(visibility) -> str:
        if isinstance(visibility, str):
            return visibility if visibility in catalog else 'low'
        try:
            weight = int(visibility)
        except (TypeError, ValueError):
            return 'low'
        if weight <= 20:
            return 'high'
        if weight <= 50:
            return 'medium'
        return 'low'

    for manifest in all_manifests.values():
        catalog[_tier(manifest.get('visibility', 100))].append(manifest)

    for tier in catalog:
        catalog[tier].sort(key=lambda x: x['name'].lower())

    return {
        'metadata': {
            'description': 'Vendors sorted by visibility tier (high, medium, low), then alphabetically',
            'totalVendors': len(all_manifests),
            'highCount': len(catalog['high']),
            'mediumCount': len(catalog['medium']),
            'lowCount': len(catalog['low'])
        },
        **catalog
    }


def generate_external_integrations_catalog(all_manifests: Dict) -> Dict:
    external_integrations = []

    for vendor_id, manifest in all_manifests.items():
        for integration in manifest.get('externalIntegrations', []):
            external_integrations.append({
                'name': integration.get('name'),
                'vendor': manifest.get('name'),
                'vendorId': vendor_id,
                'type': integration.get('type'),
                'description': integration.get('description'),
                'documentation': integration.get('documentation'),
                'category': manifest.get('category')
            })

    external_integrations.sort(key=lambda x: (x['vendor'].lower(), x['name'].lower()))

    return {
        'totalIntegrations': len(external_integrations),
        'integrations': external_integrations,
        'byVendor': _group_by(external_integrations, 'vendor'),
        'byCategory': _group_by(external_integrations, 'category'),
        'byType': _group_by(external_integrations, 'type', 'unknown')
    }


# Steps that only move data or time around: not worth a node on the workflow card
WORKFLOW_HELPER_NODES = {'variable', 'sleep'}

# Icons of the TheHive Flow nodes that are not a vendor (thehive, cortex, code, http...): <node>.svg or <node>.png
FLOW_NODE_ICONS_DIR = Path('integrations/generic/assets/flow-nodes')

WORKFLOW_INTERNAL_FIELDS = ('export_name', 'spec_version', 'timeout', 'commands', 'inputs')

STRANGEBEE_AUTHOR = {
    'name': 'StrangeBee',
    'url': 'https://strangebee.com',
    'icon': 'https://strangebee.com/wp-content/themes/strange_bee/src/assets/fav/favicon-32x32.png',
}


def generate_workflows_catalog(all_manifests: Dict) -> Dict:
    """Catalog of TheHive Flow workflows, generic and vendor.

    Name, page url and description are declared by hand: in the `workflows:` list of vendor.yml,
    or in integrations/generic/thehive/workflows/_metadata.yml for generic ones. The export file
    lives next to them as thehive/workflows/<slug>.yml and only adds derived facts.
    """
    generic_root = Path('integrations/generic/thehive/workflows')
    generic_declared = []
    metadata_path = generic_root / '_metadata.yml'
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = yaml.safe_load(f)
            generic_declared = metadata.get('workflows') or [] if isinstance(metadata, dict) else []
            if not isinstance(generic_declared, list):
                generic_declared = []
        except (OSError, yaml.YAMLError) as e:
            print(f"  Warning: cannot read {metadata_path}: {e}")

    workflows = []
    for workflow in scan_workflows(generic_root, 'integrations/generic/thehive/workflows', generic_declared,
                                   {'type': 'generic', 'id': 'generic', 'name': 'Generic'}):
        workflows.append({**workflow, 'vendor': 'Generic', 'vendor_id': None, 'vendor_category': None})

    for vendor_id in find_vendors():
        manifest = all_manifests.get(vendor_id, {})
        vendor_name = _vendor_display_name(all_manifests, vendor_id)
        for workflow in scan_workflows(
                Path('integrations/vendors') / vendor_id / 'thehive' / 'workflows',
                f"integrations/vendors/{vendor_id}/thehive/workflows",
                manifest.get('workflows', []),
                {'type': 'vendor', 'id': vendor_id, 'name': vendor_name}):
            workflows.append({**workflow, 'vendor': vendor_name, 'vendor_id': vendor_id,
                              'vendor_category': manifest.get('category') or None})

    workflows.sort(key=lambda x: (x['vendor'].lower(), (x['name'] or '').lower()))

    def _norm(value: str) -> str:
        return ''.join(c for c in value.lower() if c.isalnum())

    # Only vendors that have a manifest, so every id given out exists in integration-manifest.json
    vendors_by_norm = {_norm(v): v for v in all_manifests}

    def _vendor_logo(vendor_id: str):
        logo = all_manifests.get(vendor_id, {}).get('logo')
        return logo.get('url') if isinstance(logo, dict) else None

    def _node_icon(name: str, node_vendor):
        # The node's own icon when one is stored, else the logo of the vendor it matches
        if re.fullmatch(r'[A-Za-z0-9_-]+', name):
            for extension in ('svg', 'png'):
                icon_path = FLOW_NODE_ICONS_DIR / f'{name}.{extension}'
                if icon_path.is_file():
                    return build_url(icon_path.as_posix())
        return _vendor_logo(node_vendor) if node_vendor else None

    for workflow in workflows:
        # Nodes shown on the workflow card: one per kind of step, flow-control helpers left out.
        # strangebee.integration.<name>.<version> -> <name>, strangebee.<kind>.<...> -> <kind>
        nodes = {}
        for command in workflow.get('commands', []):
            parts = command.split('.')
            if len(parts) < 2 or parts[0] != 'strangebee':
                continue
            name = parts[2] if parts[1] == 'integration' and len(parts) > 2 else parts[1]
            if name in WORKFLOW_HELPER_NODES or name in nodes:
                continue
            node_vendor = vendors_by_norm.get(_norm(name))
            nodes[name] = {'name': name, 'vendor_id': node_vendor, 'icon': _node_icon(name, node_vendor)}
        workflow['nodes'] = [nodes[name] for name in sorted(nodes)]

        # Vendors (manifest ids) the workflow belongs with: the one it is stored under, then any
        # vendor one of its nodes matches. Empty for a generic workflow that uses no vendor.
        related = [workflow['vendor_id']] if workflow['vendor_id'] in all_manifests else []
        related += sorted({node['vendor_id'] for node in workflow['nodes']
                           if node['vendor_id'] and node['vendor_id'] not in related})
        workflow['integrations'] = related

        # Author: as declared, else implied by who maintains the workflow
        if not workflow['author']:
            if workflow['maintainer'] == 'strangebee':
                workflow['author'] = [dict(STRANGEBEE_AUTHOR)]
            elif workflow['maintainer'] == 'partner' and workflow['vendor_id']:
                vendor_manifest = all_manifests.get(workflow['vendor_id'], {})
                workflow['author'] = [{'name': workflow['vendor'], 'url': vendor_manifest.get('homepage') or None,
                                       'icon': _vendor_logo(workflow['vendor_id'])}]
        # Read from the export to build the entry, but of no use to someone browsing the catalog
        for key in WORKFLOW_INTERNAL_FIELDS:
            workflow.pop(key, None)
        workflow['agent'] = False
        # Direct link to the export file, under the name the website expects (same as file_url)
        workflow['workflow'] = workflow.get('file_url')

    by_integration: Dict[str, list] = {}
    for workflow in workflows:
        for integration in workflow.get('integrations', []):
            by_integration.setdefault(integration, []).append(workflow)

    return {
        'total_count': len(workflows),
        # A workflow declared by several vendors is one workflow: same page url, else same id
        'unique_count': len({w.get('url') or w['id'] for w in workflows}),
        'generic_count': sum(1 for w in workflows if w['owner']['type'] == 'generic'),
        'vendor_count': sum(1 for w in workflows if w['owner']['type'] == 'vendor'),
        'with_file_count': sum(1 for w in workflows if w['has_file']),
        'workflows': workflows,
        'by_vendor': _group_by(workflows, 'vendor'),
        'by_integration': by_integration,
    }


def generate_workflows_library(wf_catalog: Dict) -> list:
    """The workflows catalog reduced to the shape the website's workflow library was specified with:
    a bare list, nine fields per workflow. Same data as the catalog, nothing added."""
    return [{
        'name': workflow['name'],
        'description': workflow['description'],
        'integrations': workflow['integrations'],
        'nodes': [{'name': node['name'], 'icon': node['icon']} for node in workflow['nodes']],
        'author': workflow['author'],
        'agent': workflow['agent'],
        'popular': workflow['popular'],
        'use_cases': workflow['use_cases'],
        'workflow': workflow['workflow'],
    } for workflow in wf_catalog['workflows'] if workflow['workflow']]


def generate_functions_catalog_data(all_manifests: Dict) -> Dict:
    generic_functions = []
    generic_path = Path('integrations/generic/functions')
    if generic_path.exists():
        for func_file in generic_path.glob('function_*.js'):
            metadata = parse_function_metadata(str(func_file))
            if metadata:
                generic_functions.append({
                    'name': metadata.get('name', func_file.stem),
                    'version': metadata.get('version', 'N/A'),
                    'description': metadata.get('description', 'No description available'),
                    'type': metadata.get('type', 'function'),
                    'kind': metadata.get('kind', 'function'),
                    'mode': metadata.get('mode', 'N/A'),
                    'file': str(func_file),
                    'vendor': 'Generic'
                })

    vendor_functions = []
    for vendor_id, manifest in all_manifests.items():
        for func in manifest.get('integrations', {}).get('functions', []):
            vendor_functions.append({
                **func,
                'vendor': manifest.get('name', vendor_id),
                'vendor_id': vendor_id
            })

    all_functions = generic_functions + vendor_functions
    return {
        'total_functions': len(all_functions),
        'generic_count': len(generic_functions),
        'vendor_count': len(vendor_functions),
        'functions': all_functions
    }


def _vendor_display_name(all_manifests: Dict, vendor_id: str) -> str:
    """Vendor name for catalog owners. Vendors whose only content is templates, dashboards or
    notifications have no manifest, so fall back to their vendor.yml, then to the directory name."""
    if vendor_id in all_manifests:
        return all_manifests[vendor_id].get('name', vendor_id)
    vendor_yml = Path('integrations/vendors') / vendor_id / 'vendor.yml'
    try:
        with open(vendor_yml, 'r', encoding='utf-8') as f:
            return (yaml.safe_load(f) or {}).get('name') or vendor_id
    except (OSError, yaml.YAMLError):
        return vendor_id


def generate_case_templates_catalog(all_manifests: Dict) -> Dict:
    """Catalog of TheHive case templates: generic packs plus any vendor-provided templates."""
    packs, templates = scan_case_templates(
        Path('integrations/generic/case-templates'),
        'integrations/generic/case-templates',
        {'type': 'generic', 'id': 'generic', 'name': 'Generic'},
    )

    # All vendor directories, not only those with a manifest: a vendor may ship templates and nothing else
    for vendor_id in find_vendors():
        vendor_name = _vendor_display_name(all_manifests, vendor_id)
        vendor_packs, vendor_templates = scan_case_templates(
            Path('integrations/vendors') / vendor_id / 'thehive' / 'case-templates',
            f"integrations/vendors/{vendor_id}/thehive/case-templates",
            {'type': 'vendor', 'id': vendor_id, 'name': vendor_name},
        )
        packs.extend(vendor_packs)
        templates.extend(vendor_templates)

    templates.sort(key=lambda t: (t['pack'].lower(), (t['name'] or '').lower()))
    packs.sort(key=lambda p: p['name'].lower())

    return {
        'total_templates': len(templates),
        'total_packs': len(packs),
        'generic_count': sum(1 for t in templates if t['owner']['type'] == 'generic'),
        'vendor_count': sum(1 for t in templates if t['owner']['type'] == 'vendor'),
        'packs': packs,
        'templates': templates,
        'byPack': _group_by(templates, 'pack'),
    }


def generate_notifications_catalog(all_manifests: Dict) -> Dict:
    """Catalog of TheHive notification filters: generic ones plus any vendor-provided ones."""
    notifications = scan_notifications(
        Path('integrations/generic/thehive/notifications'),
        'integrations/generic/thehive/notifications',
        {'type': 'generic', 'id': 'generic', 'name': 'Generic'},
    )
    for vendor_id in find_vendors():
        vendor_name = _vendor_display_name(all_manifests, vendor_id)
        notifications.extend(scan_notifications(
            Path('integrations/vendors') / vendor_id / 'thehive' / 'notifications',
            f"integrations/vendors/{vendor_id}/thehive/notifications",
            {'type': 'vendor', 'id': vendor_id, 'name': vendor_name},
        ))
    notifications.sort(key=lambda n: (n['name'] or '').lower())

    by_object_type: Dict[str, List[Dict]] = {}
    for notification in notifications:
        for object_type in notification['objectTypes'] or ['none']:
            by_object_type.setdefault(object_type, []).append(notification)

    return {
        'total_notifications': len(notifications),
        'generic_count': sum(1 for n in notifications if n['owner']['type'] == 'generic'),
        'vendor_count': sum(1 for n in notifications if n['owner']['type'] == 'vendor'),
        'notifications': notifications,
        'byObjectType': by_object_type,
    }


def generate_dashboards_catalog(all_manifests: Dict) -> Dict:
    """Catalog of TheHive dashboards: generic templates plus any vendor-provided ones."""
    dashboards = scan_dashboards(
        Path('integrations/generic/dashboard-templates'),
        'integrations/generic/dashboard-templates',
        {'type': 'generic', 'id': 'generic', 'name': 'Generic'},
    )

    for vendor_id in find_vendors():
        vendor_name = _vendor_display_name(all_manifests, vendor_id)
        dashboards.extend(scan_dashboards(
            Path('integrations/vendors') / vendor_id / 'thehive' / 'dashboards',
            f"integrations/vendors/{vendor_id}/thehive/dashboards",
            {'type': 'vendor', 'id': vendor_id, 'name': vendor_name},
        ))

    dashboards.sort(key=lambda d: (d['name'] or '').lower())

    by_entity = {}
    for dashboard in dashboards:
        for entity in dashboard['entities'] or ['none']:
            by_entity.setdefault(entity, []).append(dashboard)

    return {
        'total_dashboards': len(dashboards),
        'generic_count': sum(1 for d in dashboards if d['owner']['type'] == 'generic'),
        'vendor_count': sum(1 for d in dashboards if d['owner']['type'] == 'vendor'),
        'dashboards': dashboards,
        'byEntity': by_entity,
    }


def generate_github_summary(all_manifests: Dict, previous_manifests: Dict = None,
                            wf_catalog: Dict = None) -> Dict:
    # Workflows are counted from the catalog: all unique ones, generic included
    vendor_workflows = sum(m['stats'].get('totalWorkflows', 0) for m in all_manifests.values())
    unique_workflows = wf_catalog['unique_count'] if wf_catalog else vendor_workflows
    summary = {
        'total_vendors': len(all_manifests),
        'total_analyzers': sum(m['stats']['totalAnalyzers'] for m in all_manifests.values()),
        'total_responders': sum(m['stats']['totalResponders'] for m in all_manifests.values()),
        'total_functions': sum(m['stats']['totalFunctions'] for m in all_manifests.values()),
        'total_external_integrations': sum(m['stats'].get('totalExternalIntegrations', 0) for m in all_manifests.values()),
        'total_notifiers': sum(m['stats'].get('totalNotifiers', 0) for m in all_manifests.values()),
        'total_flow': sum(m['stats'].get('totalFlow', 0) for m in all_manifests.values()),
        'total_workflows': unique_workflows,
        'total_integrations': (sum(m['stats']['total'] for m in all_manifests.values())
                               - vendor_workflows + unique_workflows),
        'added': [], 'updated': [], 'removed': []
    }

    if previous_manifests:
        current = set(all_manifests.keys())
        previous = set(previous_manifests.keys())
        summary['added'] = sorted(current - previous, key=str.lower)
        summary['removed'] = sorted(previous - current, key=str.lower)

        for vendor in current & previous:
            cur_stats = all_manifests[vendor]['stats']
            prev_stats = previous_manifests[vendor]['stats']
            if cur_stats != prev_stats:
                summary['updated'].append({
                    'vendor': vendor,
                    'name': all_manifests[vendor]['name'],
                    'previous': prev_stats['total'],
                    'current': cur_stats['total'],
                    'change': cur_stats['total'] - prev_stats['total']
                })

    return summary


def write_github_summary(summary: Dict, output_path: Path):
    lines = ["# Catalog Generation Summary", "",
             "## Statistics", "",
             f"- **Total Vendors:** {summary['total_vendors']}",
             f"- **Total Analyzers:** {summary['total_analyzers']}",
             f"- **Total Responders:** {summary['total_responders']}",
             f"- **Total Functions:** {summary['total_functions']}",
             f"- **Total External Integrations:** {summary['total_external_integrations']}",
             f"- **Total Integrations:** {summary['total_integrations']}", ""]

    has_changes = summary['added'] or summary['removed'] or summary['updated']
    lines.extend(["## Changes", ""])

    if not has_changes:
        lines.append("No changes detected.")
    else:
        if summary['added']:
            lines.extend([f"### Added Vendors ({len(summary['added'])})", ""])
            lines.extend(f"- `{v}`" for v in summary['added'])
            lines.append("")
        if summary['removed']:
            lines.extend([f"### Removed Vendors ({len(summary['removed'])})", ""])
            lines.extend(f"- `{v}`" for v in summary['removed'])
            lines.append("")
        if summary['updated']:
            lines.extend([f"### Updated Vendors ({len(summary['updated'])})", ""])
            for item in summary['updated']:
                sign = "+" if item['change'] > 0 else ""
                lines.append(f"- **{item['name']}**: {item['previous']} -> {item['current']} ({sign}{item['change']})")
            lines.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def _write_yaml(path: Path, data, header_lines: list = None):
    with open(path, 'w', encoding='utf-8') as f:
        if header_lines:
            for line in header_lines:
                f.write(f"# {line}\n")
            f.write("\n")
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)


def _write_json(path: Path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    vendors = find_vendors()
    all_manifests = {}

    print(f"=== Catalog Generation ===")
    print(f"Using branch: {CURRENT_BRANCH}")
    print(f"Using base URL: {BASE_URL}\n")

    generated_path = Path('.generated')
    generated_path.mkdir(exist_ok=True)
    catalogs_path = generated_path / 'catalogs'
    catalogs_path.mkdir(exist_ok=True)
    vendors_catalogs_path = catalogs_path / 'vendors'
    vendors_catalogs_path.mkdir(exist_ok=True)

    # Clean up obsolete vendor catalogs
    if vendors_catalogs_path.exists():
        for vendor_dir in vendors_catalogs_path.iterdir():
            if vendor_dir.is_dir() and vendor_dir.name not in vendors:
                print(f"Cleaning up obsolete catalog: {vendor_dir.name}")
                shutil.rmtree(vendor_dir)

    # Generate vendor manifests
    print(f"\nGenerating manifests for {len(vendors)} vendors...")
    for vendor in vendors:
        print(f"  Processing {vendor}...")
        manifest = generate_vendor_manifest(vendor)
        if manifest['stats']['total'] == 0:
            print(f"    Skipping {vendor}: no content (0 analyzers, responders, functions, external integrations, workflows, notifier or flow)")
            continue
        all_manifests[vendor] = manifest

    # Workflows catalog. Built before the manifests are written, so that the `workflows` list of a
    # vendor manifest holds the very same entries as the catalog (defaults, nodes, author, links).
    wf_catalog = generate_workflows_catalog(all_manifests)
    for vendor, manifest in all_manifests.items():
        manifest['workflows'] = [w for w in wf_catalog['workflows']
                                 if w['owner']['type'] == 'vendor' and w['owner']['id'] == vendor]
        # Keep the counts in step with the list (it also holds export files with no declaration)
        added = len(manifest['workflows']) - manifest['stats'].get('totalWorkflows', 0)
        manifest['stats']['totalWorkflows'] = len(manifest['workflows'])
        manifest['stats']['total'] = manifest['stats'].get('total', 0) + added

    for vendor, manifest in all_manifests.items():
        vendor_catalog_path = vendors_catalogs_path / vendor
        vendor_catalog_path.mkdir(parents=True, exist_ok=True)

        _write_yaml(vendor_catalog_path / 'manifest.yml', manifest,
                     ["AUTO-GENERATED - DO NOT EDIT",
                      "Edit vendor.yml for vendor metadata, then re-run the generator"])
        _write_json(vendor_catalog_path / 'manifest.json', manifest)

    print(f"\n> Generated {len(vendors)} vendor catalogs in catalogs/vendors/")

    # Combined manifest
    _write_json(catalogs_path / 'integration-manifest.json', all_manifests)
    _write_yaml(catalogs_path / 'integration-manifest.yml', all_manifests)
    print(f"> Combined manifest written")

    # Light manifest
    light_manifest = generate_light_manifest(all_manifests)
    _write_json(catalogs_path / 'integration-light-manifest.json', light_manifest)
    print(f"> Light manifest: {len(light_manifest)} vendors")

    # External integrations catalog
    ext_catalog = generate_external_integrations_catalog(all_manifests)
    ext_path = catalogs_path / 'external-integrations'
    ext_path.mkdir(exist_ok=True)
    _write_json(ext_path / 'catalog.json', ext_catalog)
    _write_yaml(ext_path / 'catalog.yml', ext_catalog, ["AUTO-GENERATED - DO NOT EDIT"])
    print(f"> External integrations catalog written")

    # Workflows catalog (built above, with the manifests)
    wf_path = catalogs_path / 'workflows'
    wf_path.mkdir(exist_ok=True)
    _write_json(wf_path / 'catalog.json', wf_catalog)
    _write_yaml(wf_path / 'catalog.yml', wf_catalog, ["AUTO-GENERATED - DO NOT EDIT"])
    _write_json(wf_path / 'library.json', generate_workflows_library(wf_catalog))
    print(f"> Workflows catalog written")

    # Functions catalog
    func_catalog = generate_functions_catalog_data(all_manifests)
    func_path = catalogs_path / 'functions'
    func_path.mkdir(exist_ok=True)
    _write_json(func_path / 'catalog.json', func_catalog)
    _write_yaml(func_path / 'catalog.yml', func_catalog, ["AUTO-GENERATED - DO NOT EDIT"])
    print(f"> Functions catalog written")

    # Case templates catalog
    ct_catalog = generate_case_templates_catalog(all_manifests)
    ct_path = catalogs_path / 'case-templates'
    ct_path.mkdir(exist_ok=True)
    _write_json(ct_path / 'catalog.json', ct_catalog)
    _write_yaml(ct_path / 'catalog.yml', ct_catalog, ["AUTO-GENERATED - DO NOT EDIT"])
    print(f"> Case templates catalog: {ct_catalog['total_templates']} templates in {ct_catalog['total_packs']} packs")

    # Dashboards catalog
    db_catalog = generate_dashboards_catalog(all_manifests)
    db_path = catalogs_path / 'dashboards'
    db_path.mkdir(exist_ok=True)
    _write_json(db_path / 'catalog.json', db_catalog)
    _write_yaml(db_path / 'catalog.yml', db_catalog, ["AUTO-GENERATED - DO NOT EDIT"])
    print(f"> Dashboards catalog: {db_catalog['total_dashboards']} dashboards")

    # Notifications catalog
    nt_catalog = generate_notifications_catalog(all_manifests)
    nt_path = catalogs_path / 'notifications'
    nt_path.mkdir(exist_ok=True)
    _write_json(nt_path / 'catalog.json', nt_catalog)
    _write_yaml(nt_path / 'catalog.yml', nt_catalog, ["AUTO-GENERATED - DO NOT EDIT"])
    print(f"> Notifications catalog: {nt_catalog['total_notifications']} notifications")

    # Visibility-sorted catalog
    vis_catalog = generate_visibility_sorted_catalog(all_manifests)
    _write_json(catalogs_path / 'integration-catalog-visibility-sorted.json', vis_catalog)
    _write_yaml(catalogs_path / 'integration-catalog-visibility-sorted.yml', vis_catalog,
                 ["AUTO-GENERATED - DO NOT EDIT",
                  "Vendors sorted by visibility tier (high, medium, low), then alphabetically"])
    print(f"> Visibility-sorted catalog written")

    # Change detection from git
    previous_manifests = None
    try:
        result = subprocess.run(
            ['git', 'show', f'HEAD:{catalogs_path / "integration-manifest.json"}'],
            capture_output=True, text=True, cwd=Path.cwd()
        )
        if result.returncode == 0:
            previous_manifests = json.loads(result.stdout)
    except Exception:
        pass

    # GitHub Actions summary
    summary = generate_github_summary(all_manifests, previous_manifests, wf_catalog)
    write_github_summary(summary, generated_path / 'GITHUB_SUMMARY.md')

    # Print summary
    print(f'\n=== Catalog Generation Complete ===')
    print(f"\nTotal Vendors: {len(all_manifests)}")
    print(f"Total Analyzers: {sum(m['stats']['totalAnalyzers'] for m in all_manifests.values())}")
    print(f"Total Responders: {sum(m['stats']['totalResponders'] for m in all_manifests.values())}")
    print(f"Total Functions: {sum(m['stats']['totalFunctions'] for m in all_manifests.values())}")
    print(f"Total External Integrations: {ext_catalog['totalIntegrations']}")
    print(f"Total Notifiers: {sum(m['stats'].get('totalNotifiers', 0) for m in all_manifests.values())}")
    print(f"Total Workflows: {wf_catalog['unique_count']}")
    print(f"Total Integrations: {summary['total_integrations']}")


if __name__ == '__main__':
    try:
        import yaml
    except ImportError:
        print("PyYAML not found. Please run: pip install pyyaml")
        exit(1)

    main()
