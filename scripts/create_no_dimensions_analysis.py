#!/usr/bin/env python3
"""
Create no_dimensions sensitivity analysis with proper audit trails.

This script:
1. Re-aggregates profiles excluding dimensions_suite jobs
2. Runs H1/H2 analysis pipeline
3. Creates sensitivity_analysis_info.json with full provenance

Usage:
    python3 scripts/create_no_dimensions_analysis.py baseline
    python3 scripts/create_no_dimensions_analysis.py baseline --dry-run
"""

import json
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description='Create no_dimensions sensitivity analysis'
    )
    parser.add_argument('condition', help='Condition name (e.g., baseline)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')
    parser.add_argument('--force', action='store_true',
                        help='Overwrite existing no_dimensions directory')

    args = parser.parse_args()

    condition = args.condition
    base_dir = Path("outputs/behavioral_profiles") / condition
    output_dir = base_dir / "no_dimensions"
    job_dir = Path("outputs/single_prompt_jobs")

    if not base_dir.exists():
        print(f"Error: Condition directory not found: {base_dir}")
        sys.exit(1)

    if output_dir.exists() and not args.force:
        print(f"Error: {output_dir} already exists. Use --force to overwrite.")
        sys.exit(1)

    print("=" * 80)
    print(f"CREATE NO-DIMENSIONS ANALYSIS: {condition}")
    print("=" * 80)

    # Step 1: Count what we're excluding
    print(f"\n1. Analyzing job files...")

    # Count total jobs for condition
    total_cmd = [
        "python3", "scripts/update_behavioral_profiles.py",
        str(job_dir), "--recursive", "--condition", condition, "--dry-run"
    ]
    result = subprocess.run(total_cmd, capture_output=True, text=True)
    total_match = None
    for line in result.stdout.split('\n'):
        if 'Found' in line and 'job files' in line:
            total_match = line
            break

    # Count jobs excluding dimensions
    exclude_cmd = [
        "python3", "scripts/update_behavioral_profiles.py",
        str(job_dir), "--recursive", "--condition", condition,
        "--exclude-patterns", "dimensions", "baseline_dimensions",
        "--dry-run"
    ]
    result = subprocess.run(exclude_cmd, capture_output=True, text=True)
    filtered_match = None
    for line in result.stdout.split('\n'):
        if 'Found' in line and 'job files' in line:
            filtered_match = line
            break

    print(f"   Total: {total_match}")
    print(f"   Without dimensions: {filtered_match}")

    if args.dry_run:
        print("\n[DRY RUN] Would create no_dimensions analysis")
        print("Steps that would be performed:")
        print("  1. Re-aggregate profiles excluding dimensions suite")
        print("  2. Run median split classification")
        print("  3. Generate H1/H2 visualizations")
        print("  4. Create sensitivity_analysis_info.json")
        print("  5. Generate research brief")
        return

    # Step 2: Clear and create output directory
    print(f"\n2. Preparing output directory...")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    (output_dir / "profiles").mkdir()
    (output_dir / "history").mkdir()

    # Step 3: Aggregate profiles without dimensions
    print(f"\n3. Aggregating profiles (excluding dimensions suite)...")
    aggregate_cmd = [
        "python3", "scripts/update_behavioral_profiles.py",
        str(job_dir), "--recursive",
        "--condition", condition,
        "--profile-dir", str(output_dir),
        "--exclude-patterns", "dimensions", "baseline_dimensions",
        "--force", "--skip-viz"
    ]
    result = subprocess.run(aggregate_cmd, capture_output=True, text=True)
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)

    # Step 4: Run median split classification
    print(f"\n4. Running median split classification...")
    median_cmd = [
        "python3", "scripts/calculate_median_split.py",
        str(output_dir),
        "--condition", f"{condition}/no_dimensions"
    ]
    result = subprocess.run(median_cmd, capture_output=True, text=True)
    print(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
    if result.returncode != 0:
        print(f"Warning: {result.stderr}")

    # Step 5: Generate H1/H2 visualizations
    print(f"\n5. Generating H1/H2 visualizations...")
    cond_path = f"{condition}/no_dimensions"

    scripts = [
        ["python3", "scripts/create_h1_bar_chart.py", cond_path],
        ["python3", "scripts/create_h2_color_coded_scatters.py", cond_path],
    ]

    for cmd in scripts:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   Warning: {cmd[1]} - {result.stderr[:200]}")
        else:
            print(f"   ✓ {cmd[1]}")

    # Step 6: Create sensitivity_analysis_info.json with audit trail
    print(f"\n6. Creating sensitivity analysis info with audit trail...")

    # Load original and new classifications
    orig_path = base_dir / "median_split_classification.json"
    new_path = output_dir / "median_split_classification.json"

    if not orig_path.exists() or not new_path.exists():
        print(f"   Warning: Missing classification files")
        print(f"   Original: {orig_path.exists()}")
        print(f"   New: {new_path.exists()}")
    else:
        with open(orig_path) as f:
            orig_data = json.load(f)
        with open(new_path) as f:
            new_data = json.load(f)

        # Calculate changes
        orig_d = orig_data["statistics"]["disinhibition"]["cohens_d"]
        new_d = new_data["statistics"]["disinhibition"]["cohens_d"]

        orig_r = orig_data["correlation"]["sophistication_disinhibition"]
        new_r = new_data["correlation"]["sophistication_disinhibition"]

        sensitivity_info = {
            "metadata": {
                "generated": datetime.now().isoformat() + "Z",
                "updated": datetime.now().isoformat() + "Z",
                "analysis": "No-Dimensions Sensitivity Analysis",
                "condition": condition
            },
            "provenance": {
                "source_files": {
                    "full_dataset": str(orig_path),
                    "no_dimensions": str(new_path),
                    "job_directory": str(job_dir)
                },
                "methodology": {
                    "exclusion_patterns": ["dimensions", "baseline_dimensions"],
                    "purpose": "Test robustness of H1/H2 findings without dimension-specific probing"
                }
            },
            "config": {
                "excluded_suites": ["dimensions"],
                "included_suites": ["broad", "affective", "general", "typical", "love"]
            },
            "statistics": {
                "full_dataset": {
                    "n_models": len(orig_data.get("models", [])),
                    "cohens_d": orig_d,
                    "r": orig_r,
                    "p_value": orig_data["statistics"]["disinhibition"]["p_value"]
                },
                "no_dimensions": {
                    "n_models": len(new_data.get("models", [])),
                    "cohens_d": new_d,
                    "r": new_r,
                    "p_value": new_data["statistics"]["disinhibition"]["p_value"]
                }
            },
            "change": {
                "d_delta": round(new_d - orig_d, 3),
                "r_delta": round(new_r - orig_r, 3),
                "interpretation": (
                    "strengthened" if (new_d - orig_d) > 0.1 or (new_r - orig_r) > 0.02
                    else "weakened" if (new_d - orig_d) < -0.1 or (new_r - orig_r) < -0.02
                    else "robust"
                )
            }
        }

        info_path = output_dir / "sensitivity_analysis_info.json"
        with open(info_path, 'w') as f:
            json.dump(sensitivity_info, f, indent=2)
        print(f"   ✓ Created {info_path}")

    # Step 7: Generate research brief
    print(f"\n7. Generating research brief...")
    brief_cmd = [
        "python3", "scripts/analyze_no_dimensions.py",
        condition, "--regenerate-brief"
    ]
    result = subprocess.run(brief_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✓ Generated RESEARCH_BRIEF.md")
    else:
        print(f"   Warning: Brief generation failed - {result.stderr[:200]}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    if orig_path.exists() and new_path.exists():
        print(f"Full dataset:    n={len(orig_data.get('models', []))}, d={orig_d:.2f}, r={orig_r:.3f}")
        print(f"No dimensions:   n={len(new_data.get('models', []))}, d={new_d:.2f}, r={new_r:.3f}")
        print(f"Change:          Δd={new_d - orig_d:+.2f}, Δr={new_r - orig_r:+.3f}")
    print(f"\nOutput: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
