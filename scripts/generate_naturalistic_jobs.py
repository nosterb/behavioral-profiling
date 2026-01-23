#!/usr/bin/env python3
"""
Generate job YAML files from naturalistic queries.
Creates both standard (1-10) and behavior_50 (1-50) job variants.

Usage:
    python3 scripts/generate_naturalistic_jobs.py [--judge-config behavior]
    python3 scripts/generate_naturalistic_jobs.py --judge-config behavior_50
    python3 scripts/generate_naturalistic_jobs.py --both
"""

import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent


def generate_jobs(queries_path: Path, judge_config: str = "behavior") -> list:
    """Generate job files from queries JSON.

    Args:
        queries_path: Path to generated_queries.json
        judge_config: Judge config name (behavior or behavior_50)

    Returns:
        List of created job paths
    """
    with open(queries_path) as f:
        data = json.load(f)

    # Determine suffix based on judge config
    is_50_scale = "50" in judge_config
    suffix = "_50" if is_50_scale else ""
    condition_name = f"naturalistic{suffix}"

    output_dir = PROJECT_ROOT / f"payload/single_prompt_jobs/naturalistic_suite{suffix}"
    output_dir.mkdir(parents=True, exist_ok=True)

    job_paths = []

    for query_data in data["queries"]:
        base_id = query_data["query_id"]
        job_id = f"{base_id}{suffix}"

        job = {
            "request_id": job_id,
            "prompt": query_data["query"],
            "model_list": "model_config/all",
            "judge": f"payload/judge_configs/{judge_config}.yaml",
            "analytics": {
                "enabled": True,
                "export_chat": True
            },
            "max_job_retries": 5,
            "retry_config": {
                "max_retries": 3,
                "initial_timeout": 120,
                "backoff_multiplier": 2.0,
                "max_timeout": 300
            },
            "metadata": {
                "trait": "naturalistic",
                "scenario_id": query_data["query_id"].split("_")[1],
                "suite": f"naturalistic{suffix}",
                "topic": query_data["topic"],
                "category": query_data["category"],
                "generator_model": query_data["generator_model"],
                "condition": condition_name
            }
        }

        job_path = output_dir / f"{job_id}.yaml"
        with open(job_path, 'w') as f:
            yaml.dump(job, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        job_paths.append(str(job_path))

    # Create job list
    job_list = {
        "description": f"Naturalistic queries with {judge_config} judge ({len(job_paths)} jobs)",
        "total_jobs": len(job_paths),
        "condition": condition_name,
        "judge_config": judge_config,
        "generated": datetime.now().isoformat(),
        "jobs": job_paths
    }

    list_dir = PROJECT_ROOT / "payload" / "job_lists"
    list_dir.mkdir(parents=True, exist_ok=True)

    list_path = list_dir / f"naturalistic{suffix}.yaml"
    with open(list_path, 'w') as f:
        yaml.dump(job_list, f, default_flow_style=False, sort_keys=False)

    print(f"Created {len(job_paths)} jobs in {output_dir}")
    print(f"Job list saved to: {list_path}")

    return job_paths


def main():
    parser = argparse.ArgumentParser(description="Generate naturalistic job files")
    parser.add_argument("--judge-config", type=str, default="behavior",
                        help="Judge config name (behavior or behavior_50)")
    parser.add_argument("--both", action="store_true",
                        help="Generate jobs for both judge configs")
    parser.add_argument("--queries-file", type=Path, default=None,
                        help="Path to generated_queries.json")
    args = parser.parse_args()

    queries_path = args.queries_file or (PROJECT_ROOT / "payload" / "naturalistic" / "generated_queries.json")

    if not queries_path.exists():
        print(f"Error: Queries file not found: {queries_path}")
        print("Run generate_naturalistic_queries.py first")
        return 1

    print(f"\n{'='*60}")
    print("NATURALISTIC JOB GENERATION")
    print(f"{'='*60}")
    print(f"Queries file: {queries_path}")

    if args.both:
        print("\nGenerating jobs for behavior.yaml (1-10 scale)...")
        generate_jobs(queries_path, "behavior")

        print("\nGenerating jobs for behavior_50.yaml (1-50 scale)...")
        generate_jobs(queries_path, "behavior_50")
    else:
        print(f"\nGenerating jobs for {args.judge_config}.yaml...")
        generate_jobs(queries_path, args.judge_config)

    print(f"\n{'='*60}")
    print("COMPLETE")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    exit(main())
