#!/usr/bin/env python3
"""
Add final_averaged_scores to existing judge evaluation files.

This script finds all scores in a judge evaluation file and calculates
the averaged scores across all judges, then adds it to the file.

Usage:
    python3 scripts/add_averaged_scores.py <file.json>
    python3 scripts/add_averaged_scores.py outputs/single_prompt_jobs/*.json
"""

import json
import sys
from pathlib import Path


def add_averaged_scores_to_file(file_path: Path) -> bool:
    """
    Add final_averaged_scores to a judge evaluation file.

    Returns True if file was modified, False otherwise.
    """
    # Load file
    with open(file_path, 'r') as f:
        job_data = json.load(f)

    # Check if file has judge evaluation
    if 'judge_evaluation' not in job_data:
        print(f"  ⏭️  No judge evaluation found")
        return False

    judge_eval = job_data['judge_evaluation']
    evaluations = judge_eval.get('evaluations', [])
    comparative = judge_eval.get('comparative_analysis')

    if not evaluations:
        print(f"  ⏭️  No evaluations found")
        return False

    # Check if already has final_averaged_scores
    if evaluations[0].get('final_averaged_scores'):
        print(f"  ⏭️  Already has final_averaged_scores")
        return False

    modified = False

    # Process each model evaluation
    for model_eval in evaluations:
        # Collect all judge scores for this model
        all_judge_scores = []

        # Extract scores from Pass 1 judges ONLY
        # Note: We don't include comparative judge because it provides aggregate
        # analysis, not per-model scores. Including it would pull all models toward
        # the same center.
        for judge_eval_data in model_eval.get('pass1_judges', []):
            extracted = judge_eval_data.get('extracted_json', {})
            if 'scores' in extracted and isinstance(extracted['scores'], dict):
                all_judge_scores.append(extracted['scores'])

        # If no scores found, skip this model
        if not all_judge_scores:
            continue

        # Calculate averages for each dimension
        all_dimensions = set()
        for scores in all_judge_scores:
            all_dimensions.update(scores.keys())

        averaged_scores = {}
        for dimension in all_dimensions:
            values = []
            for scores in all_judge_scores:
                if dimension in scores and isinstance(scores[dimension], (int, float)):
                    values.append(scores[dimension])

            if values:
                averaged_scores[dimension] = round(sum(values) / len(values), 2)

        # Add result to model evaluation
        model_eval['final_averaged_scores'] = {
            'scores': averaged_scores,
            'num_judges': len(all_judge_scores),
            'dimensions': list(averaged_scores.keys())
        }
        modified = True

    if not modified:
        print(f"  ⏭️  No scores to average")
        return False

    # Update post_processing metadata
    if 'dimension_averages' not in judge_eval['judge_metadata'].get('post_processing', []):
        judge_eval['judge_metadata']['post_processing'] = judge_eval['judge_metadata'].get('post_processing', []) + ['dimension_averages']

    # Write back to file
    with open(file_path, 'w') as f:
        json.dump(job_data, f, indent=2)

    print(f"  ✓  Added final_averaged_scores")

    # Re-export chat file
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
        from export_utils import export_batch_job_chat

        job_id = job_data['job_metadata'].get('payload_name') or job_data['job_metadata'].get('job_id', file_path.stem)
        timestamp_str = job_data['job_metadata']['timestamp'].replace('T', '_').replace(':', '').replace('-', '').split('.')[0]
        output_dir = file_path.parent

        chat_path = export_batch_job_chat(job_data, job_id, timestamp_str, output_dir)
        print(f"  ✓  Updated chat: {chat_path.name}")
    except Exception as e:
        print(f"  ⚠️  Could not update chat: {e}")

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/add_averaged_scores.py <file1.json> [file2.json ...]")
        sys.exit(1)

    files = [Path(f) for f in sys.argv[1:]]

    print(f"Processing {len(files)} file(s)...\n")

    updated = 0
    skipped = 0

    for file_path in files:
        if not file_path.exists():
            print(f"❌ {file_path.name}: Not found")
            skipped += 1
            continue

        print(f"📄 {file_path.name}")
        try:
            if add_averaged_scores_to_file(file_path):
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            skipped += 1

    print(f"\n{'='*60}")
    print(f"Summary: {updated} updated, {skipped} skipped")


if __name__ == '__main__':
    main()
