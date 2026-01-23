#!/usr/bin/env python3
"""
Run judge evaluation with randomly selected judges.

Constraints:
- Selects 3 judges from model_config/judges_random
- At least 1 must be high or low sophistication (from baseline classification)
- Not all 3 can be Claude models (provider diversity)
- Results appended with key 'judge_evaluation_random'
"""

import sys
import json
import random
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from model_providers import create_provider, parse_model_config
from batch_invoke import parse_model_list


def load_sophistication_classifications(classification_path: Path) -> dict:
    """Load model classifications from median split JSON."""
    with open(classification_path) as f:
        data = json.load(f)

    classifications = {}
    for model in data['models']:
        # Normalize name for matching
        name = model['display_name'].replace(' (Thinking)', '-Thinking')
        classifications[name.lower()] = model['classification']

    return classifications


def parse_judges_file(judges_path: Path) -> list:
    """Parse judges_random file and return list of judge configs."""
    judges = parse_model_list(judges_path)

    # Add provider classification
    for judge in judges:
        display_name = judge.get('display_name', '')
        judge['is_claude'] = 'claude' in display_name.lower() if display_name else False

    return judges


def classify_judges(judges: list, classifications: dict) -> dict:
    """Classify judges as high/low/unknown sophistication."""
    for judge in judges:
        display_name = judge.get('display_name', '')
        # Try various name normalizations
        name_variants = [
            display_name.lower(),
            display_name.lower().replace('-thinking', ''),
            display_name.lower().replace(' ', '-'),
        ]

        judge['sophistication'] = 'unknown'
        for variant in name_variants:
            if variant in classifications:
                judge['sophistication'] = classifications[variant]
                break

    return judges


def select_random_judges(judges: list, num_judges: int = 3, seed: int = None) -> list:
    """
    Select random judges with constraints:
    - At least 1 high or low sophistication
    - Not all Claude models
    """
    if seed is not None:
        random.seed(seed)

    # Separate by sophistication and provider
    high_low = [j for j in judges if j['sophistication'] in ['High-Sophistication', 'Low-Sophistication']]
    non_claude = [j for j in judges if not j['is_claude']]

    max_attempts = 100
    for attempt in range(max_attempts):
        selected = random.sample(judges, min(num_judges, len(judges)))

        # Check constraints
        has_classified = any(j['sophistication'] in ['High-Sophistication', 'Low-Sophistication'] for j in selected)
        all_claude = all(j['is_claude'] for j in selected)

        if has_classified and not all_claude:
            return selected

        # If we can't find valid selection, try forcing constraints
        if attempt == max_attempts - 1:
            print("Warning: Could not find selection meeting all constraints, forcing...")
            # Force at least one classified model
            if high_low:
                selected[0] = random.choice(high_low)
            # Force at least one non-Claude
            if non_claude and all_claude:
                for i, j in enumerate(selected):
                    if j['is_claude']:
                        selected[i] = random.choice(non_claude)
                        break
            return selected

    return selected


def run_judge_evaluation(job_path: Path, judges: list, output_key: str = 'judge_evaluation_random'):
    """Run judge evaluation on a job file with specified judges."""

    # Load job data
    with open(job_path) as f:
        job_data = json.load(f)

    # Check if already has this evaluation
    if output_key in job_data:
        print(f"  Skipping {job_path.name} - already has {output_key}")
        return False

    # Import judge evaluation functions
    from judge_invoke import (
        extract_model_data,
        evaluate_model,
        comparative_analysis,
        DEFAULT_SYSTEM_PROMPT
    )

    # Load judge config
    judge_config_path = PROJECT_ROOT / 'payload' / 'judge_configs' / 'behavior.yaml'
    import yaml
    with open(judge_config_path) as f:
        judge_config = yaml.safe_load(f)

    judge_prompt = judge_config.get('prompt', '')

    # Extract model data
    model_data_list = extract_model_data(job_data)

    if not model_data_list:
        print(f"  No model data found in {job_path.name}")
        return False

    # Run Pass 1: Individual evaluations with each judge
    evaluations = []

    for model_data in model_data_list:
        model_label = model_data.get('model_id', 'unknown')
        model_eval = {
            'model_id': model_label,
            'display_name': model_data.get('display_name', model_label),
            'pass1_judges': []
        }

        for j, judge in enumerate(judges, 1):
            print(f"    Judge {j}/{len(judges)}: {judge['display_name']} evaluating {model_label[:30]}...")

            try:
                # Create provider for this judge
                provider = create_provider(
                    provider_type=judge['provider'],
                    model_id=judge['model_id'],
                    display_name=judge['display_name']
                )

                evaluation = evaluate_model(
                    provider, judge, model_data, judge_prompt, model_label
                )
                evaluation['judge_model'] = judge['model_id']
                evaluation['judge_display_name'] = judge['display_name']
                evaluation['judge_sophistication'] = judge['sophistication']
                model_eval['pass1_judges'].append(evaluation)

            except Exception as e:
                print(f"      Error with judge {judge['display_name']}: {e}")
                model_eval['pass1_judges'].append({
                    'judge_model': judge['model_id'],
                    'judge_display_name': judge['display_name'],
                    'error': str(e)
                })

        evaluations.append(model_eval)

    # Run Pass 2: Comparative analysis (using first judge)
    comp_judge = judges[0]
    try:
        comp_provider = create_provider(
            provider_type=comp_judge['provider'],
            model_id=comp_judge['model_id'],
            display_name=comp_judge['display_name']
        )

        comparative = comparative_analysis(
            judge_provider=comp_provider,
            judge_config=comp_judge,
            evaluations=evaluations,
            judge_prompt=judge_prompt,
            reveal_names=True
        )
    except Exception as e:
        print(f"    Comparative pass error: {e}")
        comparative = {'error': str(e)}

    # Build result structure
    result = {
        'judge_metadata': {
            'timestamp': datetime.now().isoformat(),
            'judges': [
                {
                    'model_id': j['model_id'],
                    'display_name': j['display_name'],
                    'sophistication': j['sophistication'],
                    'is_claude': j['is_claude']
                }
                for j in judges
            ],
            'selection_method': 'random_with_constraints',
            'constraints': {
                'min_classified': 1,
                'max_same_provider': 2
            }
        },
        'evaluations': evaluations,
        'comparative_analysis': comparative
    }

    # Append to job data
    job_data[output_key] = result

    # Save
    with open(job_path, 'w') as f:
        json.dump(job_data, f, indent=2)

    print(f"  Saved {output_key} to {job_path.name}")
    return True


def find_naturalistic_jobs(jobs_dir: Path) -> list:
    """Find all naturalistic (non-50) job files."""
    jobs = []

    for job_dir in jobs_dir.iterdir():
        if not job_dir.is_dir():
            continue
        if 'naturalistic' not in job_dir.name:
            continue
        if '_50' in job_dir.name:  # Skip 1-50 scale jobs
            continue

        # Find JSON file in directory
        json_files = list(job_dir.glob('*.json'))
        if json_files:
            jobs.append(json_files[0])

    return sorted(jobs)


def main():
    parser = argparse.ArgumentParser(
        description='Run random judge evaluation on naturalistic jobs'
    )
    parser.add_argument(
        '--seed', type=int, default=None,
        help='Random seed for reproducibility (default: time-based)'
    )
    parser.add_argument(
        '--num-judges', type=int, default=3,
        help='Number of judges to select (default: 3)'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Show selected judges without running evaluation'
    )
    parser.add_argument(
        '--output-key', type=str, default='judge_evaluation_random',
        help='Key name for storing results (default: judge_evaluation_random)'
    )
    parser.add_argument(
        '--max-jobs', type=int, default=None,
        help='Maximum number of jobs to process'
    )

    args = parser.parse_args()

    # Paths
    judges_path = PROJECT_ROOT / 'model_config' / 'judges_random'
    classification_path = PROJECT_ROOT / 'outputs' / 'behavioral_profiles' / 'baseline' / 'median_split_classification.json'
    jobs_dir = PROJECT_ROOT / 'outputs' / 'single_prompt_jobs'

    # Load and classify judges
    print("Loading judges from model_config/judges_random...")
    judges = parse_judges_file(judges_path)
    print(f"  Found {len(judges)} judges")

    print("\nLoading sophistication classifications...")
    classifications = load_sophistication_classifications(classification_path)
    judges = classify_judges(judges, classifications)

    # Count by classification
    high = sum(1 for j in judges if j['sophistication'] == 'High-Sophistication')
    low = sum(1 for j in judges if j['sophistication'] == 'Low-Sophistication')
    unknown = sum(1 for j in judges if j['sophistication'] == 'unknown')
    print(f"  High: {high}, Low: {low}, Unknown: {unknown}")

    # Select random judges
    print(f"\nSelecting {args.num_judges} random judges (seed={args.seed})...")
    selected = select_random_judges(judges, args.num_judges, args.seed)

    print("\nSelected judges:")
    for i, j in enumerate(selected, 1):
        print(f"  {i}. {j['display_name']} ({j['sophistication']}) - Claude: {j['is_claude']}")

    # Verify constraints
    has_classified = any(j['sophistication'] in ['High-Sophistication', 'Low-Sophistication'] for j in selected)
    all_claude = all(j['is_claude'] for j in selected)
    print(f"\nConstraints: has_classified={has_classified}, all_claude={all_claude}")

    if not has_classified:
        print("ERROR: No high/low sophistication judge selected!")
        sys.exit(1)
    if all_claude:
        print("ERROR: All judges are Claude models!")
        sys.exit(1)

    if args.dry_run:
        print("\nDry run - not running evaluations")
        return

    # Find naturalistic jobs
    print("\nFinding naturalistic jobs...")
    jobs = find_naturalistic_jobs(jobs_dir)
    print(f"  Found {len(jobs)} naturalistic jobs")

    if args.max_jobs:
        jobs = jobs[:args.max_jobs]
        print(f"  Processing first {args.max_jobs} jobs")

    # Run evaluations
    print(f"\nRunning judge evaluations with key '{args.output_key}'...")
    success = 0
    skipped = 0
    errors = 0

    for i, job_path in enumerate(jobs, 1):
        print(f"\n[{i}/{len(jobs)}] {job_path.parent.name}")
        try:
            result = run_judge_evaluation(job_path, selected, args.output_key)
            if result:
                success += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total jobs: {len(jobs)}")
    print(f"Success: {success}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    print(f"\nResults saved with key: {args.output_key}")


if __name__ == '__main__':
    main()
