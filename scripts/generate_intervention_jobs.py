#!/usr/bin/env python3
"""
Generate intervention job files for all behavioral profiling suites.

For each baseline job, creates intervention variants:
- urgency (high-stakes time pressure)
- authority (expertise challenge)
- reminder (authenticity reminder)
- shake (competitive pressure framing)

Processes: broad_suite, affective_suite, general_suite, dimensions_suite
All intervention jobs use model_config/all for complete model coverage.
"""

import yaml
from pathlib import Path
from typing import Dict, List

# Intervention types and their prompt files
INTERVENTIONS = {
    'urgency': 'payload/prompts/urgency.txt',
    'authority': 'payload/prompts/authority.txt',
    'reminder': 'payload/prompts/reminder.txt',
    'shake': 'payload/prompts/shake.txt'
}

# Prompt sets to process
PROMPT_SETS = {
    'broad_suite': {
        'input_dir': 'payload/single_prompt_jobs/broad_suite',
        'output_base': 'payload/single_prompt_jobs',
        'job_list_base': 'payload/job_lists'
    },
    'affective_suite': {
        'input_dir': 'payload/single_prompt_jobs/affective_suite',
        'output_base': 'payload/single_prompt_jobs',
        'job_list_base': 'payload/job_lists'
    },
    'general_suite': {
        'input_dir': 'payload/single_prompt_jobs/general_suite',
        'output_base': 'payload/single_prompt_jobs',
        'job_list_base': 'payload/job_lists'
    },
    'dimensions_suite': {
        'input_dir': 'payload/single_prompt_jobs/dimensions_suite',
        'output_base': 'payload/single_prompt_jobs',
        'job_list_base': 'payload/job_lists'
    }
}


def read_job_file(job_path: Path) -> Dict:
    """Read YAML job file."""
    with open(job_path, 'r') as f:
        return yaml.safe_load(f)


def create_intervention_job(baseline_job: Dict, intervention_type: str,
                           prompt_file: str, output_path: Path) -> None:
    """
    Create intervention variant of baseline job.

    Args:
        baseline_job: Baseline job configuration
        intervention_type: Type of intervention (checkpoint, telemetry, reminder, shake)
        prompt_file: Path to intervention prompt file
        output_path: Where to write the new job file
    """
    # Copy baseline job
    intervention_job = baseline_job.copy()

    # Update job ID to include intervention type
    base_id = intervention_job.get('request_id', intervention_job.get('job_id', 'unknown'))
    intervention_job['request_id'] = f"{base_id}_{intervention_type}"

    # Add prompt_file for intervention
    intervention_job['prompt_file'] = prompt_file

    # Change model_list to use all models
    intervention_job['model_list'] = 'model_config/all'

    # Ensure analytics and export are enabled
    if 'analytics' not in intervention_job:
        intervention_job['analytics'] = {}
    intervention_job['analytics']['enabled'] = True
    intervention_job['analytics']['export_chat'] = True

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        yaml.dump(intervention_job, f, default_flow_style=False, sort_keys=False)

    print(f"  Created: {output_path.name}")


def process_prompt_set(prompt_set_name: str, config: Dict) -> Dict[str, List[str]]:
    """
    Process all baseline jobs in a prompt set, creating intervention variants.

    Returns:
        Dictionary mapping intervention type to list of job file paths
    """
    input_dir = Path(config['input_dir'])
    output_base = Path(config['output_base'])

    # Find all baseline YAML files
    baseline_jobs = sorted(input_dir.glob('*.yaml'))

    if not baseline_jobs:
        print(f"\n⚠ No baseline jobs found in {input_dir}")
        return {}

    print(f"\nProcessing {prompt_set_name}: {len(baseline_jobs)} baseline jobs")
    print(f"{'='*80}")

    # Track generated job paths by intervention type
    intervention_jobs = {intervention_type: [] for intervention_type in INTERVENTIONS.keys()}

    # Process each baseline job
    for baseline_path in baseline_jobs:
        baseline_job = read_job_file(baseline_path)
        baseline_name = baseline_path.stem

        print(f"\n{baseline_name}:")

        # Create each intervention variant
        for intervention_type, prompt_file in INTERVENTIONS.items():
            # Determine output directory and filename
            output_dir = output_base / f"{prompt_set_name}_{intervention_type}"
            output_filename = f"{baseline_name}_{intervention_type}.yaml"
            output_path = output_dir / output_filename

            # Create intervention job
            create_intervention_job(baseline_job, intervention_type, prompt_file, output_path)

            # Track relative path for job list
            relative_path = f"{output_dir.relative_to(Path('.'))}/{output_filename}"
            intervention_jobs[intervention_type].append(relative_path)

    return intervention_jobs


def create_job_lists(prompt_set_name: str, config: Dict,
                    intervention_jobs: Dict[str, List[str]]) -> None:
    """
    Create job list files for each intervention type.

    Args:
        prompt_set_name: Name of prompt set (e.g., 'personality_v2')
        config: Prompt set configuration
        intervention_jobs: Dictionary mapping intervention type to job file paths
    """
    job_list_base = Path(config['job_list_base'])
    job_list_base.mkdir(parents=True, exist_ok=True)

    print(f"\nCreating job lists for {prompt_set_name}:")
    print(f"{'='*80}")

    for intervention_type, job_paths in intervention_jobs.items():
        if not job_paths:
            continue

        # Create job list YAML
        job_list_data = {
            'job_list_id': f"{prompt_set_name}_{intervention_type}",
            'description': f"{prompt_set_name} with {intervention_type} intervention (model_config/all)",
            'jobs': job_paths
        }

        job_list_path = job_list_base / f"{prompt_set_name}_{intervention_type}.yaml"

        with open(job_list_path, 'w') as f:
            yaml.dump(job_list_data, f, default_flow_style=False, sort_keys=False)

        print(f"  ✓ {job_list_path.name} ({len(job_paths)} jobs)")


def main():
    print("="*80)
    print("INTERVENTION JOB GENERATOR")
    print("="*80)
    print("\nGenerating intervention variants (checkpoint, telemetry, reminder, shake)")
    print("for v2, love, and typical prompt sets.")
    print("\nAll intervention jobs will use model_config/all for complete coverage.")
    print("="*80)

    total_jobs_created = 0

    # Process each prompt set
    for prompt_set_name, config in PROMPT_SETS.items():
        intervention_jobs = process_prompt_set(prompt_set_name, config)

        if intervention_jobs:
            create_job_lists(prompt_set_name, config, intervention_jobs)

            # Count total jobs
            for job_list in intervention_jobs.values():
                total_jobs_created += len(job_list)

    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total intervention jobs created: {total_jobs_created}")
    print(f"Job lists created: {len(PROMPT_SETS) * len(INTERVENTIONS)}")
    print()
    print("Next steps:")
    print("1. Review generated job files in payload/single_prompt_jobs/")
    print("2. Review job lists in payload/job_lists/")
    print("3. Run intervention jobs with:")
    print("   python3 scripts/run_jobs_parallel.py payload/job_lists/<job_list>.yaml --max-parallel 3")
    print()


if __name__ == '__main__':
    main()
