#!/usr/bin/env python3
"""
Complete naturalistic queries evaluation pipeline.

Phases:
1. Generate queries from topics (seeded randomization)
2. Create job files for both judge configs
3. Run model evaluations
4. Aggregate profiles for new conditions
5. Run H1/H2 analysis

Usage:
    python3 scripts/run_naturalistic_pipeline.py [--seed 42] [--num-queries 20]
    python3 scripts/run_naturalistic_pipeline.py --skip-generation
    python3 scripts/run_naturalistic_pipeline.py --only-aggregate
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent


def run_command(cmd: list, description: str, cwd: Path = None) -> bool:
    """Run a command and handle errors."""
    print(f"\n  Running: {' '.join(str(c) for c in cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            check=True,
            capture_output=False
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR in {description}: {e}")
        return False
    except FileNotFoundError as e:
        print(f"  ERROR: Command not found: {e}")
        return False


def phase_1_generate_queries(seed: int, num_queries: int) -> bool:
    """Generate naturalistic queries from topics."""
    print(f"\n{'='*70}")
    print("PHASE 1: QUERY GENERATION")
    print(f"{'='*70}")
    print(f"Seed: {seed}")
    print(f"Number of queries: {num_queries}")

    return run_command(
        ["python3", "scripts/generate_naturalistic_queries.py",
         "--seed", str(seed),
         "--num-queries", str(num_queries)],
        "query generation"
    )


def phase_2_generate_jobs() -> bool:
    """Generate job YAML files for both judge configs."""
    print(f"\n{'='*70}")
    print("PHASE 2: JOB GENERATION")
    print(f"{'='*70}")

    return run_command(
        ["python3", "scripts/generate_naturalistic_jobs.py", "--both"],
        "job generation"
    )


def phase_3_run_evaluations(max_parallel: int = 3) -> bool:
    """Run model evaluations for both tracks."""
    print(f"\n{'='*70}")
    print("PHASE 3: MODEL EVALUATION")
    print(f"{'='*70}")

    # Run Track A (1-10 scale)
    print("\n--- Track A: 1-10 scale evaluation ---")
    success_a = run_command(
        ["python3", "scripts/run_jobs_parallel.py",
         "payload/job_lists/naturalistic.yaml",
         "--max-parallel", str(max_parallel),
         "--skip-behavioral-prompts"],
        "1-10 scale evaluation"
    )

    # Run Track B (1-50 scale)
    print("\n--- Track B: 1-50 scale evaluation ---")
    success_b = run_command(
        ["python3", "scripts/run_jobs_parallel.py",
         "payload/job_lists/naturalistic_50.yaml",
         "--max-parallel", str(max_parallel),
         "--skip-behavioral-prompts"],
        "1-50 scale evaluation"
    )

    return success_a and success_b


def phase_4_aggregate_profiles() -> bool:
    """Aggregate profiles for new conditions."""
    print(f"\n{'='*70}")
    print("PHASE 4: PROFILE AGGREGATION")
    print(f"{'='*70}")

    # Aggregate naturalistic (1-10)
    print("\n--- Aggregating naturalistic condition (1-10) ---")
    success_a = run_command(
        ["python3", "scripts/update_behavioral_profiles.py",
         "outputs/single_prompt_jobs", "--recursive",
         "--condition", "naturalistic",
         "--profile-dir", "outputs/behavioral_profiles/naturalistic"],
        "naturalistic aggregation"
    )

    # Aggregate naturalistic_50 (1-50)
    print("\n--- Aggregating naturalistic_50 condition (1-50) ---")
    success_b = run_command(
        ["python3", "scripts/update_behavioral_profiles.py",
         "outputs/single_prompt_jobs", "--recursive",
         "--condition", "naturalistic_50",
         "--profile-dir", "outputs/behavioral_profiles/naturalistic_50"],
        "naturalistic_50 aggregation"
    )

    return success_a and success_b


def phase_5_run_analysis() -> bool:
    """Run H1/H2 analysis on new conditions."""
    print(f"\n{'='*70}")
    print("PHASE 5: H1/H2 ANALYSIS")
    print(f"{'='*70}")

    # Run analysis for naturalistic
    print("\n--- Running H1/H2 analysis for naturalistic ---")
    success_a = run_command(
        ["./scripts/run_complete_h1_h2_analysis.sh", "naturalistic"],
        "naturalistic H1/H2 analysis"
    )

    # Run analysis for naturalistic_50
    print("\n--- Running H1/H2 analysis for naturalistic_50 ---")
    success_b = run_command(
        ["./scripts/run_complete_h1_h2_analysis.sh", "naturalistic_50"],
        "naturalistic_50 H1/H2 analysis"
    )

    return success_a and success_b


def main():
    parser = argparse.ArgumentParser(
        description="Run naturalistic queries evaluation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Full pipeline with default settings
    python3 scripts/run_naturalistic_pipeline.py

    # Custom seed and query count
    python3 scripts/run_naturalistic_pipeline.py --seed 123 --num-queries 30

    # Skip query generation (use existing queries)
    python3 scripts/run_naturalistic_pipeline.py --skip-generation

    # Only run aggregation and analysis (after evaluation complete)
    python3 scripts/run_naturalistic_pipeline.py --only-aggregate
        """
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for query generation")
    parser.add_argument("--num-queries", type=int, default=20, help="Number of queries to generate")
    parser.add_argument("--max-parallel", type=int, default=3, help="Max parallel job executions")
    parser.add_argument("--skip-generation", action="store_true", help="Skip query and job generation")
    parser.add_argument("--skip-evaluation", action="store_true", help="Skip model evaluation")
    parser.add_argument("--only-aggregate", action="store_true", help="Only run aggregation and analysis")

    args = parser.parse_args()

    start_time = datetime.now()

    print(f"\n{'#'*70}")
    print("#" + " NATURALISTIC QUERIES EVALUATION PIPELINE ".center(68) + "#")
    print(f"{'#'*70}")
    print(f"\nStarted: {start_time.isoformat()}")
    print(f"Configuration:")
    print(f"  Seed: {args.seed}")
    print(f"  Queries: {args.num_queries}")
    print(f"  Max parallel: {args.max_parallel}")

    all_success = True

    if args.only_aggregate:
        # Only run phases 4 and 5
        all_success = phase_4_aggregate_profiles() and all_success
        all_success = phase_5_run_analysis() and all_success
    else:
        # Full pipeline
        if not args.skip_generation:
            all_success = phase_1_generate_queries(args.seed, args.num_queries) and all_success
            all_success = phase_2_generate_jobs() and all_success

        if not args.skip_evaluation and all_success:
            all_success = phase_3_run_evaluations(args.max_parallel) and all_success

        if all_success:
            all_success = phase_4_aggregate_profiles() and all_success
            all_success = phase_5_run_analysis() and all_success

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\n{'#'*70}")
    print("#" + " PIPELINE COMPLETE ".center(68) + "#")
    print(f"{'#'*70}")
    print(f"\nFinished: {end_time.isoformat()}")
    print(f"Total time: {duration/60:.1f} minutes")
    print(f"Status: {'SUCCESS' if all_success else 'FAILED (see errors above)'}")

    if all_success:
        print(f"\nOutput locations:")
        print(f"  - Naturalistic profiles (1-10): outputs/behavioral_profiles/naturalistic/")
        print(f"  - Naturalistic profiles (1-50): outputs/behavioral_profiles/naturalistic_50/")
        print(f"\nNext steps:")
        print(f"  1. Review research briefs in each condition directory")
        print(f"  2. Compare floor/ceiling effects between 1-10 and 1-50 scales")
        print(f"  3. Update cross-condition comparison if desired")

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
