#!/usr/bin/env python3
"""Generate integration documentation (Markdown only).

For catalog generation, see generate-catalogs.py.
"""

import json
import re
import shutil
from pathlib import Path
from typing import Dict, List

from manifest_utils import (
    CURRENT_BRANCH, BASE_URL,
    find_vendors, generate_vendor_manifest, parse_function_metadata
)


def _render_cortex_items(items: list, item_type: str) -> List[str]:
    """Render a list of analyzers or responders to markdown lines."""
    lines = [f"## {item_type} ({len(items)})", ""]

    for item in items:
        name = item.get('name', 'Unknown')
        version = item.get('version', '')
        if item.get('upstream_url'):
            lines.append(f"### [{name} v{version}]({item['upstream_url']})")
        else:
            lines.append(f"### {name} v{version}")

        if item.get('description'):
            lines.extend([item['description'], ""])

        if item.get('author'):
            lines.append(f"- **Author:** {item['author']}")
        if item.get('license'):
            lines.append(f"- **License:** {item['license']}")
        if item.get('dataTypes'):
            lines.append(f"- **Data Types:** {', '.join(f'`{dt}`' for dt in item['dataTypes'])}")
        lines.append("")

    return lines


def generate_markdown_overview(vendor: str, manifest: Dict) -> str:
    lines = []

    # Determine which sections have content (for smart dividers)
    use_cases = manifest.get('useCases', [])
    analyzers = manifest.get('integrations', {}).get('analyzers', [])
    responders = manifest.get('integrations', {}).get('responders', [])
    functions = manifest.get('integrations', {}).get('functions', [])
    external_integrations = manifest.get('externalIntegrations', [])

    sections = []
    if use_cases: sections.append('use_cases')
    if analyzers: sections.append('analyzers')
    if responders: sections.append('responders')
    if functions: sections.append('functions')
    if external_integrations: sections.append('external')

    def _add_divider_if_more(section_name):
        idx = sections.index(section_name) if section_name in sections else -1
        if idx >= 0 and idx < len(sections) - 1:
            lines.extend(["---", ""])

    # Use Cases
    if use_cases:
        lines.extend([f"## Use Cases ({len(use_cases)})", ""])
        function_lookup = {f.get('file', ''): f for f in functions}

        for i, uc in enumerate(use_cases):
            github_url = uc.get('documentation', {}).get('github_url')
            if github_url:
                lines.append(f"### [{uc['name']}]({github_url})")
            else:
                lines.append(f"### {uc['name']}")
            if uc.get('description'):
                lines.append(uc['description'])
            lines.append("")

            if uc.get('license_required'):
                lines.append(f"- **License required:** {uc['license_required'].capitalize()}")
            if uc.get('thehive_version_required'):
                lines.append(f"- **TheHive version required:** {uc['thehive_version_required']}+")

            for linked_path in uc.get('linked_to', []):
                func = function_lookup.get(linked_path)
                if func:
                    lines.append(f"- **Related function:** [{func.get('name', 'Unknown')}]({func.get('github_url', '#')})")
                else:
                    lines.append(f"- **Related:** `{linked_path}`")

            lines.append("")
            if i < len(use_cases) - 1:
                lines.extend(["---", ""])

        _add_divider_if_more('use_cases')

    # Analyzers & Responders
    if analyzers:
        lines.extend(_render_cortex_items(analyzers, "Analyzers"))
        _add_divider_if_more('analyzers')

    if responders:
        lines.extend(_render_cortex_items(responders, "Responders"))
        _add_divider_if_more('responders')

    # Functions
    if functions:
        lines.extend([f"## Functions ({len(functions)})", ""])
        for func in functions:
            name = func.get('name', 'Unknown')
            version = func.get('version', '')
            github_url = func.get('github_url')
            if github_url:
                lines.append(f"### [{name}]({github_url}) `v{version}`")
            else:
                lines.append(f"### {name} `v{version}`")
            if func.get('description'):
                lines.extend([func['description'], ""])
            if func.get('author'):
                lines.append(f"- **Author:** {func['author']}")
            lines.append("")

        _add_divider_if_more('functions')

    # External Integrations
    if external_integrations:
        lines.extend([f"## External Integrations ({len(external_integrations)})", "",
                       f"External integrations that connect {manifest['name']} with TheHive:", ""])

        for i, vi in enumerate(external_integrations):
            lines.append(f"### {vi['name']}")
            if vi.get('description'):
                lines.append(vi['description'])
            lines.append("")
            if vi.get('type'):
                lines.append(f"- **Type:** {vi['type']}")
            if vi.get('documentation'):
                lines.append(f"- **Documentation:** [{vi['documentation']}]({vi['documentation']})")
            lines.append("")
            if i < len(external_integrations) - 1:
                lines.extend(["---", ""])

    return '\n'.join(lines)


def generate_catalog_index(all_manifests: Dict) -> str:
    lines = [
        "# Integration Catalog", "",
        "Auto-generated catalog of TheHive and Cortex integrations.", "",
        "## About This Catalog", "",
        "This catalog contains integrations built by StrangeBee and the community to help you "
        "integrate TheHive with your existing tools. Use them directly or as inspiration for your own.", "",
        "**Don't see what you need?** You can build your own:", "",
        "- **Analyzers** - enrich observables with external data",
        "- **Responders** - automate actions on external systems",
        "- **Functions** - custom workflow logic",
        "- **Custom tools** - whatever your setup requires", "",
        "Built something useful? Contributions are welcome!", "",
    ]

    # Summary stats
    stats_totals = {k: sum(m['stats'][k] for m in all_manifests.values())
                    for k in ('totalAnalyzers', 'totalResponders', 'totalFunctions', 'total')}
    stats_totals['totalExternalIntegrations'] = sum(
        m['stats'].get('totalExternalIntegrations', 0) for m in all_manifests.values())

    lines.extend([
        "## Summary Statistics", "",
        f"- **Total Vendors:** {len(all_manifests)}",
        f"- **Total Analyzers:** {stats_totals['totalAnalyzers']}",
        f"- **Total Responders:** {stats_totals['totalResponders']}",
        f"- **Total Functions:** {stats_totals['totalFunctions']}",
        f"- **Total External Integrations:** {stats_totals['totalExternalIntegrations']}",
        f"- **Total Integrations:** {stats_totals['total']}", "",
    ])

    # Group by category
    by_category = {}
    for vendor_id, manifest in all_manifests.items():
        category = manifest.get('category') or 'Uncategorized'
        by_category.setdefault(category, []).append((vendor_id, manifest))

    lines.extend(["## Vendors by Category", ""])
    for category in sorted(by_category, key=str.lower):
        lines.extend([f"### {category}", ""])
        for vendor_id, manifest in sorted(by_category[category], key=lambda x: x[1]['name'].lower()):
            desc = manifest.get('description', '')
            if len(desc) > 100:
                desc = desc[:97] + "..."
            lines.append(f"**[{manifest['name']}](vendors/{vendor_id}/overview.md)** ({manifest['stats']['total']} integrations)")
            if desc:
                lines.append(f"  {desc}")
            lines.append("")
        lines.append("")

    # All vendors A-Z
    lines.extend(["## All Vendors (A-Z)", ""])
    for vendor_id, manifest in sorted(all_manifests.items(), key=lambda x: x[1]['name'].lower()):
        stats = manifest['stats']
        category = manifest.get('category') or 'Uncategorized'
        parts = []
        if stats['totalAnalyzers'] > 0: parts.append(f"{stats['totalAnalyzers']} analyzers")
        if stats['totalResponders'] > 0: parts.append(f"{stats['totalResponders']} responders")
        if stats['totalFunctions'] > 0: parts.append(f"{stats['totalFunctions']} functions")
        if stats.get('totalExternalIntegrations', 0) > 0: parts.append(f"{stats['totalExternalIntegrations']} external")
        breakdown = ", ".join(parts) or "No integrations"
        lines.append(f"- **[{manifest['name']}](vendors/{vendor_id}/overview.md)** - *{category}* - {breakdown}")

    lines.extend(["", "---", "", "*This catalog is auto-generated. Do not edit manually.*", ""])
    return '\n'.join(lines)


def generate_external_integrations_markdown(catalog: Dict) -> str:
    lines = [
        "# External Integrations Catalog", "",
        "Community and vendor-built integrations that connect various platforms with TheHive and Cortex.", "",
        "## Overview", "",
        f"**Total External Integrations:** {catalog['totalIntegrations']}", "",
    ]

    # Browse by Type (collapsible)
    lines.extend(["## Browse by Type", ""])
    for int_type, integrations in sorted(catalog['byType'].items()):
        plural = '' if len(integrations) == 1 else 's'
        lines.extend([
            "<details>",
            f"<summary><strong>{int_type}</strong> ({len(integrations)} integration{plural})</summary>", "", "",
        ])
        for item in sorted(integrations, key=lambda x: x['name'].lower()):
            lines.append(f"**{item['name']}** - {item['vendor']}")
            if item.get('description'): lines.append(f"  {item['description']}")
            if item.get('documentation'): lines.append(f"  [Documentation]({item['documentation']})")
            lines.append("")
        lines.extend(["</details>", ""])

    # Browse by Category (collapsible)
    lines.extend(["## Browse by Vendor Category", ""])
    for category, integrations in sorted(catalog['byCategory'].items()):
        plural = '' if len(integrations) == 1 else 's'
        lines.extend([
            "<details>",
            f"<summary><strong>{category}</strong> ({len(integrations)} integration{plural})</summary>", "", "",
        ])
        for item in sorted(integrations, key=lambda x: (x['vendor'].lower(), x['name'].lower())):
            lines.append(f"**{item['name']}** - {item['vendor']}")
            if item.get('description'): lines.append(f"  {item['description']}")
            if item.get('type'): lines.append(f"  Type: `{item['type']}`")
            if item.get('documentation'): lines.append(f"  [Documentation]({item['documentation']})")
            lines.append("")
        lines.extend(["</details>", ""])

    # All by vendor (collapsible)
    lines.extend(["## All External Integrations by Vendor", ""])
    for vendor, integrations in sorted(catalog['byVendor'].items()):
        plural = '' if len(integrations) == 1 else 's'
        lines.extend([
            "<details>",
            f"<summary><strong>{vendor}</strong> ({len(integrations)} integration{plural})</summary>", "", "",
        ])
        for item in sorted(integrations, key=lambda x: x['name'].lower()):
            lines.extend([f"### {item['name']}", ""])
            if item.get('description'): lines.extend([item['description'], ""])
            metadata = []
            if item.get('type'): metadata.append(f"**Type:** `{item['type']}`")
            if item.get('category'): metadata.append(f"**Category:** {item['category']}")
            if metadata: lines.extend(["  \n".join(metadata), ""])
            if item.get('documentation'):
                lines.extend([f"**Documentation:** [{item['documentation']}]({item['documentation']})", ""])
        lines.extend(["</details>", ""])

    lines.extend(["---", "", "*This catalog is auto-generated. Do not edit manually.*", ""])
    return '\n'.join(lines)


def read_function_code(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return re.sub(r'/\*---\n.*?\n---\*/', '', content, flags=re.DOTALL).strip()
    except Exception as e:
        return f"// Error reading function code: {e}"


def generate_individual_function_page(func: Dict, vendor_name: str = None) -> str:
    lines = [f"# {func.get('name', 'Unknown')}", "", "## Metadata", "",
             f"- **Version:** `{func.get('version', 'N/A')}`"]

    if vendor_name:
        lines.append(f"- **Vendor:** {vendor_name}")
    else:
        lines.append(f"- **Type:** Generic Function")

    for key, label in [('type', 'Function Type'), ('kind', 'Kind'), ('mode', 'Mode')]:
        val = func.get(key)
        if val and val != 'N/A':
            lines.append(f"- **{label}:** `{val}`")
    if func.get('file'):
        lines.append(f"- **Source File:** `{func['file']}`")

    lines.extend(["", "## Description", "", func.get('description', 'No description available'), ""])

    code = func.get('code', '')
    if code:
        lines.extend(["## Code", "", "```javascript", code, "```", ""])

    lines.extend(["---", "", "*This documentation is auto-generated. Do not edit manually.*", ""])
    return '\n'.join(lines)


def generate_functions_catalog(all_manifests: Dict) -> str:
    lines = [
        "# Functions Catalog", "",
        "Example functions for TheHive. Use them as-is or as inspiration for your own.", "",
        "**Create your own:** [Functions](https://docs.strangebee.com/thehive/user-guides/organization/configure-organization/manage-functions/create-a-function/) - "
        "[Feeders](https://docs.strangebee.com/thehive/user-guides/organization/configure-organization/manage-feeders/create-a-feeder/)", "",
    ]

    # Collect generic functions
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
                    'code': read_function_code(str(func_file))
                })

    # Collect vendor functions
    vendor_functions = {}
    total = len(generic_functions)
    for vendor_id, manifest in all_manifests.items():
        funcs = manifest.get('integrations', {}).get('functions', [])
        if funcs:
            vendor_functions[manifest.get('name', vendor_id)] = {'vendor_id': vendor_id, 'functions': funcs}
            total += len(funcs)

    lines.extend([
        "## Summary", "",
        f"- **Total Functions:** {total}",
        f"- **Generic Functions:** {len(generic_functions)}",
        f"- **Vendor-Specific Functions:** {total - len(generic_functions)}",
        f"- **Vendors with Functions:** {len(vendor_functions)}", "",
    ])

    if generic_functions:
        lines.extend(["## Generic Functions", "",
                       "These functions are vendor-agnostic and can be used across all TheHive installations:", ""])
        for func in sorted(generic_functions, key=lambda x: x.get('name', '').lower()):
            safe_name = func['name'].replace(' ', '-').replace('/', '-').lower()
            lines.append(f"### [{func['name']}]({safe_name}.md) `v{func.get('version', 'N/A')}`")
            lines.append("")
            for key, label in [('type', 'Type'), ('mode', 'Mode')]:
                val = func.get(key)
                if val and val != 'N/A':
                    lines.append(f"**{label}:** {val}")
            lines.extend(["", func.get('description', ''), "",
                          f"[View full documentation]({safe_name}.md)", "", "---", ""])

    if vendor_functions:
        lines.extend(["## Vendor-Specific Functions", ""])
        for vname in sorted(vendor_functions):
            vdata = vendor_functions[vname]
            lines.extend([f"### {vname}", "",
                          f"**Vendor:** [{vname}](../vendors/{vdata['vendor_id']}/overview)", ""])
            for func in sorted(vdata['functions'], key=lambda x: x.get('name', '').lower()):
                safe_name = f"{vname.lower().replace(' ', '-')}-{func['name'].replace(' ', '-').replace('/', '-').lower()}"
                lines.append(f"#### [{func['name']}]({safe_name}.md) `v{func.get('version', 'N/A')}`")
                if func.get('kind'):
                    lines.append(f"**Kind:** `{func['kind']}`")
                lines.extend(["", func.get('description', 'No description available'), "",
                              f"[View full documentation]({safe_name}.md)", ""])
            lines.extend(["---", ""])

    lines.extend(["---", "", "*This catalog is auto-generated. Do not edit manually.*", ""])
    return '\n'.join(lines)


def get_status_badge(status: str) -> str:
    badges = {
        'tested': '![Tested](https://img.shields.io/badge/Status-Tested-brightgreen)',
        'untested': '![Untested](https://img.shields.io/badge/Status-Untested-lightgrey)',
        'not_working': '![Not Working](https://img.shields.io/badge/Status-Not_Working-red)',
        'tested_with_issues': '![Tested with Issues](https://img.shields.io/badge/Status-Tested%20with%20Issues-blue)'
    }
    return badges.get(status, '![Unknown](https://img.shields.io/badge/Status-Unknown-lightgrey)')


def collect_notifications() -> Dict:
    notifications = {'generic': [], 'vendors': {}}

    generic_path = Path('integrations/generic/thehive/notifications')
    if generic_path.exists():
        for nf in generic_path.glob('*.json'):
            try:
                with open(nf, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_file'] = str(nf)
                    notifications['generic'].append(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"  Warning: Could not read {nf}: {e}")

    vendors_path = Path('integrations/vendors')
    if vendors_path.exists():
        for vendor_dir in vendors_path.iterdir():
            if not vendor_dir.is_dir():
                continue
            notif_path = vendor_dir / 'thehive' / 'notifications'
            if not notif_path.exists():
                continue
            vendor_notifs = []
            for nf in notif_path.glob('*.json'):
                try:
                    with open(nf, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data['_file'] = str(nf)
                        vendor_notifs.append(data)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"  Warning: Could not read {nf}: {e}")
            if vendor_notifs:
                notifications['vendors'][vendor_dir.name] = vendor_notifs

    return notifications


def _render_notification(notif: Dict, heading_level: str = "###") -> List[str]:
    lines = [f"{heading_level} {notif.get('name', 'Unknown')}", "",
             get_status_badge(notif.get('status', 'untested')), ""]

    if notif.get('description'):
        lines.extend([notif['description'], ""])
    if notif.get('contributor'):
        lines.extend([f"**Contributor:** {notif['contributor']}", ""])

    comment = notif.get('comment', '')
    status = notif.get('status', 'untested')
    if comment:
        prefix = {'not_working': 'Issue', 'tested_with_issues': 'Warning'}.get(status, 'Note')
        lines.extend([f"> **{prefix}:** {comment}", ""])

    filter_data = notif.get('filter')
    if filter_data:
        lines.extend(["```json", json.dumps(filter_data, indent=4), "```"])
    else:
        lines.append("*No filter available - this functionality is not supported by TheHive.*")

    lines.extend(["", "---", ""])
    return lines


def generate_notifications_documentation(notifications: Dict) -> str:
    status_order = {'tested': 0, 'untested': 1, 'tested_with_issues': 2, 'not_working': 3}
    sort_key = lambda x: (status_order.get(x.get('status', 'untested'), 99), x.get('name', '').lower())

    total_generic = len(notifications['generic'])
    total_vendor = sum(len(v) for v in notifications['vendors'].values())
    tested = sum(1 for n in notifications['generic'] if n.get('status') == 'tested')
    tested += sum(1 for vn in notifications['vendors'].values() for n in vn if n.get('status') == 'tested')

    lines = [
        "# TheHive Notification Filters", "",
        "Ready-to-use notification filters for TheHive.", "",
        "## Summary", "",
        f"- **Total Notifications:** {total_generic + total_vendor}",
        f"- **Generic Notifications:** {total_generic}",
        f"- **Vendor-Specific Notifications:** {total_vendor}",
        f"- **Tested:** {tested}", "",
    ]

    if notifications['generic']:
        lines.extend(["## Generic Notifications", ""])
        for notif in sorted(notifications['generic'], key=sort_key):
            lines.extend(_render_notification(notif, "###"))

    if notifications['vendors']:
        lines.extend(["## Vendor-Specific Notifications", ""])
        for vendor_name in sorted(notifications['vendors']):
            vendor_notifs = notifications['vendors'][vendor_name]
            if not vendor_notifs:
                continue
            lines.extend([f"### {vendor_name}", ""])
            for notif in sorted(vendor_notifs, key=sort_key):
                lines.extend(_render_notification(notif, "####"))

    lines.extend(["*This documentation is auto-generated. Do not edit manually.*", ""])
    return '\n'.join(lines)


def generate_free_local_integrations(all_manifests: Dict) -> str:
    lines = [
        "# Free & Local Integrations", "",
        "Integrations that are either free to use or run locally without external dependencies.", "",
    ]

    collected = {'analyzers': [], 'responders': []}

    for vendor_id, manifest in all_manifests.items():
        vendor_name = manifest.get('name', vendor_id)
        free_sub = manifest.get('free_subscription', False)

        for item_type in ('analyzers', 'responders'):
            for item in manifest.get('integrations', {}).get(item_type, []):
                is_local = item.get('integration_type') == 'local'
                if free_sub or is_local:
                    collected[item_type].append({
                        'vendor': vendor_name, 'vendor_id': vendor_id,
                        'free_subscription': free_sub, 'is_local': is_local,
                        **item
                    })

    local_analyzers = [a for a in collected['analyzers'] if a['is_local']]
    free_analyzers = [a for a in collected['analyzers'] if not a['is_local'] and a['free_subscription']]
    local_responders = [r for r in collected['responders'] if r['is_local']]
    free_responders = [r for r in collected['responders'] if not r['is_local'] and r['free_subscription']]

    lines.extend([
        "## Summary", "",
        f"- **Total Analyzers:** {len(collected['analyzers'])} ({len(local_analyzers)} local, {len(free_analyzers)} free)",
        f"- **Total Responders:** {len(collected['responders'])} ({len(local_responders)} local, {len(free_responders)} free)",
        f"- **Total Integrations:** {len(collected['analyzers']) + len(collected['responders'])}", "",
    ])

    def _render_section(items: list, label_tag: str, section_title: str):
        if not items:
            return
        lines.extend([f"### {section_title}", ""])
        for item in sorted(items, key=lambda x: (x['vendor'].lower(), x.get('name', '').lower())):
            lines.extend([
                "<details>",
                f"<summary><strong>{item.get('name', 'Unknown')}</strong> <code>v{item.get('version', 'N/A')}</code> [{label_tag}] - {item['vendor']}</summary>", "",
                f"**Vendor:** [{item['vendor']}](vendors/{item['vendor_id']}/overview)",
            ])
            if item.get('dataTypes'):
                lines.append(f"**Data Types:** {', '.join(f'`{dt}`' for dt in item['dataTypes'])}")
            lines.extend(["", item.get('description', 'No description available'), "", "</details>", ""])

    if local_analyzers or free_analyzers:
        lines.extend(["## Analyzers", ""])
        _render_section(local_analyzers, "Local", "Local Analyzers")
        _render_section(free_analyzers, "Free", "Free Subscription Analyzers")

    if local_responders or free_responders:
        lines.extend(["## Responders", ""])
        _render_section(local_responders, "Local", "Local Responders")
        _render_section(free_responders, "Free", "Free Subscription Responders")

    lines.extend(["---", "", "*This catalog is auto-generated. Do not edit manually.*", ""])
    return '\n'.join(lines)


def main():
    print(f"=== Documentation Generation ===")
    print(f"Using branch: {CURRENT_BRANCH}")
    print(f"Using base URL: {BASE_URL}\n")

    generated_path = Path('.generated')
    catalogs_path = generated_path / 'catalogs'

    manifest_path = catalogs_path / 'integration-manifest.json'
    if not manifest_path.exists():
        print("Error: integration-manifest.json not found! Run generate-catalogs.py first.")
        exit(1)

    with open(manifest_path, 'r', encoding='utf-8') as f:
        all_manifests = json.load(f)

    vendors = list(all_manifests.keys())
    print(f"Loaded manifests for {len(vendors)} vendors\n")

    docs_path = generated_path / 'docs'
    docs_path.mkdir(exist_ok=True)

    # Clean obsolete vendor docs
    vendors_docs_path = docs_path / 'vendors'
    if vendors_docs_path.exists():
        for d in vendors_docs_path.iterdir():
            if d.is_dir() and d.name not in vendors:
                print(f"Cleaning up obsolete docs: {d.name}")
                shutil.rmtree(d)

    # Generate per-vendor docs
    print(f"Generating documentation for {len(vendors)} vendors...")
    for vendor in vendors:
        print(f"  Processing {vendor}...")
        vendor_docs = docs_path / 'vendors' / vendor
        vendor_docs.mkdir(parents=True, exist_ok=True)
        with open(vendor_docs / 'overview.md', 'w', encoding='utf-8') as f:
            f.write(generate_markdown_overview(vendor, all_manifests[vendor]))
    print(f"> Generated {len(vendors)} vendor documentation pages")

    # Catalog index
    with open(docs_path / 'overview.md', 'w', encoding='utf-8') as f:
        f.write(generate_catalog_index(all_manifests))
    print(f"> Catalog index written")

    # External integrations docs
    ext_catalog_path = catalogs_path / 'external-integrations' / 'catalog.json'
    if ext_catalog_path.exists():
        with open(ext_catalog_path, 'r', encoding='utf-8') as f:
            ext_catalog = json.load(f)
        ext_docs = docs_path / 'external-integrations'
        ext_docs.mkdir(exist_ok=True)
        with open(ext_docs / 'overview.md', 'w', encoding='utf-8') as f:
            f.write(generate_external_integrations_markdown(ext_catalog))
        print(f"> External integrations docs written")

    # Functions docs
    functions_dir = docs_path / 'functions'
    functions_dir.mkdir(exist_ok=True)
    with open(functions_dir / 'overview.md', 'w', encoding='utf-8') as f:
        f.write(generate_functions_catalog(all_manifests))
    print(f"> Functions overview written")

    # Individual function pages
    function_count = 0
    generic_path = Path('integrations/generic/functions')
    if generic_path.exists():
        for func_file in generic_path.glob('function_*.js'):
            metadata = parse_function_metadata(str(func_file))
            if metadata:
                func_data = {
                    'name': metadata.get('name', func_file.stem),
                    'version': metadata.get('version', 'N/A'),
                    'description': metadata.get('description', 'No description available'),
                    'type': metadata.get('type', 'function'),
                    'kind': metadata.get('kind', 'function'),
                    'mode': metadata.get('mode', 'N/A'),
                    'file': str(func_file),
                    'code': read_function_code(str(func_file))
                }
                safe_name = func_data['name'].replace(' ', '-').replace('/', '-').lower()
                with open(functions_dir / f"{safe_name}.md", 'w', encoding='utf-8') as f:
                    f.write(generate_individual_function_page(func_data))
                function_count += 1

    for vendor_id, manifest in all_manifests.items():
        vendor_name = manifest.get('name', vendor_id)
        for func in manifest.get('integrations', {}).get('functions', []):
            func_file_path = func.get('file', '')
            func['code'] = read_function_code(func_file_path) if func_file_path and Path(func_file_path).exists() else ''
            safe_name = f"{vendor_name.lower().replace(' ', '-')}-{func['name'].replace(' ', '-').replace('/', '-').lower()}"
            with open(functions_dir / f"{safe_name}.md", 'w', encoding='utf-8') as f:
                f.write(generate_individual_function_page(func, vendor_name))
            function_count += 1

    print(f"> Generated {function_count} individual function pages")

    # Free/local integrations
    with open(docs_path / 'free-local.md', 'w', encoding='utf-8') as f:
        f.write(generate_free_local_integrations(all_manifests))
    print(f"> Free/local integrations docs written")

    # Notifications
    notifications = collect_notifications()
    total_notifs = len(notifications['generic']) + sum(len(v) for v in notifications['vendors'].values())
    if total_notifs > 0:
        with open(docs_path / 'notifications.md', 'w', encoding='utf-8') as f:
            f.write(generate_notifications_documentation(notifications))
        print(f"> Notifications docs written ({total_notifs} filters)")

    print('\n=== Documentation Generation Complete ===')


if __name__ == '__main__':
    main()
