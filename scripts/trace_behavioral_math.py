#!/usr/bin/env python3
"""
Trace Behavioral Math - Show all raw numbers and calculations

This script provides a complete trace of how behavioral scores are calculated:
1. Individual judge scores (Pass 1) - 3 judges
2. Comparative judge scores (if present)
3. Per-job averages (averaging 3 Pass 1 judges only)
4. Cross-job aggregation (averaging across all jobs)
5. Final spider chart values

Output is written to a human-readable file showing all raw data and math.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional


def load_job_file(filepath: Path) -> dict:
    """Load and parse a judge evaluation JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def extract_pass1_scores(model_eval: dict) -> List[Dict[str, any]]:
    """Extract all Pass 1 judge scores for a model."""
    scores = []
    for judge in model_eval.get('pass1_judges', []):
        extracted = judge.get('extracted_json', {})
        if 'scores' in extracted:
            judge_name = judge.get('judge_display_name', 'Unknown')
            scores.append({
                'judge_name': judge_name,
                'scores': extracted['scores']
            })
    return scores


def extract_comparative_score(job_data: dict, model_eval: dict) -> Optional[Dict[str, float]]:
    """Extract comparative judge score for a specific model.

    Note: Comparative analysis often only contains data for the first model due to
    token limits. If a model's evaluation isn't present, returns None.
    """
    comp_analysis = job_data.get('judge_evaluation', {}).get('comparative_analysis', {})
    extracted_json = comp_analysis.get('extracted_json', {})

    if not extracted_json or not isinstance(extracted_json, dict):
        return None

    # The extracted_json contains ONE model's evaluation (usually MODEL 1)
    # We need to match this to the current model_eval

    # Get the model's index from the evaluations list
    evaluations = job_data.get('judge_evaluation', {}).get('evaluations', [])
    try:
        model_index = evaluations.index(model_eval)
        comp_model_id = f"MODEL {model_index + 1}"
    except (ValueError, AttributeError):
        return None

    # Check if the extracted_json is for this model
    if extracted_json.get('model_id') == comp_model_id:
        return extracted_json.get('scores')

    return None


def calculate_per_job_average(pass1_scores: List[Dict]) -> Dict[str, float]:
    """Calculate average across Pass 1 judges for each dimension."""
    if not pass1_scores:
        return {}

    # Get all dimensions
    all_dimensions = set()
    for judge_data in pass1_scores:
        all_dimensions.update(judge_data['scores'].keys())

    # Calculate averages
    averaged = {}
    for dimension in all_dimensions:
        values = []
        for judge_data in pass1_scores:
            if dimension in judge_data['scores']:
                value = judge_data['scores'][dimension]
                # Skip non-numeric values (like notes/strings)
                if isinstance(value, (int, float)):
                    values.append(value)

        if values:
            averaged[dimension] = sum(values) / len(values)

    return averaged


def trace_single_job(filepath: Path, output_lines: List[str]):
    """Trace calculations for a single job file."""
    job_data = load_job_file(filepath)
    job_name = filepath.stem

    output_lines.append(f"\n{'='*80}")
    output_lines.append(f"JOB: {job_name}")
    output_lines.append(f"File: {filepath.name}")
    output_lines.append(f"{'='*80}\n")

    evaluations = job_data.get('judge_evaluation', {}).get('evaluations', [])

    for model_eval in evaluations:
        model_name = model_eval.get('display_name', 'Unknown')
        model_id = model_eval.get('model_id', 'Unknown')

        output_lines.append(f"\n{'─'*80}")
        output_lines.append(f"MODEL: {model_name}")
        output_lines.append(f"Model ID: {model_id}")
        output_lines.append(f"{'─'*80}\n")

        # Extract Pass 1 judge scores
        pass1_scores = extract_pass1_scores(model_eval)

        if not pass1_scores:
            output_lines.append("  ⚠ No Pass 1 judge scores found\n")
            continue

        # Show raw judge scores
        output_lines.append("PASS 1 JUDGE SCORES (Used for averaging):")
        output_lines.append("")

        # Get all dimensions from first judge
        dimensions = list(pass1_scores[0]['scores'].keys())

        for i, judge_data in enumerate(pass1_scores, 1):
            output_lines.append(f"  Judge {i}: {judge_data['judge_name']}")
            for dim in dimensions:
                score = judge_data['scores'].get(dim, 'N/A')
                output_lines.append(f"    {dim:20s}: {score}")
            output_lines.append("")

        # Extract comparative judge score
        comp_score = extract_comparative_score(job_data, model_eval)

        output_lines.append("\nCOMPARATIVE JUDGE SCORE (For reference only, NOT used in averaging):")
        output_lines.append("")

        if comp_score:
            output_lines.append(f"  Comparative Judge: {job_data.get('judge_evaluation', {}).get('comparative_analysis', {}).get('judge_display_name', 'Unknown')}")
            for dim in dimensions:
                score = comp_score.get(dim, 'N/A')
                output_lines.append(f"    {dim:20s}: {score}")
        else:
            output_lines.append("  N/A (Comparative judge output not present for this model)")
        output_lines.append("")

        # Calculate and show per-job averages
        output_lines.append("\nCALCULATION (Per-Job Average - ONLY Pass 1 judges):")
        output_lines.append("")
        output_lines.append("  Note: Only the 3 Pass 1 judges are averaged.")
        output_lines.append("        Comparative judge is excluded to prevent score convergence.")
        output_lines.append("")

        calculated_avg = calculate_per_job_average(pass1_scores)

        for dim in dimensions:
            values = [j['scores'].get(dim) for j in pass1_scores if dim in j['scores']]
            if values:
                avg = sum(values) / len(values)
                values_str = ' + '.join(str(v) for v in values)
                output_lines.append(f"  {dim:20s}: ({values_str}) / {len(values)} = {avg:.2f}")

        # Check against stored final_averaged_scores if present
        stored_avg = model_eval.get('final_averaged_scores', {}).get('scores', {})
        if stored_avg:
            output_lines.append("\n\nVERIFICATION (Stored final_averaged_scores):")
            output_lines.append("")

            all_match = True
            for dim in dimensions:
                calc_val = calculated_avg.get(dim)
                stored_val = stored_avg.get(dim)

                if calc_val is not None and stored_val is not None:
                    match = abs(calc_val - stored_val) < 0.01
                    status = "✓" if match else "✗"
                    output_lines.append(f"  {dim:20s}: Calculated={calc_val:.2f}, Stored={stored_val:.2f} {status}")
                    if not match:
                        all_match = False

            if all_match:
                output_lines.append("\n  ✓ All calculated values match stored values!")
            else:
                output_lines.append("\n  ✗ Some values don't match - check calculation")
        else:
            output_lines.append("\n\n⚠ No final_averaged_scores found in file (needs post-processing)")


def trace_aggregation(directory: Path, output_lines: List[str]):
    """Trace cross-job aggregation for all models."""
    output_lines.append(f"\n\n{'='*80}")
    output_lines.append("CROSS-JOB AGGREGATION (Final Spider Chart Values)")
    output_lines.append(f"{'='*80}\n")
    output_lines.append("This shows how per-job averages are aggregated across all jobs")
    output_lines.append("to produce the final spider chart visualization.\n")

    # Collect all scores per model per dimension
    model_scores = defaultdict(lambda: defaultdict(list))
    job_files = []

    for filepath in sorted(directory.rglob("job_*.json")):
        job_files.append(filepath.name)
        job_data = load_job_file(filepath)
        evaluations = job_data.get('judge_evaluation', {}).get('evaluations', [])

        for model_eval in evaluations:
            model_name = model_eval.get('display_name', 'Unknown')
            scores = model_eval.get('final_averaged_scores', {}).get('scores', {})

            for dimension, value in scores.items():
                model_scores[model_name][dimension].append({
                    'job': filepath.stem,
                    'value': value
                })

    output_lines.append(f"Found {len(job_files)} job files:")
    for jf in job_files:
        output_lines.append(f"  - {jf}")
    output_lines.append("")

    # Calculate and show aggregation for each model
    for model_name in sorted(model_scores.keys()):
        output_lines.append(f"\n{'─'*80}")
        output_lines.append(f"MODEL: {model_name}")
        output_lines.append(f"{'─'*80}\n")

        dimensions_data = model_scores[model_name]

        # Show calculations for each dimension
        for dimension in sorted(dimensions_data.keys()):
            job_scores = dimensions_data[dimension]
            output_lines.append(f"\nDimension: {dimension}")
            output_lines.append("")

            # Show all job values
            output_lines.append("  Per-Job Scores:")
            for js in job_scores:
                output_lines.append(f"    {js['job']:50s}: {js['value']:.2f}")

            # Calculate aggregate
            values = [js['value'] for js in job_scores]
            aggregate = sum(values) / len(values)

            output_lines.append(f"\n  Calculation:")
            values_str = ' + '.join(f"{v:.2f}" for v in values)
            output_lines.append(f"    ({values_str}) / {len(values)}")
            output_lines.append(f"    = {sum(values):.2f} / {len(values)}")
            output_lines.append(f"    = {aggregate:.2f}")
            output_lines.append(f"\n  ⭐ FINAL AGGREGATED SCORE (used in spider chart): {aggregate:.2f}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single job:  python trace_behavioral_math.py <job_file.json>")
        print("  Directory:   python trace_behavioral_math.py <directory_path>")
        print("")
        print("Examples:")
        print("  python trace_behavioral_math.py outputs/single_prompt_jobs/job_behavioral_warmth_baseline_*.json")
        print("  python trace_behavioral_math.py outputs/single_prompt_jobs/")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_lines = []

    # Header
    output_lines.append("="*80)
    output_lines.append("BEHAVIORAL SCORE CALCULATION TRACE")
    output_lines.append("="*80)
    output_lines.append("")
    output_lines.append("This file shows all raw judge scores and the mathematical calculations")
    output_lines.append("used to produce the final behavioral spider charts.")
    output_lines.append("")
    output_lines.append("Data Flow:")
    output_lines.append("  1. Pass 1 Judge Scores - 3 judges independently evaluate each model")
    output_lines.append("  2. Comparative Judge Score - 1 judge reviews all evaluations (reference only)")
    output_lines.append("  3. Per-Job Average - Average the 3 Pass 1 judge scores (NOT comparative)")
    output_lines.append("  4. Cross-Job Aggregation - Average per-job scores across all jobs")
    output_lines.append("  5. Final Spider Chart - Uses the aggregated scores from step 4")
    output_lines.append("")
    output_lines.append("Important: Only Pass 1 judges (3) are used for quantitative averaging.")
    output_lines.append("           Comparative judge provides qualitative analysis only.")
    output_lines.append("")

    if input_path.is_file():
        # Single file mode
        output_lines.append(f"Mode: Single Job Analysis")
        output_lines.append(f"Input: {input_path}")
        trace_single_job(input_path, output_lines)

        output_file = input_path.parent / f"{input_path.stem}_math_trace.txt"

    elif input_path.is_dir():
        # Directory mode - analyze all jobs and show aggregation
        output_lines.append(f"Mode: Full Directory Analysis with Aggregation")
        output_lines.append(f"Input: {input_path}")

        # Trace each job
        job_files = sorted(input_path.rglob("job_*.json"))
        if not job_files:
            print(f"Error: No job_*.json files found in {input_path}")
            sys.exit(1)

        output_lines.append(f"\nFound {len(job_files)} behavioral job files\n")

        for job_file in job_files:
            trace_single_job(job_file, output_lines)

        # Show cross-job aggregation
        trace_aggregation(input_path, output_lines)

        output_file = input_path / "behavioral_math_trace_FULL.txt"

    else:
        print(f"Error: {input_path} is not a file or directory")
        sys.exit(1)

    # Write output
    with open(output_file, 'w') as f:
        f.write('\n'.join(output_lines))

    print(f"\n✓ Trace complete!")
    print(f"  Output written to: {output_file}")
    print(f"\nThe file contains:")
    print(f"  - Raw Pass 1 judge scores (3 judges per model)")
    print(f"  - Comparative judge scores (when available, shown as N/A otherwise)")
    print(f"  - Step-by-step averaging calculations (Pass 1 judges only)")
    print(f"  - Verification against stored values")
    if input_path.is_dir():
        print(f"  - Cross-job aggregation showing final spider chart values")
    print(f"\nOpen the file to inspect all calculations in detail.")


if __name__ == "__main__":
    main()
