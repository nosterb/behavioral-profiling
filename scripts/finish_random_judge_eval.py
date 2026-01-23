#!/usr/bin/env python3
"""
Finish random judge evaluation using the EXACT judges from the original run.
Supports --max-parallel for concurrent job processing.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from model_providers import create_provider
from judge_invoke import extract_model_data, evaluate_model, comparative_analysis
import yaml

# Exact judges from the original run (verified from job_naturalistic_03)
JUDGES = [
    {
        'provider': 'bedrock',
        'model_id': 'us.anthropic.claude-sonnet-4-5-20250929-v1:0',
        'display_name': 'Claude-4.5-Sonnet-Thinking',
        'sophistication': 'unknown',
        'is_claude': True
    },
    {
        'provider': 'grok',
        'model_id': 'grok-4-0709',
        'display_name': 'Grok-4-0709',
        'sophistication': 'High-Sophistication',
        'is_claude': False
    },
    {
        'provider': 'bedrock',
        'model_id': 'us.anthropic.claude-haiku-4-5-20251001-v1:0',
        'display_name': 'Claude-4.5-Haiku',
        'sophistication': 'High-Sophistication',
        'is_claude': True
    },
]


def run_judge_evaluation(job_path: Path, judges: list, output_key: str = 'judge_evaluation_random'):
    """Run judge evaluation on a job file."""
    with open(job_path) as f:
        job_data = json.load(f)

    if output_key in job_data:
        print(f"  Skipping {job_path.name} - already has {output_key}")
        return False

    judge_config_path = PROJECT_ROOT / 'payload' / 'judge_configs' / 'behavior.yaml'
    with open(judge_config_path) as f:
        judge_config = yaml.safe_load(f)

    judge_prompt = judge_config.get('prompt', '')
    model_data_list = extract_model_data(job_data)

    if not model_data_list:
        print(f"  No model data found in {job_path.name}")
        return False

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

    # Pass 2: Comparative analysis
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
            'selection_method': 'hardcoded_from_original_run',
        },
        'evaluations': evaluations,
        'comparative_analysis': comparative
    }

    job_data[output_key] = result

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
        if '_50' in job_dir.name:
            continue
        json_files = list(job_dir.glob('*.json'))
        if json_files:
            jobs.append(json_files[0])
    return sorted(jobs)


def process_job(job_path: Path, job_index: int, total_jobs: int) -> tuple:
    """Process a single job. Returns (job_name, success, error_msg)."""
    job_name = job_path.parent.name
    print(f"\n[{job_index}/{total_jobs}] {job_name}")
    try:
        result = run_judge_evaluation(job_path, JUDGES)
        return (job_name, result, None)
    except Exception as e:
        print(f"  ERROR: {e}")
        return (job_name, False, str(e))


def main():
    parser = argparse.ArgumentParser(description='Finish random judge eval with exact judges')
    parser.add_argument('--max-parallel', type=int, default=1, help='Max parallel jobs (default: 1)')
    parser.add_argument('--dry-run', action='store_true', help='Show jobs without running')
    args = parser.parse_args()

    jobs_dir = PROJECT_ROOT / 'outputs' / 'single_prompt_jobs'

    print("Using exact judges from original run:")
    for i, j in enumerate(JUDGES, 1):
        print(f"  {i}. {j['display_name']} ({j['sophistication']})")

    print("\nFinding naturalistic jobs...")
    jobs = find_naturalistic_jobs(jobs_dir)
    print(f"  Found {len(jobs)} naturalistic jobs")

    # Filter to jobs needing evaluation
    needs_eval = []
    for job_path in jobs:
        with open(job_path) as f:
            data = json.load(f)
        if 'judge_evaluation_random' not in data:
            needs_eval.append(job_path)

    print(f"  {len(needs_eval)} jobs need evaluation")

    if not needs_eval:
        print("\nAll jobs already have judge_evaluation_random!")
        return

    print("\nJobs to evaluate:")
    for j in needs_eval:
        print(f"  {j.parent.name}")

    if args.dry_run:
        print("\n--dry-run: Not running evaluations")
        return

    print(f"\nRunning judge evaluations (max-parallel={args.max_parallel})...")
    success = 0
    errors = 0
    error_jobs = []

    if args.max_parallel == 1:
        for i, job_path in enumerate(needs_eval, 1):
            job_name, result, error = process_job(job_path, i, len(needs_eval))
            if result:
                success += 1
            elif error:
                errors += 1
                error_jobs.append((job_name, error))
    else:
        with ThreadPoolExecutor(max_workers=args.max_parallel) as executor:
            futures = {
                executor.submit(process_job, job_path, i, len(needs_eval)): job_path
                for i, job_path in enumerate(needs_eval, 1)
            }
            for future in as_completed(futures):
                job_name, result, error = future.result()
                if result:
                    success += 1
                elif error:
                    errors += 1
                    error_jobs.append((job_name, error))

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Success: {success}")
    print(f"Errors: {errors}")
    if error_jobs:
        print("\nFailed jobs:")
        for job_name, error in error_jobs:
            print(f"  {job_name}: {error}")


if __name__ == '__main__':
    main()
