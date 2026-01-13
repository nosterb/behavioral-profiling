#!/usr/bin/env python3
"""
Complete behavioral visualization - creates both per-job and aggregated charts.

This script:
1. Creates individual job visualizations in visualization/individual_jobs/
2. Creates cross-job aggregate in visualization/summary/

Usage:
    python3 scripts/visualize_all_behavioral.py <directory>

Example:
    python3 scripts/visualize_all_behavioral.py outputs/single_prompt_jobs/12_7_2025_behavioral_v3
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from visualize_behavioral import visualize_judge_results
from aggregate_behavioral import aggregate_scores_from_directory, create_aggregated_spider_chart


def visualize_all(directory: Path):
    """
    Create complete visualization suite for a behavioral study directory.

    Creates:
    - visualization/individual_jobs/{job_id}/ for each job
    - visualization/summary/aggregated_behavioral_profiles.png for all jobs
    """
    directory = Path(directory)

    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        sys.exit(1)

    if not directory.is_dir():
        print(f"❌ Not a directory: {directory}")
        sys.exit(1)

    print(f"{'='*70}")
    print(f"Behavioral Visualization Suite")
    print(f"{'='*70}")
    print(f"Directory: {directory.name}\n")

    # Find all JSON files
    json_files = sorted(directory.rglob("*.json"))

    if not json_files:
        print(f"❌ No JSON files found in {directory}")
        sys.exit(1)

    print(f"Found {len(json_files)} job files\n")

    # Step 1: Create per-job visualizations
    print(f"{'─'*70}")
    print(f"STEP 1: Creating per-job visualizations")
    print(f"{'─'*70}\n")

    base_viz_dir = directory / 'visualization' / 'individual_jobs'
    base_viz_dir.mkdir(parents=True, exist_ok=True)

    processed = 0
    skipped = 0
    total_files = 0

    for job_file in json_files:
        print(f"📄 {job_file.name}")

        try:
            # Extract job ID from metadata
            import json
            with open(job_file, 'r') as f:
                job_data = json.load(f)

            job_id = job_data.get('job_metadata', {}).get('payload_name', job_file.stem)
            job_output_dir = base_viz_dir / job_id

            # Create visualizations for this job
            created_files = visualize_judge_results(job_file, job_output_dir)
            print(f"  ✓ Created {len(created_files)} visualizations in individual_jobs/{job_id}/")
            total_files += len(created_files)
            processed += 1

        except ValueError as e:
            print(f"  ⏭️  Skipped: {e}")
            skipped += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            skipped += 1

    print(f"\n{'─'*70}")
    print(f"Per-job results: {processed} processed, {skipped} skipped")
    print(f"Total files created: {total_files}")
    print(f"{'─'*70}\n")

    # Step 2: Create cross-job aggregate
    print(f"{'─'*70}")
    print(f"STEP 2: Creating cross-job aggregate")
    print(f"{'─'*70}\n")

    try:
        # Aggregate scores
        aggregated_scores = aggregate_scores_from_directory(directory)

        # Create summary directory
        summary_dir = directory / "visualization" / "summary"
        summary_dir.mkdir(parents=True, exist_ok=True)
        output_path = summary_dir / "aggregated_behavioral_profiles.png"

        # Create aggregated chart
        print(f"📊 Creating aggregated spider chart...")
        chart_path = create_aggregated_spider_chart(
            aggregated_scores,
            output_path,
            title=f"Aggregated Behavioral Profiles - {directory.name}"
        )

        print(f"  ✓ Created: {chart_path.name}")
        print(f"  Models: {len(aggregated_scores)}")
        print(f"  Dimensions: {len(next(iter(aggregated_scores.values())))}")

    except Exception as e:
        print(f"  ❌ Error creating aggregate: {e}")
        import traceback
        traceback.print_exc()

    # Final summary
    print(f"\n{'='*70}")
    print(f"✓ Visualization Complete!")
    print(f"{'='*70}")
    print(f"Structure:")
    print(f"  {directory.name}/")
    print(f"  └── visualization/")
    print(f"      ├── individual_jobs/        ({processed} jobs)")
    print(f"      │   ├── {json_files[0].stem.replace('job_', '')}/")
    print(f"      │   │   ├── *_spider_1_Model.png")
    print(f"      │   │   ├── *_spider_2_Model.png")
    print(f"      │   │   ├── ...")
    print(f"      │   │   ├── *_comparative_spider.png")
    print(f"      │   │   └── *_heatmap.png")
    print(f"      │   └── ...")
    print(f"      └── summary/")
    print(f"          └── aggregated_behavioral_profiles.png")
    print(f"{'='*70}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/visualize_all_behavioral.py <directory>")
        print("\nCreates complete visualization suite:")
        print("  - Per-job visualizations in visualization/individual_jobs/")
        print("  - Cross-job aggregate in visualization/summary/")
        print("\nExample:")
        print("  python3 scripts/visualize_all_behavioral.py outputs/single_prompt_jobs/12_7_2025_behavioral_v3")
        sys.exit(1)

    directory = Path(sys.argv[1])
    visualize_all(directory)


if __name__ == "__main__":
    main()
