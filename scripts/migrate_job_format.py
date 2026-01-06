#!/usr/bin/env python3
"""
Migrate job YAML files to standardized format.

Changes:
1. Rename request_id → job_id
2. Add prompt_set field (inferred from directory)
3. Add intervention field (inferred from directory or job_id suffix)
4. Enhance metadata section with new fields
5. Add gap fill identification

Usage:
    python scripts/migrate_job_format.py --dry-run    # Preview changes
    python scripts/migrate_job_format.py              # Execute migration
"""

import argparse
import yaml
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import re


# Directory name → (prompt_set, intervention, is_gap_fill)
DIRECTORY_MAPPING = {
    # Love v1
    'love_v1': ('Ps.love', 'baseline', False),
    'love_v1_checkpoint': ('Ps.love', 'urgency', False),
    'love_v1_telemetry': ('Ps.love', 'authority', False),
    'love_v1_reminder': ('Ps.love', 'reminder', False),
    'love_v1_shake': ('Ps.love', 'shake', False),
    'love_v1_baseline_gap': ('Ps.love', 'baseline', True),

    # Personality v2
    'personality_v2': ('Ps.v2', 'baseline', False),
    'personality_v2_checkpoint': ('Ps.v2', 'urgency', False),
    'personality_v2_telemetry': ('Ps.v2', 'authority', False),
    'personality_v2_reminder': ('Ps.v2', 'reminder', False),
    'personality_v2_shake': ('Ps.v2', 'shake', False),
    'personality_v2_baseline_gap': ('Ps.v2', 'baseline', True),

    # Typical v2
    'typical_v2': ('Ps.typical', 'baseline', False),
    'typical_v2_checkpoint': ('Ps.typical', 'urgency', False),
    'typical_v2_telemetry': ('Ps.typical', 'authority', False),
    'typical_v2_reminder': ('Ps.typical', 'reminder', False),
    'typical_v2_shake': ('Ps.typical', 'shake', False),
    'typical_v2_baseline_gap': ('Ps.typical', 'baseline', True),

    # Personality v6-v8 gap
    'personality_v6-v8_gap': ('Ps1.v6-v8', 'baseline', True),
}


def infer_metadata(job_path: Path) -> Tuple[str, str, bool]:
    """
    Infer prompt_set, intervention, and gap fill status from directory name.

    Returns:
        (prompt_set, intervention, is_gap_fill)
    """
    dir_name = job_path.parent.name

    if dir_name in DIRECTORY_MAPPING:
        return DIRECTORY_MAPPING[dir_name]

    # Fallback: try to parse from directory name
    if 'gap' in dir_name:
        is_gap_fill = True
    else:
        is_gap_fill = False

    # Extract intervention type
    if '_checkpoint' in dir_name:
        intervention = 'urgency'
    elif '_telemetry' in dir_name:
        intervention = 'authority'
    elif '_reminder' in dir_name:
        intervention = 'reminder'
    elif '_shake' in dir_name:
        intervention = 'shake'
    else:
        intervention = 'baseline'

    # Extract prompt set
    if 'love' in dir_name:
        prompt_set = 'Ps.love'
    elif 'typical' in dir_name:
        prompt_set = 'Ps.typical'
    elif 'personality_v2' in dir_name:
        prompt_set = 'Ps.v2'
    elif 'personality_v6' in dir_name or 'personality_v7' in dir_name or 'personality_v8' in dir_name:
        prompt_set = 'Ps1.v6-v8'
    elif 'personality_v3' in dir_name or 'personality_v4' in dir_name or 'personality_v5' in dir_name:
        prompt_set = 'Ps1.v3-5'
    else:
        prompt_set = 'Ps.unknown'

    return prompt_set, intervention, is_gap_fill


def extract_version(prompt_set: str) -> Optional[str]:
    """Extract version number from prompt_set tag."""
    if prompt_set == 'Ps.v2':
        return '2'
    elif prompt_set == 'Ps.love':
        return '1'
    elif prompt_set == 'Ps.typical':
        return '2'
    elif prompt_set == 'Ps1.v3-5':
        return '3-5'
    elif prompt_set == 'Ps1.v6-v8':
        return '6-8'
    return None


def migrate_job(job_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """
    Migrate a single job file to new format.

    Returns dict with:
        - status: 'migrated', 'skipped', 'error'
        - message: description of action taken
        - changes: list of changes made
    """
    try:
        with open(job_path, 'r') as f:
            job_data = yaml.safe_load(f)

        if not job_data:
            return {
                'status': 'error',
                'message': 'Empty or invalid YAML',
                'changes': []
            }

        changes = []

        # 1. Rename request_id → job_id
        if 'request_id' in job_data and 'job_id' not in job_data:
            job_data['job_id'] = job_data.pop('request_id')
            changes.append('Renamed request_id → job_id')
        elif 'job_id' in job_data:
            changes.append('Already has job_id (no change)')
        else:
            # Neither field present - use filename
            job_data['job_id'] = job_path.stem
            changes.append('Added job_id from filename')

        # 2. Infer and add prompt_set, intervention, is_gap_fill
        prompt_set, intervention, is_gap_fill = infer_metadata(job_path)

        if 'prompt_set' not in job_data:
            job_data['prompt_set'] = prompt_set
            changes.append(f'Added prompt_set: {prompt_set}')

        if 'intervention' not in job_data:
            job_data['intervention'] = intervention
            changes.append(f'Added intervention: {intervention}')

        # 3. Enhance metadata section
        if 'metadata' not in job_data:
            job_data['metadata'] = {}

        metadata = job_data['metadata']

        # Add version
        version = extract_version(prompt_set)
        if version and 'prompt_set_version' not in metadata:
            metadata['prompt_set_version'] = version
            changes.append(f'Added metadata.prompt_set_version: {version}')

        # Add intervention_type (duplicate for backwards compat)
        if 'intervention_type' not in metadata:
            metadata['intervention_type'] = intervention
            changes.append(f'Added metadata.intervention_type: {intervention}')

        # Add gap fill flags
        if 'is_gap_fill' not in metadata:
            metadata['is_gap_fill'] = is_gap_fill
            changes.append(f'Added metadata.is_gap_fill: {is_gap_fill}')

        if is_gap_fill and 'gap_models_only' not in metadata:
            metadata['gap_models_only'] = True
            changes.append('Added metadata.gap_models_only: True')

        # 4. Write back to file (unless dry run)
        if not dry_run:
            # Preserve field order by using custom YAML dumper
            with open(job_path, 'w') as f:
                yaml.dump(job_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        return {
            'status': 'migrated' if changes else 'skipped',
            'message': f"{len(changes)} changes made",
            'changes': changes,
            'file': str(job_path)
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'changes': [],
            'file': str(job_path)
        }


def main():
    parser = argparse.ArgumentParser(description='Migrate job YAML files to standardized format')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--dir', default='payload/single_prompt_jobs', help='Directory to scan for job files')
    parser.add_argument('--file', help='Migrate a single file instead of scanning directory')
    args = parser.parse_args()

    # Find all job YAML files
    if args.file:
        job_files = [Path(args.file)]
    else:
        job_dir = Path(args.dir)
        if not job_dir.exists():
            print(f"Error: Directory not found: {job_dir}")
            return 1

        job_files = sorted(job_dir.glob('**/*.yaml'))
        # Exclude TEMPLATE.yaml and files in archive/
        job_files = [f for f in job_files
                     if f.name != 'TEMPLATE.yaml'
                     and 'archive' not in f.parts]

    if not job_files:
        print("No job files found")
        return 0

    print(f"{'DRY RUN - ' if args.dry_run else ''}Migrating {len(job_files)} job files")
    print("=" * 80)

    # Track statistics
    stats = {
        'migrated': 0,
        'skipped': 0,
        'error': 0
    }

    results_by_dir = {}

    # Process each file
    for job_file in job_files:
        result = migrate_job(job_file, dry_run=args.dry_run)
        stats[result['status']] += 1

        # Group by directory for reporting
        dir_name = job_file.parent.name
        if dir_name not in results_by_dir:
            results_by_dir[dir_name] = []
        results_by_dir[dir_name].append(result)

    # Print results grouped by directory
    for dir_name, results in sorted(results_by_dir.items()):
        print(f"\n{dir_name}/")
        print("-" * 80)

        migrated_count = sum(1 for r in results if r['status'] == 'migrated')
        skipped_count = sum(1 for r in results if r['status'] == 'skipped')
        error_count = sum(1 for r in results if r['status'] == 'error')

        print(f"  Files: {len(results)} | Migrated: {migrated_count} | Skipped: {skipped_count} | Errors: {error_count}")

        # Show sample changes (first file only)
        if results and results[0]['changes']:
            print(f"  Sample changes ({results[0]['file']}):")
            for change in results[0]['changes'][:5]:
                print(f"    • {change}")
            if len(results[0]['changes']) > 5:
                print(f"    ... and {len(results[0]['changes']) - 5} more")

        # Show errors
        for result in results:
            if result['status'] == 'error':
                print(f"  ERROR: {result['file']}: {result['message']}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {len(job_files)}")
    print(f"  Migrated: {stats['migrated']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors: {stats['error']}")

    if args.dry_run:
        print("\n*** DRY RUN - No files were modified ***")
        print("Run without --dry-run to apply changes")
    else:
        print("\n✓ Migration complete")

    return 0 if stats['error'] == 0 else 1


if __name__ == '__main__':
    exit(main())
