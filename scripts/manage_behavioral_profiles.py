#!/usr/bin/env python3
"""
Behavioral Profile Management CLI

Manage master behavioral profiles with incremental updates and undo.

Usage:
    # Add job to profiles
    python3 scripts/manage_behavioral_profiles.py add outputs/single_prompt_jobs/job_*.json

    # Remove job (undo)
    python3 scripts/manage_behavioral_profiles.py remove personality_warmth_baseline_20251210

    # Add all jobs from a directory
    python3 scripts/manage_behavioral_profiles.py add-all outputs/single_prompt_jobs/12_10_2025_personality_v6/

    # View current profiles
    python3 scripts/manage_behavioral_profiles.py status

    # List all contributions
    python3 scripts/manage_behavioral_profiles.py list

    # Reset all profiles
    python3 scripts/manage_behavioral_profiles.py reset --confirm
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.behavioral_profile_manager import BehavioralProfileManager


def cmd_add(args):
    """Add a job evaluation to profiles."""
    manager = BehavioralProfileManager(args.master_dir)

    job_file = Path(args.job_file)
    if not job_file.exists():
        print(f"Error: Job file not found: {job_file}")
        return 1

    # Extract job_id from filename or metadata
    job_id = job_file.stem

    print(f"Adding job: {job_id}")
    result = manager.add_job_evaluation(job_id, job_file, update_viz=not args.no_viz)

    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")

    if result['status'] == 'success' and result.get('models'):
        print(f"Updated models: {', '.join(result['models'])}")

    return 0 if result['status'] in ['success', 'skipped'] else 1


def cmd_remove(args):
    """Remove a job evaluation from profiles."""
    manager = BehavioralProfileManager(args.master_dir)

    print(f"Removing job: {args.job_id}")
    result = manager.remove_job_evaluation(args.job_id, update_viz=not args.no_viz)

    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")

    if result['status'] == 'success' and result.get('models'):
        print(f"Updated models: {', '.join(result['models'])}")

    return 0 if result['status'] == 'success' else 1


def cmd_add_all(args):
    """Add all job evaluations from a directory."""
    manager = BehavioralProfileManager(args.master_dir)

    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        return 1

    # Find all job JSON files
    job_files = sorted(directory.glob("job_*.json"))

    if not job_files:
        print(f"No job files found in {directory}")
        return 1

    print(f"Found {len(job_files)} job files")
    print()

    added = 0
    skipped = 0
    failed = 0

    for i, job_file in enumerate(job_files, 1):
        job_id = job_file.stem

        # Skip visualizations on all but last
        update_viz = (i == len(job_files)) and not args.no_viz

        result = manager.add_job_evaluation(job_id, job_file, update_viz=update_viz)

        if result['status'] == 'success':
            added += 1
            print(f"[{i}/{len(job_files)}] ✓ {job_id}")
        elif result['status'] == 'skipped':
            skipped += 1
            print(f"[{i}/{len(job_files)}] - {job_id} (skipped: {result['message']})")
        else:
            failed += 1
            print(f"[{i}/{len(job_files)}] ✗ {job_id} (error: {result['message']})")

    print()
    print(f"Summary: {added} added, {skipped} skipped, {failed} failed")

    # Generate visualizations if we skipped them during the loop
    if added > 0 and args.no_viz:
        print("\nSkipped visualization updates (use --viz to enable)")

    return 0


def cmd_status(args):
    """Show current profile status."""
    manager = BehavioralProfileManager(args.master_dir)

    summary = manager.get_profile_summary()

    if not summary:
        print("No profiles found")
        return 0

    print(f"Master Profile Directory: {manager.master_dir}")
    print(f"Total Models: {len(summary)}")
    print()

    # Sort by model name
    for model_name in sorted(summary.keys()):
        data = summary[model_name]
        print(f"Model: {model_name}")
        print(f"  Total Evaluations: {data['total_evaluations']}")
        print(f"  Last Updated: {data.get('last_updated', 'Never')}")

        if data['dimensions']:
            print(f"  Dimensions:")
            for dim, score in sorted(data['dimensions'].items()):
                print(f"    {dim}: {score:.2f}")
        print()

    return 0


def cmd_list(args):
    """List all job contributions."""
    manager = BehavioralProfileManager(args.master_dir)

    contributions = manager.list_contributions()

    if not contributions:
        print("No contributions found")
        return 0

    print(f"Total Contributions: {len(contributions)}")
    print()

    # Sort by timestamp (newest first)
    for contrib in sorted(contributions, key=lambda x: x['timestamp'], reverse=True):
        print(f"Job ID: {contrib['job_id']}")
        print(f"  Timestamp: {contrib['timestamp']}")
        print(f"  Models: {', '.join(contrib['models'])}")
        print()

    return 0


def cmd_reset(args):
    """Reset all profiles (requires confirmation)."""
    manager = BehavioralProfileManager(args.master_dir)

    if not args.confirm:
        print("Error: Reset requires --confirm flag")
        print("This will delete all profile data!")
        return 1

    import shutil

    # Backup first
    if args.backup:
        from datetime import datetime
        backup_dir = manager.master_dir.parent / f"behavioral_profiles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"Creating backup: {backup_dir}")
        shutil.copytree(manager.master_dir, backup_dir)

    # Remove profiles
    print(f"Resetting profiles in {manager.master_dir}")

    if manager.profiles_dir.exists():
        shutil.rmtree(manager.profiles_dir)
    if manager.history_dir.exists():
        shutil.rmtree(manager.history_dir)
    if manager.viz_dir.exists():
        shutil.rmtree(manager.viz_dir)

    print("✓ All profiles reset")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Manage master behavioral profiles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--master-dir',
        type=str,
        default='outputs/behavioral_profiles',
        help='Master profile directory (default: outputs/behavioral_profiles)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a job evaluation to profiles')
    add_parser.add_argument('job_file', help='Path to job JSON file')
    add_parser.add_argument('--no-viz', action='store_true', help='Skip visualization update')

    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a job evaluation (undo)')
    remove_parser.add_argument('job_id', help='Job ID to remove')
    remove_parser.add_argument('--no-viz', action='store_true', help='Skip visualization update')

    # Add-all command
    addall_parser = subparsers.add_parser('add-all', help='Add all jobs from a directory')
    addall_parser.add_argument('directory', help='Directory containing job JSON files')
    addall_parser.add_argument('--no-viz', action='store_true', help='Skip visualization updates')

    # Status command
    subparsers.add_parser('status', help='Show current profile status')

    # List command
    subparsers.add_parser('list', help='List all job contributions')

    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset all profiles')
    reset_parser.add_argument('--confirm', action='store_true', help='Confirm reset operation')
    reset_parser.add_argument('--backup', action='store_true', help='Create backup before reset')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    commands = {
        'add': cmd_add,
        'remove': cmd_remove,
        'add-all': cmd_add_all,
        'status': cmd_status,
        'list': cmd_list,
        'reset': cmd_reset
    }

    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
