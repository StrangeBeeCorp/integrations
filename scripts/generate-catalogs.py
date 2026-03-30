#!/usr/bin/env python3
"""Generate integration catalogs (JSON/YAML only).

For documentation generation, see generate-docs.py.
"""

import json
import shutil
import subprocess
import yaml
from pathlib import Path
from typing import Dict

from manifest_utils import (
    CURRENT_BRANCH, BASE_URL,
    find_vendors, generate_vendor_manifest, parse_function_metadata
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
            'visibility': vendor.get('visibility', 'low'),
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
                'total': old_stats.get('total', 0),
            },
        }

    return light


def generate_visibility_sorted_catalog(all_manifests: Dict) -> Dict:
    """Catalog sorted by visibility tiers, then alphabetically."""
    catalog = {'high': [], 'medium': [], 'low': []}

    for manifest in all_manifests.values():
        tier = manifest.get('visibility', 'low')
        if tier not in catalog:
            tier = 'low'
        catalog[tier].append(manifest)

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


def generate_github_summary(all_manifests: Dict, previous_manifests: Dict = None) -> Dict:
    summary = {
        'total_vendors': len(all_manifests),
        'total_analyzers': sum(m['stats']['totalAnalyzers'] for m in all_manifests.values()),
        'total_responders': sum(m['stats']['totalResponders'] for m in all_manifests.values()),
        'total_functions': sum(m['stats']['totalFunctions'] for m in all_manifests.values()),
        'total_external_integrations': sum(m['stats'].get('totalExternalIntegrations', 0) for m in all_manifests.values()),
        'total_notifiers': sum(m['stats'].get('totalNotifiers', 0) for m in all_manifests.values()),
        'total_integrations': sum(m['stats']['total'] for m in all_manifests.values()),
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
            print(f"    Skipping {vendor}: no content (0 analyzers, responders, functions, or external integrations)")
            continue
        all_manifests[vendor] = manifest

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

    # Functions catalog
    func_catalog = generate_functions_catalog_data(all_manifests)
    func_path = catalogs_path / 'functions'
    func_path.mkdir(exist_ok=True)
    _write_json(func_path / 'catalog.json', func_catalog)
    _write_yaml(func_path / 'catalog.yml', func_catalog, ["AUTO-GENERATED - DO NOT EDIT"])
    print(f"> Functions catalog written")

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
    summary = generate_github_summary(all_manifests, previous_manifests)
    write_github_summary(summary, generated_path / 'GITHUB_SUMMARY.md')

    # Print summary
    print(f'\n=== Catalog Generation Complete ===')
    print(f"\nTotal Vendors: {len(all_manifests)}")
    print(f"Total Analyzers: {sum(m['stats']['totalAnalyzers'] for m in all_manifests.values())}")
    print(f"Total Responders: {sum(m['stats']['totalResponders'] for m in all_manifests.values())}")
    print(f"Total Functions: {sum(m['stats']['totalFunctions'] for m in all_manifests.values())}")
    print(f"Total External Integrations: {ext_catalog['totalIntegrations']}")
    print(f"Total Notifiers: {sum(m['stats'].get('totalNotifiers', 0) for m in all_manifests.values())}")
    print(f"Total Integrations: {sum(m['stats']['total'] for m in all_manifests.values())}")


if __name__ == '__main__':
    try:
        import yaml
    except ImportError:
        print("PyYAML not found. Please run: pip install pyyaml")
        exit(1)

    main()
