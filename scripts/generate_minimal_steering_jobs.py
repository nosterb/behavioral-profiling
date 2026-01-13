#!/usr/bin/env python3
"""
Generate minimal_steering intervention jobs based on telemetryV3 template.
"""

import yaml
from pathlib import Path
import shutil

def generate_minimal_steering_jobs():
    """Generate minimal_steering jobs from telemetryV3 templates."""

    # Source and destination directories
    source_dir = Path('payload/single_prompt_jobs/all_suites_telemetryV3')
    dest_dir = Path('payload/single_prompt_jobs/all_suites_minimal_steering')

    # Create destination directory
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating minimal_steering jobs...")
    print(f"Source: {source_dir}")
    print(f"Destination: {dest_dir}")
    print()

    # Get all telemetryV3 job files
    telemetry_jobs = sorted(source_dir.glob('*.yaml'))

    generated = []

    for job_file in telemetry_jobs:
        # Load the job config
        with open(job_file) as f:
            config = yaml.safe_load(f)

        # Get the original filename parts
        filename = job_file.name
        # Replace telemetryV3 with minimal_steering in filename
        new_filename = filename.replace('telemetryV3', 'minimal_steering')

        # Update config fields
        config['request_id'] = config['request_id'].replace('telemetryV3', 'minimal_steering')
        config['metadata']['intervention'] = 'baseline_minimal_steering'
        config['prompt_file'] = 'payload/prompts/minimal_steering.txt'

        # Write new job file
        new_job_path = dest_dir / new_filename
        with open(new_job_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        generated.append(new_filename)

    print(f"✓ Generated {len(generated)} minimal_steering jobs")
    print()

    # Create job list YAML
    job_list_path = Path('payload/job_lists/minimal_steering_all.yaml')
    job_list = {
        'job_list_id': 'all_suites_baseline_minimal_steering',
        'description': f'All suites - baseline minimal steering ({len(generated)} jobs)',
        'jobs': [str(dest_dir / filename) for filename in generated]
    }

    with open(job_list_path, 'w') as f:
        yaml.dump(job_list, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Created job list: {job_list_path}")
    print(f"  Jobs: {len(generated)}")
    print()

    # Show breakdown by suite
    suites = {}
    for filename in generated:
        if 'affective' in filename:
            suite = 'affective'
        elif 'broad' in filename:
            suite = 'broad'
        elif 'dimensions' in filename:
            suite = 'dimensions'
        elif 'general' in filename:
            suite = 'general'
        else:
            suite = 'other'

        suites[suite] = suites.get(suite, 0) + 1

    print("Breakdown by suite:")
    for suite, count in sorted(suites.items()):
        print(f"  {suite}: {count} jobs")

    print()
    print("="*80)
    print("COMPLETE")
    print("="*80)
    print(f"Generated files: payload/single_prompt_jobs/all_suites_minimal_steering/")
    print(f"Job list: payload/job_lists/minimal_steering_all.yaml")
    print()
    print("To run all jobs:")
    print("  python3 scripts/run_jobs_parallel.py \\")
    print("    payload/job_lists/minimal_steering_all.yaml \\")
    print("    --max-parallel 3 \\")
    print("    --skip-behavioral-prompts")


if __name__ == '__main__':
    generate_minimal_steering_jobs()
