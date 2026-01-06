#!/usr/bin/env python3
"""
Retroactively update behavioral profiles from completed jobs.

Useful when:
- Jobs failed to update profiles during run
- Parallel job runs were interrupted
- Need to rebuild profiles from scratch
- Want to add old jobs to profiles
"""

import sys
import argparse
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from behavioral_profile_manager import BehavioralProfileManager
import json


def find_jobs(job_path: Path, recursive: bool = False) -> list:
    """Find all job JSON files in a path."""
    jobs = []

    if job_path.is_file():
        # Single file
        if job_path.suffix == '.json':
            jobs.append(job_path)
    elif job_path.is_dir():
        # Directory
        if recursive:
            jobs = list(job_path.rglob("*.json"))
        else:
            jobs = list(job_path.glob("*.json"))

    # Filter to only job files (not other JSON files)
    jobs = [j for j in jobs if j.stem.startswith('job_') or j.stem.startswith('chat_job_')]

    return sorted(jobs)


def main():
    parser = argparse.ArgumentParser(
        description='Retroactively update behavioral profiles from completed jobs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add all jobs from a directory
  %(prog)s outputs/single_prompt_jobs/12_16_2025_personality_v2/

  # Add specific job file
  %(prog)s outputs/single_prompt_jobs/12_16_2025_personality_v2/job_batch_20251216_205725.json

  # Add jobs recursively from all subdirectories
  %(prog)s outputs/single_prompt_jobs/ --recursive

  # Force re-add jobs (skip duplicate check)
  %(prog)s outputs/single_prompt_jobs/12_16_2025_personality_v2/ --force

  # Dry run (show what would be added without making changes)
  %(prog)s outputs/single_prompt_jobs/12_16_2025_personality_v2/ --dry-run
        """
    )

    parser.add_argument(
        'job_path',
        type=Path,
        help='Path to job file or directory containing job files'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Recursively search subdirectories for job files'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force re-add jobs even if already processed (updates profiles)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be added without making changes'
    )
    parser.add_argument(
        '--profile-dir',
        type=Path,
        default=Path('outputs/behavioral_profiles'),
        help='Personality profiles directory (default: outputs/behavioral_profiles)'
    )
    parser.add_argument(
        '--skip-viz',
        action='store_true',
        help='Skip visualization updates (faster, update manually later)'
    )

    args = parser.parse_args()

    # Validate input path
    if not args.job_path.exists():
        print(f"✗ Error: Path not found: {args.job_path}")
        sys.exit(1)

    # Find job files
    print(f"Searching for job files in: {args.job_path}")
    if args.recursive:
        print("  (recursive search enabled)")

    jobs = find_jobs(args.job_path, args.recursive)

    if not jobs:
        print(f"✗ No job files found")
        sys.exit(1)

    print(f"Found {len(jobs)} job files\n")

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made\n")

    # Initialize manager
    manager = BehavioralProfileManager(args.profile_dir)

    # Process each job
    updated_count = 0
    skipped_count = 0
    error_count = 0
    updated_models = set()

    for i, job_file in enumerate(jobs, 1):
        # Extract job_id
        try:
            with open(job_file) as f:
                job_data = json.load(f)

            # Try multiple locations for job_id
            job_id = (
                job_data.get('job_metadata', {}).get('job_id') or
                job_data.get('job_metadata', {}).get('request_id') or
                job_data.get('metadata', {}).get('scenario_id') or
                job_file.stem
            )

            # Check if has behavioral evaluation
            has_eval = (
                'judge_evaluation' in job_data or
                'personality_evaluation' in job_data
            )

            if not has_eval:
                print(f"[{i}/{len(jobs)}] {job_id}")
                print(f"  ⊘ No behavioral evaluation in job (skipping)")
                skipped_count += 1
                continue

        except Exception as e:
            print(f"[{i}/{len(jobs)}] {job_file.name}")
            print(f"  ✗ Error reading job: {e}")
            error_count += 1
            continue

        print(f"[{i}/{len(jobs)}] {job_id}")

        # Dry run - just report what would happen
        if args.dry_run:
            if job_id in manager.contributions['job_contributions']:
                print(f"  → Would skip (already processed)")
            else:
                print(f"  → Would add to profiles")
            continue

        # Check if already processed
        if not args.force and job_id in manager.contributions['job_contributions']:
            print(f"  ⊘ Already processed (use --force to re-add)")
            skipped_count += 1
            continue

        # Add to profiles
        try:
            result = manager.add_job_evaluation(
                job_id,
                job_file,
                update_viz=False  # Update viz once at end
            )

            if result['status'] == 'success':
                print(f"  ✓ Added: {', '.join(result['models'])}")
                updated_models.update(result['models'])
                updated_count += 1
            elif result['status'] == 'skipped':
                print(f"  ⊘ {result['message']}")
                skipped_count += 1
            else:
                print(f"  ✗ {result['message']}")
                error_count += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            error_count += 1

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Total jobs found: {len(jobs)}")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Errors: {error_count}")

    if args.dry_run:
        print(f"\nDRY RUN - No changes were made")
        sys.exit(0)

    # Update visualizations
    if updated_models and not args.skip_viz:
        print(f"\n{'='*70}")
        print(f"UPDATING VISUALIZATIONS")
        print(f"{'='*70}")
        print(f"Regenerating for {len(updated_models)} models...")
        manager._generate_visualizations()
        print(f"✓ Visualizations updated")
    elif updated_models and args.skip_viz:
        print(f"\nSkipped visualization update (use --skip-viz=false to enable)")
        print(f"To update manually, run: python3 -c 'from pathlib import Path; import sys; sys.path.insert(0, \"src\"); from behavioral_profile_manager import BehavioralProfileManager; BehavioralProfileManager(Path(\"outputs/behavioral_profiles\"))._generate_visualizations()'")

    if updated_models:
        print(f"\n✓ Successfully updated profiles for {len(updated_models)} models:")
        for model in sorted(updated_models):
            print(f"  - {model}")
    else:
        print(f"\nNo profiles were updated")

    print(f"\nMaster profiles: {args.profile_dir}")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
