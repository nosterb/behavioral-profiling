#!/usr/bin/env python3
"""
Compare the 3-judge panel (Claude-4.5-Sonnet, Llama-4-Maverick-17B, DeepSeek-R1).
Measure how consistently they rate the same model responses.
"""

import json
from pathlib import Path
from collections import defaultdict


def extract_judge_scores(job_file):
    """Extract scores from all 3 judges for all models in a job."""
    try:
        with open(job_file) as f:
            data = json.load(f)
    except:
        return []

    je = data.get('judge_evaluation', {})
    evals = je.get('evaluations', [])

    comparisons = []

    for eval_data in evals:
        model_name = eval_data.get('display_name', 'Unknown')
        pass1_judges = eval_data.get('pass1_judges', [])

        if len(pass1_judges) != 3:
            continue

        # Extract scores from each judge
        judge_scores = {}

        for judge in pass1_judges:
            judge_name = judge.get('judge_display_name', 'Unknown')
            ej = judge.get('extracted_json', {})
            scores = ej.get('scores', {})

            if scores:
                judge_scores[judge_name] = scores

        # Need all 3 judges
        if len(judge_scores) == 3:
            comparisons.append({
                'model': model_name,
                'judges': judge_scores
            })

    return comparisons


def calculate_judge_agreement(comparisons):
    """Calculate agreement statistics between judges."""
    dimensions = ['depth', 'authenticity', 'transgression', 'aggression',
                  'tribalism', 'grandiosity', 'warmth', 'formality', 'hedging']

    judge_names = ['Claude-4.5-Sonnet', 'Llama-4-Maverick-17B', 'DeepSeek-R1']

    # Collect scores by judge and dimension
    judge_dim_scores = defaultdict(lambda: defaultdict(list))

    for comp in comparisons:
        for judge_name, scores in comp['judges'].items():
            for dim in dimensions:
                if dim in scores:
                    judge_dim_scores[judge_name][dim].append(scores[dim])

    # Calculate mean scores per judge per dimension
    judge_means = {}
    for judge_name in judge_names:
        judge_means[judge_name] = {}
        for dim in dimensions:
            scores = judge_dim_scores[judge_name][dim]
            if scores:
                judge_means[judge_name][dim] = sum(scores) / len(scores)

    # Calculate pairwise correlations
    judge_pairs = [
        ('Claude-4.5-Sonnet', 'Llama-4-Maverick-17B'),
        ('Claude-4.5-Sonnet', 'DeepSeek-R1'),
        ('Llama-4-Maverick-17B', 'DeepSeek-R1')
    ]

    correlations = {}

    for judge1, judge2 in judge_pairs:
        pair_corr = {}

        for dim in dimensions:
            scores1 = judge_dim_scores[judge1][dim]
            scores2 = judge_dim_scores[judge2][dim]

            # Match up scores (same model)
            matched_scores = []
            for comp in comparisons:
                if judge1 in comp['judges'] and judge2 in comp['judges']:
                    s1 = comp['judges'][judge1].get(dim)
                    s2 = comp['judges'][judge2].get(dim)
                    if s1 is not None and s2 is not None:
                        matched_scores.append((s1, s2))

            if len(matched_scores) > 2:
                # Calculate correlation
                from math import sqrt
                n = len(matched_scores)
                x_vals = [s[0] for s in matched_scores]
                y_vals = [s[1] for s in matched_scores]

                mean_x = sum(x_vals) / n
                mean_y = sum(y_vals) / n

                numerator = sum((x_vals[i] - mean_x) * (y_vals[i] - mean_y) for i in range(n))
                denom_x = sqrt(sum((x_vals[i] - mean_x)**2 for i in range(n)))
                denom_y = sqrt(sum((y_vals[i] - mean_y)**2 for i in range(n)))

                r = numerator / (denom_x * denom_y) if denom_x > 0 and denom_y > 0 else 0

                # Calculate mean absolute difference
                mad = sum(abs(s[0] - s[1]) for s in matched_scores) / n

                pair_corr[dim] = {
                    'correlation': r,
                    'mad': mad,
                    'n': n
                }

        correlations[(judge1, judge2)] = pair_corr

    return {
        'judge_means': judge_means,
        'correlations': correlations,
        'n_comparisons': len(comparisons)
    }


def main():
    job_dir = Path("outputs/single_prompt_jobs")

    print("Loading job results...")
    job_files = list(job_dir.rglob("*.json"))

    all_comparisons = []
    for job_file in job_files:
        comps = extract_judge_scores(job_file)
        all_comparisons.extend(comps)

    print(f"Found {len(all_comparisons)} model evaluations with all 3 judges\n")

    if not all_comparisons:
        print("No evaluations found with all 3 judges")
        return

    # Calculate agreement
    results = calculate_judge_agreement(all_comparisons)

    print(f"{'='*120}")
    print("3-JUDGE PANEL AGREEMENT ANALYSIS")
    print(f"{'='*120}\n")

    print(f"Judges: Claude-4.5-Sonnet, Llama-4-Maverick-17B, DeepSeek-R1")
    print(f"Total evaluations: {results['n_comparisons']}\n")

    # Show mean scores per judge
    print(f"{'='*120}")
    print("MEAN SCORES BY JUDGE")
    print(f"{'='*120}\n")

    dimensions = ['depth', 'authenticity', 'transgression', 'aggression', 'tribalism', 'grandiosity', 'warmth', 'formality', 'hedging']

    print(f"{'Dimension':<15s}  {'Sonnet':>7s}  {'Llama':>7s}  {'DeepSeek':>7s}  {'Range':>7s}")
    print("-" * 120)

    for dim in dimensions:
        sonnet = results['judge_means']['Claude-4.5-Sonnet'].get(dim, 0)
        llama = results['judge_means']['Llama-4-Maverick-17B'].get(dim, 0)
        deepseek = results['judge_means']['DeepSeek-R1'].get(dim, 0)

        scores = [sonnet, llama, deepseek]
        score_range = max(scores) - min(scores)

        print(f"{dim.capitalize():<15s}  {sonnet:>7.2f}  {llama:>7.2f}  {deepseek:>7.2f}  {score_range:>7.2f}")

    # Show pairwise correlations
    print(f"\n{'='*120}")
    print("PAIRWISE JUDGE AGREEMENT (Correlation & Mean Absolute Difference)")
    print(f"{'='*120}\n")

    judge_pairs = [
        ('Claude-4.5-Sonnet', 'Llama-4-Maverick-17B', 'Sonnet vs Llama'),
        ('Claude-4.5-Sonnet', 'DeepSeek-R1', 'Sonnet vs DeepSeek'),
        ('Llama-4-Maverick-17B', 'DeepSeek-R1', 'Llama vs DeepSeek')
    ]

    for judge1, judge2, label in judge_pairs:
        print(f"\n{label}")
        print("-" * 120)
        print(f"{'Dimension':<15s}  {'Corr (r)':>10s}  {'MAD':>7s}  {'n':>5s}  {'Agreement':<20s}")
        print("-" * 120)

        pair_corr = results['correlations'].get((judge1, judge2), {})

        for dim in dimensions:
            if dim in pair_corr:
                r = pair_corr[dim]['correlation']
                mad = pair_corr[dim]['mad']
                n = pair_corr[dim]['n']

                # Interpret agreement
                if r >= 0.8:
                    agreement = "Very High"
                elif r >= 0.6:
                    agreement = "High"
                elif r >= 0.4:
                    agreement = "Moderate"
                elif r >= 0.2:
                    agreement = "Low"
                else:
                    agreement = "Very Low"

                print(f"{dim.capitalize():<15s}  {r:>10.3f}  {mad:>7.2f}  {n:>5d}  {agreement:<20s}")

    # Overall summary
    print(f"\n{'='*120}")
    print("OVERALL SUMMARY")
    print(f"{'='*120}\n")

    # Calculate average correlations
    for judge1, judge2, label in judge_pairs:
        pair_corr = results['correlations'].get((judge1, judge2), {})
        all_r = [pair_corr[dim]['correlation'] for dim in dimensions if dim in pair_corr]
        avg_r = sum(all_r) / len(all_r) if all_r else 0

        all_mad = [pair_corr[dim]['mad'] for dim in dimensions if dim in pair_corr]
        avg_mad = sum(all_mad) / len(all_mad) if all_mad else 0

        print(f"{label}:")
        print(f"  Average correlation: {avg_r:.3f}")
        print(f"  Average MAD: {avg_mad:.2f}")

    # Find dimensions with highest/lowest agreement
    print(f"\n{'='*120}")
    print("DIMENSIONS BY AGREEMENT")
    print(f"{'='*120}\n")

    # Calculate average correlation across all judge pairs per dimension
    dim_avg_corr = {}
    for dim in dimensions:
        corrs = []
        for judge1, judge2 in [p[:2] for p in judge_pairs]:
            pair_corr = results['correlations'].get((judge1, judge2), {})
            if dim in pair_corr:
                corrs.append(pair_corr[dim]['correlation'])
        if corrs:
            dim_avg_corr[dim] = sum(corrs) / len(corrs)

    sorted_dims = sorted(dim_avg_corr.items(), key=lambda x: x[1], reverse=True)

    print("Highest Agreement:")
    for dim, avg_r in sorted_dims[:5]:
        print(f"  {dim.capitalize()}: r = {avg_r:.3f}")

    print("\nLowest Agreement:")
    for dim, avg_r in sorted_dims[-5:]:
        print(f"  {dim.capitalize()}: r = {avg_r:.3f}")


if __name__ == "__main__":
    main()
