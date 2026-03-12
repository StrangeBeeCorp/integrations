#!/usr/bin/env python3
"""Shared utilities for integration manifest generation."""

import json
import re
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Optional


def get_current_branch() -> str:
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip() or 'main'
    except Exception:
        return 'main'


GITHUB_ORG = "StrangeBeeCorp"
GITHUB_REPO = "integrations"

CURRENT_BRANCH = get_current_branch()
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_ORG}/{GITHUB_REPO}/refs/heads/{CURRENT_BRANCH}"
GITHUB_BASE_URL = f"https://github.com/{GITHUB_ORG}/{GITHUB_REPO}/blob/{CURRENT_BRANCH}"
UPSTREAM_CORTEX_URL = "https://github.com/TheHive-Project/Cortex-Analyzers/blob/master"


def _clean_path(relative_path: str) -> str:
    return relative_path[2:] if relative_path.startswith('./') else relative_path


def build_url(relative_path: str) -> str:
    return f"{BASE_URL}/{_clean_path(relative_path)}"


def build_github_url(relative_path: str) -> str:
    return f"{GITHUB_BASE_URL}/{_clean_path(relative_path)}"


def build_upstream_url(relative_path: str) -> str:
    if '.upstream/cortex/' in relative_path:
        upstream_path = relative_path.split('.upstream/cortex/')[1]
        return f"{UPSTREAM_CORTEX_URL}/{upstream_path}"
    return relative_path


def parse_markdown_frontmatter(file_path: str) -> Optional[Dict]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None
        return yaml.safe_load(match.group(1))
    except Exception as e:
        print(f"  Warning: Error parsing front matter from {file_path}: {e}")
        return None


def parse_function_metadata(file_path: str) -> Optional[Dict]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'/\*---\n(.*?)\n---\*/', content, re.DOTALL)
        if not match:
            return None
        metadata = yaml.safe_load(match.group(1))
        return metadata.get('thehive') if metadata else None
    except Exception as e:
        print(f"Error parsing metadata from {file_path}: {e}")
        return None


def _scan_cortex_items(vendor: str, item_type: str) -> tuple[List[Dict], Dict]:
    """Scan analyzers or responders for a vendor. item_type is 'analyzers' or 'responders'."""
    items_path = Path('.upstream') / 'cortex' / item_type / vendor
    if not items_path.exists():
        return [], {}

    items = []
    subscription_fields = {
        'registration_required': [],
        'subscription_required': [],
        'free_subscription': []
    }

    for file_path in items_path.glob('*.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)

            relative_path = f".upstream/cortex/{item_type}/{vendor}/{file_path.name}"

            items.append({
                'name': content.get('name', '').replace('_', ' '),
                'version': content.get('version'),
                'author': content.get('author'),
                'license': content.get('license'),
                'description': content.get('description'),
                'dataTypes': content.get('dataTypeList', []),
                'file': relative_path,
                'url': build_url(relative_path),
                'github_url': build_github_url(relative_path),
                'upstream_url': f"{UPSTREAM_CORTEX_URL}/{item_type}/{vendor}",
                'integration_type': content.get('integration_type')
            })

            for field in subscription_fields:
                if field in content:
                    subscription_fields[field].append(content[field])

        except Exception as e:
            print(f"Error reading {item_type[:-1]} {file_path}: {e}")

    return items, subscription_fields


def scan_analyzers(vendor: str) -> tuple[List[Dict], Dict]:
    return _scan_cortex_items(vendor, 'analyzers')


def scan_responders(vendor: str) -> tuple[List[Dict], Dict]:
    return _scan_cortex_items(vendor, 'responders')


def consolidate_subscription_fields(analyzer_fields: Dict, responder_fields: Dict) -> Dict:
    result = {}
    for key in ('registration_required', 'subscription_required', 'free_subscription'):
        values = analyzer_fields.get(key, []) + responder_fields.get(key, [])
        if not values:
            continue
        unique = list(set(values))
        result[key] = unique[0] if len(unique) == 1 else sorted(unique, key=lambda x: (not x, x))
    return result


def scan_functions(vendor: str) -> List[Dict]:
    functions_path = Path('integrations') / 'vendors' / vendor / 'thehive' / 'functions'
    if not functions_path.exists():
        return []

    functions = []
    for file_path in functions_path.glob('*.js'):
        metadata = parse_function_metadata(str(file_path))
        if not metadata:
            continue

        relative_path = f"integrations/vendors/{vendor}/thehive/functions/{file_path.name}"
        functions.append({
            'name': metadata.get('name'),
            'version': metadata.get('version'),
            'description': metadata.get('description'),
            'kind': metadata.get('kind'),
            'mode': metadata.get('mode'),
            'file': relative_path,
            'url': build_url(relative_path),
            'github_url': build_github_url(relative_path)
        })

    return functions


def discover_use_cases_from_markdown(vendor: str) -> List[Dict]:
    vendor_path = Path('integrations') / 'vendors' / vendor
    if not vendor_path.exists():
        return []

    use_cases = []
    md_files = list(vendor_path.glob('*.md')) + list(vendor_path.glob('use-cases/*.md'))
    skip_files = {'manifest.md', 'vendor.md', 'README.md'}

    for md_file in md_files:
        if md_file.name in skip_files:
            continue

        frontmatter = parse_markdown_frontmatter(str(md_file))
        if not frontmatter:
            continue

        title = frontmatter.get('title')
        description = frontmatter.get('description')
        if not title or not description:
            continue

        if md_file.parent.name == 'use-cases':
            relative_doc_path = f"integrations/vendors/{vendor}/use-cases/{md_file.name}"
        else:
            relative_doc_path = f"integrations/vendors/{vendor}/{md_file.name}"

        use_case = {
            'name': title,
            'description': description,
            'documentation': {
                'file': relative_doc_path,
                'url': build_url(relative_doc_path),
                'github_url': build_github_url(relative_doc_path)
            }
        }

        for field in ('tags', 'difficulty', 'thehive_version_required', 'license_required', 'linked_to'):
            if field in frontmatter:
                use_case[field] = frontmatter[field]

        use_cases.append(use_case)

    return use_cases


def auto_detect_logo(vendor: str) -> Dict:
    """Detect logo file from vendor assets. Priority: SVG > PNG > JPG > JPEG > ICO."""
    assets_dir = Path('integrations') / 'vendors' / vendor / 'assets'
    if not assets_dir.exists():
        return {}

    extensions = ['.svg', '.png', '.jpg', '.jpeg', '.ico']
    patterns = ['logo', 'icon', vendor.lower()]

    for pattern in patterns:
        for ext in extensions:
            logo_file = assets_dir / f"{pattern}{ext}"
            if logo_file.exists():
                relative_path = f"integrations/vendors/{vendor}/assets/{pattern}{ext}"
                return {
                    'file': relative_path,
                    'url': build_url(relative_path),
                    'github_url': build_github_url(relative_path)
                }

    return {}


def read_vendor_metadata(vendor: str) -> Dict:
    vendor_yml_path = Path('integrations') / 'vendors' / vendor / 'vendor.yml'
    default_name = vendor.replace('_', ' ')

    default_metadata = {
        'id': vendor, 'name': default_name, 'description': '', 'category': '',
        'tags': [], 'homepage': '', 'logo': {}, 'useCases': [],
        'externalIntegrations': [], 'displayOnWebsite': True, 'visibility': 100
    }

    if not vendor_yml_path.exists():
        print(f"  Warning: vendor.yml not found for {vendor}, using defaults")
        return default_metadata

    try:
        with open(vendor_yml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data:
            return default_metadata

        tags = data.get('tags', [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',')]

        return {
            'id': data.get('id', vendor),
            'name': data.get('name', default_name),
            'description': data.get('description', ''),
            'category': data.get('category', ''),
            'tags': tags,
            'homepage': data.get('homepage', ''),
            'logo': auto_detect_logo(vendor),
            'useCases': discover_use_cases_from_markdown(vendor),
            'externalIntegrations': data.get('externalIntegrations', []),
            'displayOnWebsite': data.get('displayOnWebsite', True),
            'visibility': data.get('visibility', 'low')
        }
    except Exception as e:
        print(f"  Error reading vendor.yml for {vendor}: {e}")
        return default_metadata


def find_vendors() -> List[str]:
    vendors = set()

    for subdir in ('analyzers', 'responders'):
        path = Path('.upstream') / 'cortex' / subdir
        if path.exists():
            vendors.update(d.name for d in path.iterdir() if d.is_dir())

    vendors_path = Path('integrations') / 'vendors'
    if vendors_path.exists():
        vendors.update(d.name for d in vendors_path.iterdir() if d.is_dir() and not d.name.startswith('.'))

    return sorted(vendors, key=str.lower)


def generate_vendor_manifest(vendor: str) -> Dict:
    vendor_metadata = read_vendor_metadata(vendor)
    analyzers, analyzer_sub = scan_analyzers(vendor)
    responders, responder_sub = scan_responders(vendor)
    functions = scan_functions(vendor)

    subscription_info = consolidate_subscription_fields(analyzer_sub, responder_sub)
    external_count = len(vendor_metadata.get('externalIntegrations', []))
    use_cases_count = len(vendor_metadata.get('useCases', []))

    return {
        **vendor_metadata,
        **subscription_info,
        'integrations': {
            'analyzers': analyzers,
            'responders': responders,
            'functions': functions
        },
        'stats': {
            'totalAnalyzers': len(analyzers),
            'totalResponders': len(responders),
            'totalFunctions': len(functions),
            'totalUseCases': use_cases_count,
            'totalExternalIntegrations': external_count,
            'total': len(analyzers) + len(responders) + len(functions) + external_count
        }
    }
