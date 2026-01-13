#!/usr/bin/env python3
"""
Find and report on all judge evaluations with json_validation structure.
This is the old (fantastic) repair method that:
- Preserves original invalid JSON for posterity
- Tracks repair status
- Flags items to exclude from statistics
"""

import json
import sys
from pathlib import Path
from collections import defaultdict


def analyze_json_validation_structure():
    """Find all files with json_validation structure."""

    directories = [
        'outputs/single_prompt_jobs/baseline_affective',
        'outputs/single_prompt_jobs/baseline_broad',
        'outputs/single_prompt_jobs/baseline_dimensions',
        'outputs/single_prompt_jobs/baseline_general',
        'outputs/single_prompt_jobs/baseline_telemetryV3_affective',
        'outputs/single_prompt_jobs/baseline_telemetryV3_broad',
        'outputs/single_prompt_jobs/baseline_telemetryV3_dimensions',
        'outputs/single_prompt_jobs/baseline_telemetryV3_general',
    ]

    results = {
        'total_files_checked': 0,
        'files_with_validation': [],
        'by_status': {
            'repaired_successfully': [],      # repaired: true
            'flagged_needs_repair': [],       # flagged_for_repair: true, repaired: false
            'excluded_from_stats': []         # exclude_from_stats: true
        },
        'by_model': defaultdict(list),
        'by_judge': defaultdict(list),
        'by_failure_type': defaultdict(list)
    }

    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue

        json_files = list(dir_path.rglob('*.json'))
        results['total_files_checked'] += len(json_files)

        for f in json_files:
            try:
                with open(f) as fp:
                    data = json.load(fp)

                if 'judge_evaluation' not in data:
                    continue

                evals = data['judge_evaluation'].get('evaluations', [])
                file_has_validation = False

                for eval_idx, ev in enumerate(evals):
                    model_name = ev.get('display_name', 'unknown')

                    for judge_idx, judge in enumerate(ev.get('pass1_judges', [])):
                        if 'json_validation' not in judge:
                            continue

                        file_has_validation = True
                        validation = judge['json_validation']

                        entry = {
                            'file': str(f.relative_to('outputs/single_prompt_jobs')),
                            'file_path': str(f),
                            'model': model_name,
                            'judge_number': judge_idx + 1,
                            'judge_model': judge.get('judge_display_name', 'unknown'),
                            'validation': validation,
                            'original_valid': validation.get('original_valid'),
                            'repaired': validation.get('repaired'),
                            'exclude_from_stats': validation.get('exclude_from_stats'),
                            'extraction_failed': validation.get('original_invalid_response', {}).get('extraction_failed'),
                            'flagged_for_repair': validation.get('original_invalid_response', {}).get('flagged_for_repair')
                        }

                        # Categorize by status
                        if validation.get('repaired'):
                            results['by_status']['repaired_successfully'].append(entry)

                        if validation.get('original_invalid_response', {}).get('flagged_for_repair'):
                            if not validation.get('repaired'):
                                results['by_status']['flagged_needs_repair'].append(entry)

                        if validation.get('exclude_from_stats'):
                            results['by_status']['excluded_from_stats'].append(entry)

                        # Track by model and judge
                        results['by_model'][model_name].append(entry)
                        results['by_judge'][entry['judge_model']].append(entry)

                        # Track failure types
                        if validation.get('original_invalid_response', {}).get('extraction_failed'):
                            results['by_failure_type']['extraction_failed'].append(entry)

                if file_has_validation:
                    results['files_with_validation'].append(str(f.relative_to('outputs/single_prompt_jobs')))

            except Exception as e:
                print(f"Error reading {f.name}: {e}", file=sys.stderr)

    return results


def print_report(results):
    """Print comprehensive report."""

    print("=" * 80)
    print("JSON VALIDATION REPAIR SYSTEM REPORT")
    print("=" * 80)
    print(f"Total files checked: {results['total_files_checked']}")
    print(f"Files with json_validation structure: {len(results['files_with_validation'])}")
    print()

    print("=" * 80)
    print("STATUS BREAKDOWN")
    print("=" * 80)
    print(f"✓ Successfully repaired: {len(results['by_status']['repaired_successfully'])}")
    print(f"⚠ Flagged for repair (needs fixing): {len(results['by_status']['flagged_needs_repair'])}")
    print(f"✗ Excluded from stats: {len(results['by_status']['excluded_from_stats'])}")
    print()

    # Show repaired examples
    if results['by_status']['repaired_successfully']:
        print("=" * 80)
        print("SUCCESSFULLY REPAIRED (first 5)")
        print("=" * 80)
        for entry in results['by_status']['repaired_successfully'][:5]:
            print(f"\n{Path(entry['file']).name}")
            print(f"  Model: {entry['model']}")
            print(f"  Judge {entry['judge_number']}: {entry['judge_model']}")
            print(f"  Exclude from stats: {entry['exclude_from_stats']}")

    # Show needs repair
    if results['by_status']['flagged_needs_repair']:
        print("\n" + "=" * 80)
        print("FLAGGED FOR REPAIR - NOT YET FIXED (first 5)")
        print("=" * 80)
        for entry in results['by_status']['flagged_needs_repair'][:5]:
            print(f"\n{Path(entry['file']).name}")
            print(f"  Model: {entry['model']}")
            print(f"  Judge {entry['judge_number']}: {entry['judge_model']}")
            print(f"  Exclude from stats: {entry['exclude_from_stats']}")

    # Show excluded from stats
    if results['by_status']['excluded_from_stats']:
        print("\n" + "=" * 80)
        print("EXCLUDED FROM STATISTICS")
        print("=" * 80)
        for entry in results['by_status']['excluded_from_stats']:
            print(f"\n{Path(entry['file']).name}")
            print(f"  Model: {entry['model']}")
            print(f"  Judge {entry['judge_number']}: {entry['judge_model']}")
            print(f"  Repaired: {entry['repaired']}")

    # Models with most issues
    print("\n" + "=" * 80)
    print("MODELS WITH MOST JSON VALIDATION ENTRIES")
    print("=" * 80)
    model_counts = [(model, len(entries)) for model, entries in results['by_model'].items()]
    model_counts.sort(key=lambda x: x[1], reverse=True)
    for model, count in model_counts[:10]:
        print(f"  {model}: {count}")

    # Judges with most issues
    print("\n" + "=" * 80)
    print("JUDGES WITH MOST JSON VALIDATION ENTRIES")
    print("=" * 80)
    judge_counts = [(judge, len(entries)) for judge, entries in results['by_judge'].items()]
    judge_counts.sort(key=lambda x: x[1], reverse=True)
    for judge, count in judge_counts[:10]:
        print(f"  {judge}: {count}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Find and report on json_validation repair structure'
    )
    parser.add_argument('--json', action='store_true',
                        help='Output full results as JSON')
    parser.add_argument('--list-files', action='store_true',
                        help='List all files with json_validation')
    parser.add_argument('--needs-repair', action='store_true',
                        help='List only files needing repair')
    parser.add_argument('--exclude-from-stats', action='store_true',
                        help='List files excluded from statistics')

    args = parser.parse_args()

    print("Analyzing json_validation structures...\n", file=sys.stderr)
    results = analyze_json_validation_structure()

    if args.json:
        # Convert defaultdicts to regular dicts for JSON serialization
        output = {
            'total_files_checked': results['total_files_checked'],
            'files_with_validation': results['files_with_validation'],
            'by_status': results['by_status'],
            'by_model': dict(results['by_model']),
            'by_judge': dict(results['by_judge']),
            'by_failure_type': dict(results['by_failure_type'])
        }
        print(json.dumps(output, indent=2))

    elif args.list_files:
        for file_path in results['files_with_validation']:
            print(file_path)

    elif args.needs_repair:
        for entry in results['by_status']['flagged_needs_repair']:
            print(entry['file_path'])

    elif args.exclude_from_stats:
        for entry in results['by_status']['excluded_from_stats']:
            print(f"{entry['file_path']} - {entry['model']} - Judge {entry['judge_number']}")

    else:
        print_report(results)


if __name__ == '__main__':
    main()
