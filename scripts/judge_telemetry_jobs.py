#!/usr/bin/env python3
"""
Run judge evaluations on all telemetry V3 jobs.

This script:
1. Finds all telemetry job files across all suites
2. Runs judge evaluation using behavior_telemetry.yaml config
3. Skips models with failed extraction (79 failures expected)
4. Stores results in 'judge_evaluation_telemetry' field
5. Uses 3 judges for Pass 1 (no comparative judge in Pass 2)
"""

import sys
import subprocess
from pathlib import Path
from collections import defaultdict

# Base directory
base_dir = Path('outputs/single_prompt_jobs')
suites = ['baseline_affective', 'baseline_broad', 'baseline_dimensions', 'baseline_general']

# Judge config
judge_config = 'payload/judge_configs/behavior_telemetry.yaml'

# Find all telemetry jobs
telemetry_jobs = []
for suite in suites:
    suite_dir = base_dir / suite
    if not suite_dir.exists():
        print(f"⚠️  Suite directory not found: {suite_dir}")
        continue

    # Find all telemetryV3 job files
    jobs = list(suite_dir.glob('*_telemetryV3_*/job_*_telemetryV3_*.json'))
    telemetry_jobs.extend([(suite, job) for job in jobs])

print(f"Found {len(telemetry_jobs)} telemetry jobs")
print(f"{'='*80}\n")

# Track statistics
stats = defaultdict(int)
failed_jobs = []

# Process each job
for i, (suite, job_path) in enumerate(telemetry_jobs, 1):
    job_name = job_path.stem
    print(f"[{i}/{len(telemetry_jobs)}] {suite}/{job_name}")

    # Run judge evaluation
    try:
        result = subprocess.run(
            ['python3', 'src/judge_invoke.py', judge_config, str(job_path)],
            capture_output=True,
            text=True,
            check=True
        )

        # Check output for success indicators
        if 'Evaluation Complete' in result.stdout or 'Evaluation Complete' in result.stderr:
            stats['success'] += 1
            print(f"  ✅ Complete")
        else:
            stats['unknown'] += 1
            print(f"  ⚠️  Unknown status")

        # Check for skipped models
        if 'Skipped' in result.stderr:
            import re
            match = re.search(r'Skipped (\d+) models', result.stderr)
            if match:
                skipped_count = int(match.group(1))
                stats['total_skipped'] += skipped_count
                print(f"  ℹ️  Skipped {skipped_count} models with failed extraction")

    except subprocess.CalledProcessError as e:
        stats['failed'] += 1
        failed_jobs.append((job_name, e.stderr))
        print(f"  ❌ Failed: {e.stderr[:100]}")

    print()

# Print summary
print(f"{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
print(f"Total jobs:          {len(telemetry_jobs)}")
print(f"Successful:          {stats['success']}")
print(f"Failed:              {stats['failed']}")
print(f"Unknown status:      {stats['unknown']}")
print(f"Total skipped models: {stats['total_skipped']}")
print(f"{'='*80}")

if failed_jobs:
    print("\nFailed jobs:")
    for job_name, error in failed_jobs:
        print(f"  - {job_name}")
        print(f"    Error: {error[:200]}")

print("\n✓ Judge evaluation complete for all telemetry jobs")
print(f"Results stored in 'judge_evaluation_telemetry' field")
