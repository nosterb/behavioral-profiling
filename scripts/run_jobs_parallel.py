#!/usr/bin/env python3
"""
General-purpose parallel job runner for agent and batch jobs.

Usage:
    # From job list YAML
    python3 scripts/run_jobs_parallel.py payload/job_lists/my_jobs.yaml --max-parallel 3

    # Direct job files
    python3 scripts/run_jobs_parallel.py job1.yaml job2.yaml job3.yaml --max-parallel 2

    # With job range
    python3 scripts/run_jobs_parallel.py payload/job_lists/example_multi_provider.yaml --start 1 --end 12 --max-parallel 3

    # Background mode (saves output, returns immediately)
    python3 scripts/run_jobs_parallel.py payload/job_lists/my_jobs.yaml --background
"""

import os
import sys
import yaml
import subprocess
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "outputs" / "job_logs"

def prompt_batch_behavioral_analysis(num_jobs: int) -> dict:
    """
    Prompt user once for behavioral analysis settings for all jobs.

    Args:
        num_jobs: Total number of jobs that will be run

    Returns:
        Dictionary with personality settings: {
            'run_personality': bool,
            'chunking_strategy': str (e.g., 'n=1', 'n=4', 'n=turns:3'),
            'apply_to_profiles': bool
        }
    """
    print(f"\n{'='*70}")
    print(f"BATCH PERSONALITY ANALYSIS SETTINGS")
    print(f"{'='*70}")
    print(f"About to run {num_jobs} jobs.")
    print(f"You can configure behavioral analysis for all jobs now.")
    print(f"(Jobs with existing behavioral evaluations will be skipped)")
    print(f"{'='*70}\n")

    # Ask if user wants behavioral analysis for all jobs
    while True:
        response = input("Run behavioral analysis for all jobs after completion? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            break
        elif response in ['n', 'no']:
            print("→ Behavioral analysis disabled for this batch\n")
            return {
                'run_personality': False,
                'chunking_strategy': None,
                'apply_to_profiles': False
            }
        else:
            print("Please enter 'y' or 'n'")

    # Ask for chunking strategy
    print("\nDefault chunking strategy:")
    print("  1. n=1 (entire conversation as one - recommended)")
    print("  2. n=4 (split into 4 equal chunks)")
    print("  3. n=turns:3 (every 3 turns)")
    print()

    while True:
        choice = input("Choose default strategy [1-3, or press Enter for n=1]: ").strip()

        if not choice or choice == '1':
            chunking = 'n=1'
            break
        elif choice == '2':
            chunking = 'n=4'
            break
        elif choice == '3':
            chunking = 'n=turns:3'
            break
        else:
            print("Please enter 1, 2, or 3")

    print(f"→ Using chunking strategy: {chunking}")

    # Ask about profile application (will prompt again after all jobs complete)
    print("\nAfter all jobs complete, you'll be prompted to apply results to master profiles.")
    print()

    return {
        'run_personality': True,
        'chunking_strategy': chunking,
        'apply_to_profiles': True  # Will prompt again later
    }

def parse_chunking_strategy(chunking_str: str):
    """
    Parse chunking strategy string into ChunkingStrategy object.

    Args:
        chunking_str: String like 'n=1', 'n=4', 'n=turns:3'

    Returns:
        ChunkingStrategy object
    """
    sys.path.insert(0, str(PROJECT_ROOT / 'src'))
    from behavioral_prompt_handler import ChunkingStrategy

    if chunking_str == 'n=1':
        return ChunkingStrategy('none', None)
    elif chunking_str.startswith('n=turns:'):
        turns = int(chunking_str.split(':')[1])
        return ChunkingStrategy('turns', turns)
    elif chunking_str.startswith('n='):
        chunks = int(chunking_str.split('=')[1])
        return ChunkingStrategy('chunks', chunks)
    else:
        # Default to n=1
        return ChunkingStrategy('none', None)

def run_batch_behavioral_analysis(successful_jobs: list, personality_config: dict):
    """
    Run behavioral analysis on all successful jobs, then prompt for profile updates.

    Args:
        successful_jobs: List of successful job result dictionaries
        personality_config: Personality configuration from batch prompt
    """
    sys.path.insert(0, str(PROJECT_ROOT / 'src'))
    from behavioral_prompt_handler import (
        run_behavioral_analysis,
        get_job_info,
        check_if_behavioral_already_evaluated,
        prompt_for_profile_update
    )
    import json

    print(f"\n{'='*70}")
    print(f"BATCH PERSONALITY ANALYSIS")
    print(f"{'='*70}")
    print(f"Processing {len(successful_jobs)} successful jobs...")
    print(f"Strategy: {personality_config['chunking_strategy']}")
    print(f"{'='*70}\n")

    chunking = parse_chunking_strategy(personality_config['chunking_strategy'])
    staged_results = []

    # Process each successful job
    for i, job_result in enumerate(successful_jobs, 1):
        job_path = Path(job_result['output_json'])

        # Check if already evaluated
        try:
            with open(job_path, 'r') as f:
                job_data = json.load(f)
            if check_if_behavioral_already_evaluated(job_data):
                print(f"[{i}/{len(successful_jobs)}] {job_path.name}: already evaluated (skipping)")
                continue
        except Exception as e:
            print(f"[{i}/{len(successful_jobs)}] {job_path.name}: error checking status ({e})")
            continue

        # Run behavioral analysis
        try:
            print(f"[{i}/{len(successful_jobs)}] {job_path.name}: running analysis...")
            staged_path = run_behavioral_analysis(
                job_path,
                chunking,
                framework_config=None,
                staging_dir=None
            )
            staged_results.append(staged_path)
            print(f"  ✓ Staged: {staged_path.name}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Summary of staged results
    print(f"\n{'='*70}")
    print(f"PERSONALITY ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"Successfully analyzed: {len(staged_results)} jobs")
    print(f"Staged results: outputs/personality_staging/")
    print(f"{'='*70}\n")

    if not staged_results:
        print("No results to apply to master profiles.\n")
        return

    # Prompt to apply to master profiles
    print("You can now apply these results to master behavioral profiles.")
    print(f"This will update running averages for each model across all {len(staged_results)} jobs.\n")

    while True:
        response = input(f"Apply all {len(staged_results)} results to master profiles? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            break
        elif response in ['n', 'no']:
            print("→ Results remain staged (not applied to master profiles)")
            print("   You can apply them later using personality_profile_manager.py\n")
            return
        else:
            print("Please enter 'y' or 'n'")

    # Apply all staged results
    print(f"\n{'='*70}")
    print(f"APPLYING TO MASTER PROFILES")
    print(f"{'='*70}\n")

    from behavioral_prompt_handler import apply_to_master_profiles

    for i, staged_path in enumerate(staged_results, 1):
        try:
            print(f"[{i}/{len(staged_results)}] {staged_path.name}...")
            result = apply_to_master_profiles(staged_path)
            if result['status'] == 'success':
                print(f"  ✓ Updated: {', '.join(result['models'])}")
            else:
                print(f"  ⚠ {result['message']}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print(f"\n{'='*70}")
    print(f"PROFILE UPDATE COMPLETE")
    print(f"{'='*70}")
    print(f"Master profiles: outputs/behavioral_profiles/profiles/")
    print(f"Visualizations: outputs/behavioral_profiles/visualizations/")
    print(f"{'='*70}\n")

def load_job_list_yaml(yaml_path: str) -> List[str]:
    """Load job paths from YAML config."""
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    if 'jobs' in config:
        return config['jobs']
    else:
        raise ValueError("YAML must contain 'jobs' key with list of job paths")

def detect_job_type(job_path: Path) -> str:
    """Detect if job is batch, agent, or chat type."""
    # Check parent directory
    if 'single_prompt_jobs' in str(job_path):
        return 'batch'
    elif 'chat_jobs' in str(job_path):
        return 'chat'
    elif 'agent_jobs' in str(job_path):
        return 'agent'

    # Check job config content
    try:
        with open(job_path, 'r') as f:
            config = yaml.safe_load(f)
            if 'job_id' in config:
                return 'batch'
            elif config.get('simulation_type') == 'chat':
                return 'chat'
            elif 'request_id' in config or 'agent_profile' in config:
                return 'agent'
    except Exception:
        pass

    # Default to agent
    return 'agent'

def run_job(job_file: Path, job_num: int, total: int, log_to_file: bool = True, output_dir: Optional[str] = None) -> dict:
    """Run a single job and return results."""
    start_time = datetime.now()
    job_name = job_file.stem
    job_type = detect_job_type(job_file)

    # Select script based on job type
    if job_type == 'batch':
        script = 'src/batch_invoke.py'
    elif job_type == 'chat':
        script = 'src/chat_invoke.py'
    else:  # agent
        script = 'src/agent_invoke.py'

    # Create log file path
    if log_to_file:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / f"{job_name}_{start_time.strftime('%Y%m%d_%H%M%S')}.log"
    else:
        log_file = None

    print(f"[{start_time.strftime('%H:%M:%S')}] [{job_num}/{total}] Starting: {job_name} ({job_type})")

    # Build command (-u for unbuffered output so logs update in real-time)
    cmd = ["python3", "-u", script, str(job_file)]

    # Add output directory if specified (works for both batch and agent jobs)
    if output_dir:
        cmd.extend(['--output-dir', output_dir])

    try:
        if log_to_file:
            # Run with output to log file
            with open(log_file, 'w') as log:
                result = subprocess.run(
                    cmd,
                    cwd=PROJECT_ROOT,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    timeout=7200  # 2 hour timeout per job
                )
        else:
            # Run with output to stdout/stderr
            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                timeout=7200
            )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        if result.returncode == 0:
            print(f"[{end_time.strftime('%H:%M:%S')}] [{job_num}/{total}] ✓ {job_name} ({duration:.1f}s)")

            # Determine output JSON path based on job type
            if job_type == 'batch':
                output_json = PROJECT_ROOT / "outputs" / "single_prompt_jobs" / f"job_{job_name}.json"
            elif job_type == 'chat':
                output_json = PROJECT_ROOT / "outputs" / "chat_jobs" / "reports" / f"chat_job_{job_name}.json"
            else:  # agent
                output_json = PROJECT_ROOT / "outputs" / "agent_jobs" / "reports" / f"{job_name}.json"

            # Use custom output dir if specified
            if output_dir:
                output_json = Path(output_dir) / output_json.name

            return {
                'job': job_name,
                'path': str(job_file),
                'status': 'success',
                'duration': duration,
                'log': log_file,
                'output_json': str(output_json)
            }
        else:
            print(f"[{end_time.strftime('%H:%M:%S')}] [{job_num}/{total}] ✗ {job_name} (exit code {result.returncode})")
            return {
                'job': job_name,
                'path': str(job_file),
                'status': 'failed',
                'duration': duration,
                'exit_code': result.returncode,
                'log': log_file
            }

    except subprocess.TimeoutExpired:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{job_num}/{total}] ⏱ {job_name} (timeout)")
        return {
            'job': job_name,
            'path': str(job_file),
            'status': 'timeout',
            'log': log_file
        }

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{job_num}/{total}] ✗ {job_name} (error: {e})")
        return {
            'job': job_name,
            'path': str(job_file),
            'status': 'error',
            'error': str(e),
            'log': log_file
        }

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Run multiple jobs in parallel with proper parallelism control',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run jobs from YAML list
  %(prog)s payload/job_lists/my_jobs.yaml --max-parallel 3

  # Run specific jobs
  %(prog)s job1.yaml job2.yaml job3.yaml

  # Run subset of jobs from list
  %(prog)s payload/job_lists/example_multi_provider.yaml --start 1 --end 12

  # Run without saving logs (output to terminal)
  %(prog)s payload/job_lists/my_jobs.yaml --no-log

  # Run in background
  %(prog)s payload/job_lists/my_jobs.yaml --background
        """
    )

    parser.add_argument(
        'jobs',
        nargs='+',
        help='Job config files or YAML job list'
    )
    parser.add_argument(
        '--max-parallel',
        type=int,
        default=3,
        help='Maximum number of jobs to run in parallel (default: 3)'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=1,
        help='Start job number (1-indexed, for job lists only)'
    )
    parser.add_argument(
        '--end',
        type=int,
        default=None,
        help='End job number (1-indexed, for job lists only)'
    )
    parser.add_argument(
        '--no-log',
        action='store_true',
        help='Do not save logs, output to terminal instead'
    )
    parser.add_argument(
        '--background',
        action='store_true',
        help='Run in background (implies --no-log=False)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default=None,
        help='Custom output directory (passed to batch_invoke.py and agent_invoke.py)'
    )

    args = parser.parse_args()

    # Determine if first argument is a job list YAML or individual job
    if len(args.jobs) == 1 and 'job_lists' in args.jobs[0]:
        # Load from YAML job list
        job_paths = load_job_list_yaml(args.jobs[0])

        # Apply range filter
        if args.end is None:
            args.end = len(job_paths)

        job_paths = job_paths[args.start - 1:args.end]
        total_jobs = len(job_paths)
    else:
        # Use command line arguments directly
        job_paths = args.jobs
        total_jobs = len(job_paths)
        args.start = 1
        args.end = total_jobs

    # Validate job paths
    validated_jobs = []
    for path in job_paths:
        job_path = Path(path)
        if job_path.exists():
            validated_jobs.append(job_path)
        else:
            print(f"Warning: Job file not found: {path}")

    if not validated_jobs:
        print("Error: No valid job files found")
        sys.exit(1)

    # Print configuration
    print(f"\n{'='*70}")
    print(f"Parallel Job Runner")
    print(f"{'='*70}")
    print(f"Total jobs: {len(validated_jobs)} (#{args.start} to #{args.end} of {total_jobs})")
    print(f"Max parallel: {args.max_parallel}")

    if not args.no_log:
        print(f"Logs: {LOG_DIR}")
    else:
        print(f"Logs: disabled (output to terminal)")

    print(f"{'='*70}\n")

    # Check if jobs already have behavioral judge configured
    jobs_with_behavioral_judge = []
    for job_path in validated_jobs:
        try:
            with open(job_path, 'r') as f:
                import yaml
                job_config = yaml.safe_load(f)
                judge_config = job_config.get('judge', '')
                if isinstance(judge_config, str) and 'personality' in judge_config.lower():
                    jobs_with_behavioral_judge.append(job_path)
                elif isinstance(judge_config, dict):
                    # Check inline judge config
                    judge_prompt = judge_config.get('judge_prompt', '')
                    if 'personality' in str(judge_prompt).lower():
                        jobs_with_behavioral_judge.append(job_path)
        except:
            pass

    # Batch behavioral analysis prompt (skip if all jobs have behavioral judge)
    if len(jobs_with_behavioral_judge) == len(validated_jobs):
        print(f"✓ All jobs have behavioral judge configured in their config")
        print(f"  Personality evaluation will run automatically via chained judge")
        print(f"  Skipping batch behavioral prompt\n")
        personality_config = {'run_personality': False}
    else:
        if jobs_with_behavioral_judge:
            print(f"Note: {len(jobs_with_behavioral_judge)}/{len(validated_jobs)} jobs have behavioral judge configured")
            print(f"      Those will skip behavioral prompt automatically\n")
        personality_config = prompt_batch_behavioral_analysis(len(validated_jobs))

    start_time = datetime.now()
    results = []

    # Run jobs with thread pool
    with ThreadPoolExecutor(max_workers=args.max_parallel) as executor:
        futures = {
            executor.submit(
                run_job,
                job,
                i + args.start,
                total_jobs,
                log_to_file=not args.no_log,
                output_dir=args.output_dir
            ): job
            for i, job in enumerate(validated_jobs)
        }

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    # Print summary
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    success = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']
    timeout = [r for r in results if r['status'] == 'timeout']
    errors = [r for r in results if r['status'] == 'error']

    print(f"\n{'='*70}")
    print(f"Summary")
    print(f"{'='*70}")
    print(f"Total time: {total_duration / 60:.1f} minutes")
    print(f"Success: {len(success)}")
    print(f"Failed: {len(failed)}")
    print(f"Timeout: {len(timeout)}")
    print(f"Errors: {len(errors)}")

    if success and not failed and not timeout and not errors:
        avg_duration = sum(r['duration'] for r in success) / len(success)
        print(f"Average duration: {avg_duration:.1f}s")

    if failed:
        print(f"\nFailed jobs:")
        for r in failed:
            log_msg = f" - see {r['log']}" if r['log'] else ""
            print(f"  - {r['job']} (exit code {r['exit_code']}){log_msg}")

    if timeout:
        print(f"\nTimeout jobs:")
        for r in timeout:
            log_msg = f" - see {r['log']}" if r['log'] else ""
            print(f"  - {r['job']}{log_msg}")

    if errors:
        print(f"\nError jobs:")
        for r in errors:
            log_msg = f" - see {r['log']}" if r['log'] else ""
            print(f"  - {r['job']}: {r['error']}{log_msg}")

    print(f"{'='*70}\n")

    # Post-batch behavioral analysis (if enabled)
    if personality_config['run_personality'] and success:
        run_batch_behavioral_analysis(success, personality_config)

    sys.exit(0 if len(failed) + len(timeout) + len(errors) == 0 else 1)

if __name__ == '__main__':
    main()
