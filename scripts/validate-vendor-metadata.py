#!/usr/bin/env python3
"""Validate vendor.yml files against schema and taxonomy.

Usage:
    python validate-vendor-metadata.py [--vendor VENDOR_NAME] [--strict]
"""

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

        if errors and vendor_data.get('displayOnWebsite') is False:
            return 'hidden', errors
        return ('valid' if not errors else 'invalid'), errors

    except yaml.YAMLError as e:
        return 'invalid', [f"YAML parsing error: {e}"]
    except Exception as e:
        return 'invalid', [f"Unexpected error: {e}"]


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
    if args.strict and not all_valid:
        sys.exit(1)


if __name__ == '__main__':
    main()
