#!/usr/bin/env python3
"""Shared utilities for integration manifest generation."""

import json
import os
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


def get_github_repo() -> tuple:
    """Resolve the GitHub owner/repo the generated URLs should point to.

    Uses GITHUB_REPOSITORY in CI (so forks generate URLs to themselves),
    then the origin remote locally, then the canonical repository.
    """
    env_repo = os.environ.get('GITHUB_REPOSITORY', '')
    if '/' in env_repo:
        owner, repo = env_repo.split('/', 1)
        return owner, repo
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True, text=True, check=True
        )
        match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$', result.stdout.strip())
        if match:
            owner, repo = match.group(1), match.group(2)
            if (owner.lower(), repo.lower()) == ('strangebeecorp', 'integrations'):
                return 'StrangeBeeCorp', 'integrations'
            return owner, repo
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return 'StrangeBeeCorp', 'integrations'


GITHUB_ORG, GITHUB_REPO = get_github_repo()

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
        # Always emit a boolean: true if any analyzer/responder config says so
        result[key] = any(bool(v) for v in values)
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
            'author': metadata.get('author'),
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

        for field in ('author', 'tags', 'difficulty', 'thehive_version_required', 'license_required', 'linked_to'):
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
        'notifier': False, 'flow': {}, 'workflows': [], 'externalIntegrations': [],
        'displayOnWebsite': True, 'visibility': 100, 'analyzersTagline': '', 'analyzerDisplayName': ''
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
            'notifier': data.get('notifier', False),
            'flow': data.get('flow') or {},
            'workflows': data.get('workflows') or [],
            'externalIntegrations': data.get('externalIntegrations', []),
            'displayOnWebsite': data.get('displayOnWebsite', True),
            'visibility': data.get('visibility', 100),
            'analyzersTagline': data.get('analyzersTagline', ''),
            'analyzerDisplayName': data.get('analyzerDisplayName', '')
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


def _rebrand_item_names(items: List[Dict], vendor: str, display_name: str) -> None:
    if not display_name:
        return
    for item in items:
        name = item.get('name', '')
        if name.lower().startswith(vendor.lower()):
            item['name'] = display_name + name[len(vendor):]


def _link_workflow_files(vendor: str, workflows: List[Dict]) -> List[Dict]:
    """Add the export file links to each declared workflow whose thehive/workflows/<slug>.yml exists."""
    root = Path('integrations') / 'vendors' / vendor / 'thehive' / 'workflows'
    files = {}
    if root.exists():
        for file_path in sorted(list(root.glob('*.yml')) + list(root.glob('*.yaml'))):
            if not file_path.name.startswith('_'):
                files.setdefault(file_path.stem.lower(), file_path.name)

    linked = []
    for workflow in workflows or []:
        if not isinstance(workflow, dict):
            continue
        workflow = dict(workflow)
        file_name = files.get(workflow_slug(workflow))
        if file_name:
            relative_path = f"integrations/vendors/{vendor}/thehive/workflows/{file_name}"
            workflow['file'] = relative_path
            workflow['file_url'] = build_url(relative_path)
            workflow['github_url'] = build_github_url(relative_path)
        linked.append(workflow)
    return linked


def generate_vendor_manifest(vendor: str) -> Dict:
    vendor_metadata = read_vendor_metadata(vendor)
    analyzers, analyzer_sub = scan_analyzers(vendor)
    responders, responder_sub = scan_responders(vendor)
    functions = scan_functions(vendor)

    display_name = vendor_metadata.get('analyzerDisplayName', '')
    _rebrand_item_names(analyzers, vendor, display_name)
    _rebrand_item_names(responders, vendor, display_name)

    subscription_info = consolidate_subscription_fields(analyzer_sub, responder_sub)
    external_count = len(vendor_metadata.get('externalIntegrations', []))
    use_cases_count = len(vendor_metadata.get('useCases', []))
    is_notifier = vendor_metadata.get('notifier', False)
    notifier_count = 1 if is_notifier else 0
    flow_count = 1 if vendor_metadata.get('flow') else 0
    workflows_count = len(vendor_metadata.get('workflows', []))
    vendor_metadata['workflows'] = _link_workflow_files(vendor, vendor_metadata.get('workflows', []))

    return {
        **vendor_metadata,
        **subscription_info,
        'vendor_internal_page_content_url': f"{BASE_URL}/.generated/docs/vendors/{vendor}/overview.md",
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
            'totalNotifiers': notifier_count,
            'totalFlow': flow_count,
            'totalWorkflows': workflows_count,
            'total': len(analyzers) + len(responders) + len(functions) + external_count + notifier_count + flow_count + workflows_count
        }
    }


# ---------------------------------------------------------------------------
# Case templates
# ---------------------------------------------------------------------------

def _summarize_markdown(text: str, limit: int = 200) -> str:
    """First paragraph line of a markdown description. Headings, rules and tables are skipped."""
    for line in (text or '').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(('#', '---', '|', '>', '```')):
            continue
        # Drop emphasis, inline code and leading list or emoji markers
        stripped = re.sub(r'(\*\*|__|`)', '', stripped)
        stripped = re.sub(r'^[^\w(]+', '', stripped).strip()
        if stripped:
            return stripped if len(stripped) <= limit else stripped[:limit - 1].rstrip() + '…'
    return ''


def _read_pack_metadata(pack_dir: Path) -> Dict:
    """Optional pack.yml next to the templates: name, description, language, credit, license."""
    pack_yml = pack_dir / 'pack.yml'
    if not pack_yml.exists():
        return {}
    try:
        with open(pack_yml, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"  Warning: cannot read {pack_yml}: {e}")
        return {}


def _read_pack_readme(readme_path: Path) -> Dict:
    """Title and first paragraph from a pack README. Both optional."""
    if not readme_path.exists():
        return {}
    try:
        lines = readme_path.read_text(encoding='utf-8').splitlines()
    except Exception:
        return {}
    title = ''
    paragraph: List[str] = []
    for line in lines:
        stripped = line.strip()
        if not title:
            if stripped.startswith('# '):
                title = stripped[2:].strip()
            continue
        if stripped.startswith('#'):
            if paragraph:
                break
            continue
        if stripped:
            paragraph.append(stripped)
        elif paragraph:
            break
    return {'name': title, 'description': ' '.join(paragraph)}


def _pack_language(dir_name: str) -> str:
    upper = dir_name.upper()
    if upper.endswith('_FR') or upper.endswith('-FR'):
        return 'fr'
    return 'en'


def _slugify(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def _read_case_template(file_path: Path, relative_path: str, pack_id: str, owner: Dict) -> Optional[Dict]:
    """Catalog entry for one exported case template. Export metadata (_id, _createdBy, ...) is never copied."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  Warning: cannot read case template {relative_path}: {e}")
        return None
    if not isinstance(data, dict) or 'name' not in data:
        return None

    tasks = data.get('tasks') or []
    custom_fields = data.get('customFields') or []
    if isinstance(custom_fields, dict):
        custom_fields = list(custom_fields.keys())

    return {
        'id': f"{pack_id}/{_slugify(file_path.stem)}",
        'name': data.get('displayName') or data.get('name'),
        'templateName': data.get('name'),
        'description': _summarize_markdown(data.get('description', '')),
        'titlePrefix': data.get('titlePrefix') or '',
        'severity': data.get('severity'),
        'tlp': data.get('tlp'),
        'pap': data.get('pap'),
        'flag': bool(data.get('flag', False)),
        'tags': data.get('tags') or [],
        'tasks': len(tasks),
        'taskTitles': [t.get('title') for t in tasks if isinstance(t, dict) and t.get('title')],
        'customFields': len(custom_fields),
        'pack': pack_id,
        'owner': owner,
        'file': relative_path,
        'url': build_url(relative_path),
        'github_url': build_github_url(relative_path),
    }


def scan_case_templates(root: Path, relative_root: str, owner: Dict) -> tuple[List[Dict], List[Dict]]:
    """Scan a case-templates directory.

    Two layouts are accepted:
      <root>/<Pack>/*.json   one pack per sub-directory, optional README.md per pack (generic content)
      <root>/*.json          a single pack named after the owner (vendor content)
    Returns (packs, templates).
    """
    if not root.exists():
        return [], []

    pack_dirs = sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith('.'))
    if any(root.glob('*.json')):
        pack_dirs.insert(0, root)

    packs: List[Dict] = []
    templates: List[Dict] = []
    for pack_dir in pack_dirs:
        is_root = pack_dir == root
        pack_rel = relative_root if is_root else f"{relative_root}/{pack_dir.name}"
        display_name = owner.get('name', owner['id']) if is_root else pack_dir.name
        if owner['type'] == 'vendor':
            pack_id = _slugify(owner['id']) if is_root else _slugify(f"{owner['id']}-{pack_dir.name}")
        else:
            pack_id = _slugify(display_name)
        readme = _read_pack_readme(pack_dir / 'README.md')
        meta = _read_pack_metadata(pack_dir)

        pack_templates = []
        for file_path in sorted(pack_dir.glob('*.json')):
            entry = _read_case_template(file_path, f"{pack_rel}/{file_path.name}", pack_id, owner)
            if entry:
                pack_templates.append(entry)
        if not pack_templates:
            continue

        # Precedence: pack.yml, then README, then the directory name
        pack = {
            'id': pack_id,
            'name': meta.get('name') or display_name,
            'description': meta.get('description') or readme.get('description', ''),
            'language': meta.get('language') or _pack_language(pack_dir.name),
            'owner': owner,
            'path': pack_rel,
            'github_url': build_github_url(pack_rel),
            'templates': len(pack_templates),
        }
        for optional in ('credit', 'license', 'source'):
            if meta.get(optional):
                pack[optional] = meta[optional]
        if (pack_dir / 'README.md').exists():
            pack['readme_url'] = build_github_url(f"{pack_rel}/README.md")
        packs.append(pack)
        templates.extend(pack_templates)

    return packs, templates


# ---------------------------------------------------------------------------
# Dashboards
# ---------------------------------------------------------------------------

def _read_dashboard(file_path: Path, relative_path: str, owner: Dict) -> Optional[Dict]:
    """Catalog entry for one exported dashboard. Export metadata (_id, owner, group, ...) is never copied."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  Warning: cannot read dashboard {relative_path}: {e}")
        return None
    if not isinstance(data, dict) or 'title' not in data:
        return None

    definition = data.get('definition') or {}
    if isinstance(definition, str):
        try:
            definition = json.loads(definition)
        except Exception:
            definition = {}

    # A definition is a list of containers (rows), each holding the widgets. Only that level is
    # read: deeper objects are widget options and filters, not widgets.
    widgets = []
    for container in definition.get('items') or []:
        if not isinstance(container, dict):
            continue
        for widget in container.get('items') or []:
            if not isinstance(widget, dict):
                continue
            options = widget.get('options') or {}
            widgets.append({
                'title': options.get('title') or widget.get('title') or '',
                'type': widget.get('type'),
                'entity': options.get('entity') or widget.get('entity'),
            })

    entities = sorted({w['entity'] for w in widgets if w['entity']})

    return {
        'id': f"{_slugify(owner['id'])}/{_slugify(file_path.stem)}",
        'name': data.get('title'),
        'description': _summarize_markdown(data.get('description', '')),
        'version': data.get('version'),
        'period': definition.get('period'),
        'entities': entities,
        'widgets': len(widgets),
        'widgetList': widgets,
        'owner': owner,
        'file': relative_path,
        'url': build_url(relative_path),
        'github_url': build_github_url(relative_path),
    }


def scan_dashboards(root: Path, relative_root: str, owner: Dict) -> List[Dict]:
    """Scan a flat directory of exported dashboards."""
    if not root.exists():
        return []
    dashboards = []
    for file_path in sorted(root.glob('*.json')):
        entry = _read_dashboard(file_path, f"{relative_root}/{file_path.name}", owner)
        if entry:
            dashboards.append(entry)
    return dashboards


def _collect_filter_values(node, key: str, found: set) -> None:
    """Walk a notification filter and collect every value `key` is matched against.

    Handles both forms, {"_is": {"objectType": "Case"}} and
    {"_in": {"_field": "objectType", "_values": ["Case", "Alert"]}}. Negated branches are
    skipped: a value the filter excludes is not one it triggers on.
    """
    if isinstance(node, list):
        for item in node:
            _collect_filter_values(item, key, found)
        return
    if not isinstance(node, dict):
        return
    if node.get('_field') == key:
        values = node.get('_values', node.get('_value'))
        for value in values if isinstance(values, list) else [values]:
            if isinstance(value, (str, int, bool)):
                found.add(value)
        return
    for k, value in node.items():
        if k in ('_not', '_ne'):
            continue
        if k == key:
            for item in value if isinstance(value, list) else [value]:
                if isinstance(item, (str, int, bool)):
                    found.add(item)
        else:
            _collect_filter_values(value, key, found)


def _read_notification(file_path: Path, relative_path: str, owner: Dict) -> Optional[Dict]:
    """Catalog entry for one notification filter definition."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  Warning: cannot read notification {relative_path}: {e}")
        return None
    if not isinstance(data, dict) or 'name' not in data or 'filter' not in data:
        return None
    # Filters known not to work stay in the repo but are not published
    if data.get('status') == 'not_working':
        return None

    object_types, actions = set(), set()
    _collect_filter_values(data['filter'], 'objectType', object_types)
    _collect_filter_values(data['filter'], 'action', actions)

    entry = {
        'id': f"{_slugify(owner['id'])}/{_slugify(file_path.stem)}",
        'name': data.get('name'),
        'description': data.get('description', ''),
        'type': data.get('type'),
        'status': data.get('status'),
        'objectTypes': sorted(object_types),
        'actions': sorted(actions),
        'filter': data['filter'],
        'owner': owner,
        'file': relative_path,
        'url': build_url(relative_path),
        'github_url': build_github_url(relative_path),
    }
    for key in ('comment', 'contributor'):
        if data.get(key):
            entry[key] = data[key]
    return entry


def scan_notifications(root: Path, relative_root: str, owner: Dict) -> List[Dict]:
    """Scan a flat directory of notification filter definitions."""
    if not root.exists():
        return []
    notifications = []
    for file_path in sorted(root.glob('*.json')):
        entry = _read_notification(file_path, f"{relative_root}/{file_path.name}", owner)
        if entry:
            notifications.append(entry)
    return notifications


def _text(value) -> Optional[str]:
    return None if value is None else str(value)


def _read_workflow_export(file_path: Path) -> Optional[Dict]:
    """Facts derived from one TheHive Flow export. The export is only read, never rewritten, and
    its instance metadata (id, organisation, created_by, modified_by) is never copied.
    Any file that does not have the expected shape is skipped with a warning."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        data = yaml.safe_load(raw)
        if not isinstance(data, dict) or not isinstance(data.get('workflow'), dict):
            print(f"  Warning: {file_path} is not a TheHive Flow export, skipped")
            return None

        steps = [s for s in data['workflow'].values() if isinstance(s, dict)]
        commands = set()
        for step in steps:
            command = step.get('command')
            if isinstance(command, dict) and isinstance(command.get('command'), str):
                commands.add(command['command'])
        # strangebee.integration.<name>.<version> -> <name>
        integrations = sorted({c.split('.')[2] for c in commands
                               if c.startswith('strangebee.integration.') and len(c.split('.')) > 2})
        variables = data.get('variables')
        declared_inputs = variables.get('input') if isinstance(variables, dict) else None
        inputs = [v['name'] for v in declared_inputs or [] if isinstance(v, dict) and v.get('name')]

        return {
            # Always text or null, whatever YAML made of the value (a bare `version: 1` is a number)
            'export_name': _text(data.get('name')),
            'spec_version': _text(data.get('spec_version')),
            'version': _text(data.get('version')),
            'timeout': _text(data.get('timeout')),
            'steps': sum(1 for s in steps if s.get('type') != 'start'),
            'flow_integrations': integrations,
            'commands': sorted(commands),
            'inputs': inputs,
            # What the importer has to bind in their own instance before the workflow can run
            'requires': {
                'secrets': len(set(re.findall(r'\$secret\["([^"]+)"\]', raw))),
                'globals': len(set(re.findall(r'\$global\["([^"]+)"\]', raw))),
            },
        }
    except Exception as e:
        print(f"  Warning: cannot read workflow {file_path}: {e}")
        return None


WORKFLOW_MAINTAINERS = ('strangebee', 'partner', 'community')


def workflow_declared_fields(workflow: Optional[Dict]) -> Dict:
    """Hand-declared catalog fields of a workflow entry, with their defaults.
    A workflow is 'community' unless its entry says otherwise, so nothing is presented as
    maintained by StrangeBee or a partner by omission."""
    workflow = workflow if isinstance(workflow, dict) else {}
    maintainer = workflow.get('maintainer')
    use_cases = workflow.get('use_cases')
    authors = workflow.get('author')
    return {
        'maintainer': maintainer if maintainer in WORKFLOW_MAINTAINERS else 'community',
        'use_cases': [u for u in use_cases if isinstance(u, str)] if isinstance(use_cases, list) else [],
        'popular': workflow.get('popular') is True,
        'author': [{'name': a['name'], 'url': a.get('url'), 'icon': a.get('icon')}
                   for a in authors if isinstance(a, dict) and a.get('name')] if isinstance(authors, list) else [],
    }


def workflow_slug_from_url(url: str) -> str:
    """https://strangebee.com/workflow/Command-Line-Analysis/?x=1 -> command-line-analysis"""
    path = re.split(r'[?#]', url or '', maxsplit=1)[0]
    return path.rstrip('/').rsplit('/', 1)[-1].lower()


def workflow_slug(workflow: Dict) -> str:
    """Slug that ties a declared workflow to its export file: from the page url, else from the name."""
    return (workflow_slug_from_url(workflow.get('url'))
            or re.sub(r'[^a-z0-9]+', '-', (workflow.get('name') or '').lower()).strip('-'))


def scan_workflows(root: Path, relative_root: str, declared: List[Dict], owner: Dict) -> List[Dict]:
    """Workflows of one owner: the declared entries (name, url, description), each joined to its
    export file <root>/<slug>.yml when present. Export files with no declaration are listed too,
    with a warning, since that usually means the url and the file name do not match.
    Files starting with '_' are metadata, not exports."""
    exports = {}
    if root.exists():
        for file_path in sorted(list(root.glob('*.yml')) + list(root.glob('*.yaml'))):
            if file_path.name.startswith('_'):
                continue
            slug = file_path.stem.lower()
            if slug in exports:
                print(f"  Warning: {file_path} ignored, {exports[slug][0].name} already provides '{slug}'")
                continue
            export = _read_workflow_export(file_path)
            if export:
                exports[slug] = (file_path, export)

    def entry(slug: str, name: str, url: Optional[str], description: Optional[str],
              declared_entry: Optional[Dict] = None) -> Dict:
        item = {
            'id': f"{owner['id'].lower()}/{slug}",
            'name': name,
            'url': url,
            'description': description,
            **workflow_declared_fields(declared_entry),
            'owner': owner,
            'has_file': slug in exports,
            # Same keys whether or not there is an export file: null or empty when there is none
            'file': None, 'file_url': None, 'github_url': None,
            'export_name': None, 'spec_version': None, 'version': None, 'timeout': None, 'steps': None,
            'flow_integrations': [], 'commands': [], 'inputs': [], 'requires': None,
        }
        if slug in exports:
            file_path, export = exports.pop(slug)
            relative_path = f"{relative_root}/{file_path.name}"
            item.update({
                'file': relative_path,
                'file_url': build_url(relative_path),
                'github_url': build_github_url(relative_path),
                **export,
            })
        return item

    workflows = []
    seen = set()
    for workflow in declared or []:
        if not isinstance(workflow, dict) or not workflow.get('name'):
            print(f"  Warning: workflow entry without a name ignored for {owner['id']}")
            continue
        slug = workflow_slug(workflow)
        if slug in seen:
            print(f"  Warning: workflow '{workflow['name']}' ignored for {owner['id']}, '{slug}' is declared twice")
            continue
        seen.add(slug)
        workflows.append(entry(slug, workflow['name'], workflow.get('url'), workflow.get('description'), workflow))
    for slug in sorted(exports):
        file_path, export = exports[slug]
        print(f"  Warning: {relative_root}/{file_path.name} has no declared workflow (name, url, description)")
        workflows.append(entry(slug, export.get('export_name') or slug, None, None))
    return workflows
