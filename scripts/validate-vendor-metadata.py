#!/usr/bin/env python3
"""Validate vendor.yml files against schema and taxonomy.

Usage:
    python validate-vendor-metadata.py [--vendor VENDOR_NAME] [--strict]
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import yaml

try:
    from jsonschema import Draft7Validator
except ImportError:
    print("Error: jsonschema package not found. Install with: pip install jsonschema")
    sys.exit(1)


RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def load_yaml_file(path: Path) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


GENERIC_WORKFLOWS_DIR = Path('integrations') / 'generic' / 'thehive' / 'workflows'
GENERIC_WORKFLOWS_METADATA = GENERIC_WORKFLOWS_DIR / '_metadata.yml'


def workflow_slug(workflow: Dict) -> str:
    """Same rule as manifest_utils.workflow_slug: last segment of the page url, else the name."""
    path = re.split(r'[?#]', workflow.get('url') or '', maxsplit=1)[0]
    slug = path.rstrip('/').rsplit('/', 1)[-1].lower()
    return slug or re.sub(r'[^a-z0-9]+', '-', (workflow.get('name') or '').lower()).strip('-')


def check_workflow_files(workflows_dir: Path, declared, declared_in: str) -> List[str]:
    """Every export file in thehive/workflows/ must be declared, and each slug declared once.
    A declared workflow with no file is allowed: it is a link to the workflow page only."""
    errors = []
    slugs = []
    for workflow in declared if isinstance(declared, list) else []:
        if isinstance(workflow, dict):
            slugs.append(workflow_slug(workflow))
    for slug in sorted({s for s in slugs if slugs.count(s) > 1}):
        errors.append(f"Workflow '{slug}' is declared more than once in {declared_in}")

    if not workflows_dir.is_dir():
        return errors
    seen = {}
    for file_path in sorted(list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))):
        if file_path.name.startswith('_'):
            continue
        slug = file_path.stem.lower()
        if slug in seen:
            errors.append(f"Workflow files {seen[slug]} and {file_path.name} have the same name")
            continue
        seen[slug] = file_path.name
        if slug not in slugs:
            errors.append(f"Workflow file {file_path.name} is not declared in {declared_in}: add an entry "
                          f"whose url ends with '/{slug}/', or rename the file to match the url")
        try:
            export = load_yaml_file(file_path)
            if not isinstance(export, dict) or not isinstance(export.get('workflow'), dict):
                errors.append(f"Workflow file {file_path.name} is not a TheHive Flow export")
        except Exception as e:
            errors.append(f"Workflow file {file_path.name} cannot be read: {e}")
    return errors


def check_workflow_use_cases(declared, taxonomy: Dict) -> List[str]:
    """Each use case of a workflow entry must be listed under workflow_use_cases in taxonomy.yml."""
    valid = [u['name'] for u in taxonomy.get('workflow_use_cases', []) if isinstance(u, dict) and u.get('name')]
    errors = []
    for workflow in declared if isinstance(declared, list) else []:
        if not valid or not isinstance(workflow, dict) or not isinstance(workflow.get('use_cases'), list):
            continue
        invalid = [u for u in workflow['use_cases'] if u not in valid]
        if invalid:
            errors.append(f"Workflow '{workflow.get('name')}': invalid use case(s) {', '.join(map(str, invalid))}. "
                          f"Valid: {', '.join(valid)}")
    return errors


def validate_generic_workflows(schema: Dict, taxonomy: Dict) -> List[str]:
    """Validate the generic workflows metadata with the same rules as `workflows:` in vendor.yml."""
    has_files = GENERIC_WORKFLOWS_DIR.is_dir() and any(
        not p.name.startswith('_') for p in list(GENERIC_WORKFLOWS_DIR.glob('*.yml')) + list(GENERIC_WORKFLOWS_DIR.glob('*.yaml')))
    if not GENERIC_WORKFLOWS_METADATA.exists():
        return [f"{GENERIC_WORKFLOWS_METADATA} not found but workflow files exist"] if has_files else []

    try:
        metadata = load_yaml_file(GENERIC_WORKFLOWS_METADATA)
    except yaml.YAMLError as e:
        return [f"YAML parsing error: {e}"]
    if not isinstance(metadata, dict):
        return ["File must be a mapping with a 'workflows' list"]

    metadata_schema = {
        'type': 'object',
        'required': ['workflows'],
        'properties': {'workflows': schema.get('properties', {}).get('workflows', {'type': 'array'})},
        'additionalProperties': False,
    }
    errors = []
    for error in Draft7Validator(metadata_schema).iter_errors(metadata):
        field = '.'.join(str(p) for p in error.path) if error.path else None
        prefix = f"Schema error at '{field}'" if field else "Schema error"
        errors.append(f"{prefix}: {error.message}")
    errors.extend(check_workflow_files(GENERIC_WORKFLOWS_DIR, metadata.get('workflows'), '_metadata.yml'))
    errors.extend(check_workflow_use_cases(metadata.get('workflows'), taxonomy))
    return errors


def validate_vendor_file(vendor_name: str, schema: Dict, taxonomy: Dict) -> Tuple[str, List[str]]:
    vendor_yml_path = Path('integrations') / 'vendors' / vendor_name / 'vendor.yml'

    if not vendor_yml_path.exists():
        return 'missing', [
            "vendor.yml not found - manifest will be generated with empty defaults",
            "Create vendor.yml with at minimum: description, category, tags, homepage"
        ]

    errors = []

    try:
        vendor_data = load_yaml_file(vendor_yml_path)
        if not vendor_data:
            return 'invalid', ["vendor.yml is empty"]

        # Schema validation
        try:
            for error in Draft7Validator(schema).iter_errors(vendor_data):
                field = '.'.join(str(p) for p in error.path) if error.path else None
                prefix = f"Schema error at '{field}'" if field else "Schema error"
                errors.append(f"{prefix}: {error.message}")
        except Exception as e:
            errors.append(f"Schema validation failed: {e}")

        # Taxonomy validation
        valid_categories = [c['name'] for c in taxonomy.get('categories', [])]
        valid_tags = [t['name'] for t in taxonomy.get('tags', [])]

        category = vendor_data.get('category')
        if category and valid_categories and category not in valid_categories:
            errors.append(f"Invalid category '{category}'. Valid: {', '.join(valid_categories)}")

        tags = vendor_data.get('tags', [])
        if tags and valid_tags:
            invalid = [t for t in tags if t not in valid_tags]
            if invalid:
                errors.append(f"Invalid tags: {', '.join(invalid)}. See taxonomy.yml for valid tags.")

        if 'id' in vendor_data and vendor_data['id'] != vendor_name:
            errors.append(f"ID mismatch: vendor.yml has id '{vendor_data['id']}' but directory is '{vendor_name}'")

        errors.extend(check_workflow_files(
            Path('integrations') / 'vendors' / vendor_name / 'thehive' / 'workflows',
            vendor_data.get('workflows'), 'vendor.yml'))
        errors.extend(check_workflow_use_cases(vendor_data.get('workflows'), taxonomy))

        if errors and vendor_data.get('displayOnWebsite') is False:
            return 'hidden', errors
        return ('valid' if not errors else 'invalid'), errors

    except yaml.YAMLError as e:
        return 'invalid', [f"YAML parsing error: {e}"]
    except Exception as e:
        return 'invalid', [f"Unexpected error: {e}"]


def check_flow_ids(vendors: List[str]) -> List[str]:
    """A flow.id links workflow nodes to one vendor, so two vendors cannot declare the same one."""
    owners = {}
    for vendor in vendors:
        try:
            data = load_yaml_file(Path('integrations') / 'vendors' / vendor / 'vendor.yml')
        except Exception:
            continue
        flow = data.get('flow') if isinstance(data, dict) else None
        flow_id = flow.get('id') if isinstance(flow, dict) else None
        if isinstance(flow_id, str) and flow_id:
            owners.setdefault(flow_id, []).append(vendor)
    return [f"flow.id '{flow_id}' is declared by several vendors: {', '.join(names)}"
            for flow_id, names in sorted(owners.items()) if len(names) > 1]


def find_all_vendors() -> List[str]:
    vendors_path = Path('integrations') / 'vendors'
    if not vendors_path.exists():
        return []
    return sorted(d.name for d in vendors_path.iterdir() if d.is_dir())


def validate_all_vendors(schema: Dict, taxonomy: Dict, specific_vendor: str = None) -> bool:
    vendors = [specific_vendor] if specific_vendor else find_all_vendors()
    label = f"vendor: {specific_vendor}" if specific_vendor else f"{len(vendors)} vendors"
    print(f"{BLUE}Validating {label}{NC}\n")

    valid_count = missing_count = invalid_count = hidden_count = 0
    status_config = {
        'valid': (GREEN, 'V'),
        'missing': (YELLOW, '?'),
        'hidden': (YELLOW, '~'),
        'invalid': (RED, 'X'),
    }

    for vendor in vendors:
        status, messages = validate_vendor_file(vendor, schema, taxonomy)
        color, icon = status_config.get(status, (RED, 'X'))
        print(f"{color}{icon} {vendor}{NC}")
        for msg in messages:
            print(f"   {color}>{NC} {msg}")

        if status == 'valid':
            valid_count += 1
        elif status == 'missing':
            missing_count += 1
        elif status == 'hidden':
            hidden_count += 1
        else:
            invalid_count += 1

    print(f"\n{CYAN}{'='*60}{NC}")
    print(f"Total: {len(vendors)} | {GREEN}Valid: {valid_count}{NC} | "
          f"{YELLOW}Missing: {missing_count}{NC} | {YELLOW}Hidden with issues: {hidden_count}{NC} | "
          f"{RED}Invalid: {invalid_count}{NC}")

    if valid_count < len(vendors):
        coverage = (valid_count / len(vendors) * 100) if vendors else 0
        print(f"Coverage: {coverage:.1f}%")

    return invalid_count == 0


def main():
    parser = argparse.ArgumentParser(description='Validate vendor.yml files against schema and taxonomy')
    parser.add_argument('--vendor', type=str, help='Validate specific vendor only')
    parser.add_argument('--strict', action='store_true', help='Exit with error code if any validation fails')
    args = parser.parse_args()

    schema_path = Path('scripts') / 'schemas' / 'vendor-schema.yml'
    taxonomy_path = Path('scripts') / 'schemas' / 'taxonomy.yml'

    if not schema_path.exists():
        print(f"{RED}Error: {schema_path} not found{NC}")
        sys.exit(1)

    schema = load_yaml_file(schema_path)
    taxonomy = load_yaml_file(taxonomy_path) if taxonomy_path.exists() else {'categories': [], 'tags': []}

    all_valid = validate_all_vendors(schema, taxonomy, args.vendor)

    if not args.vendor:
        generic_errors = validate_generic_workflows(schema, taxonomy)
        color, icon = (RED, 'X') if generic_errors else (GREEN, 'V')
        print(f"\n{color}{icon} Generic workflows ({GENERIC_WORKFLOWS_METADATA}){NC}")
        for msg in generic_errors:
            print(f"   {color}>{NC} {msg}")
        all_valid = all_valid and not generic_errors

        flow_id_errors = check_flow_ids(find_all_vendors())
        for msg in flow_id_errors:
            print(f"{RED}X{NC} {msg}")
        all_valid = all_valid and not flow_id_errors

    if args.strict and not all_valid:
        sys.exit(1)


if __name__ == '__main__':
    main()
