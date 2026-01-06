#!/usr/bin/env python3
"""
Post-processing utilities for judge evaluation results.

This module provides functions to analyze and transform judge evaluation results
after the core evaluation is complete. Each function is designed for specific
use cases (e.g., behavioral profiling studies, intervention studies) and can be selectively
applied via configuration.
"""

from typing import Dict, List, Any, Optional


def calculate_dimension_averages(
    evaluations: List[Dict[str, Any]],
    comparative_analysis: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Calculate averaged scores across dimensions for behavioral profiling studies.

    This post-processor expects judges to return structured scores with named
    dimensions (e.g., "warmth", "dominance", "identity"). It averages scores
    across ONLY the Pass 1 judges (typically 3 independent judges).

    IMPORTANT: The comparative judge is NOT included in the averaging to prevent
    score convergence. Comparative judge provides qualitative analysis only.

    Args:
        evaluations: List of model evaluations with pass1_judges
        comparative_analysis: Optional comparative judge results (NOT used in averaging)

    Returns:
        Updated evaluations list with 'final_averaged_scores' added to each model

    Example structure:
        final_averaged_scores: {
            'scores': {'warmth': 7.5, 'dominance': 4.2},
            'num_judges': 3,  # Only Pass 1 judges
            'dimensions': ['warmth', 'dominance']
        }
    """
    # NOTE: comparative_analysis parameter is accepted for compatibility but NOT used
    # We only average Pass 1 judges to prevent score convergence

    for i, model_eval in enumerate(evaluations):
        # Collect all judge scores for this model
        all_judge_scores = []

        # Extract scores from Pass 1 judges ONLY
        for judge_eval in model_eval.get('pass1_judges', []):
            extracted = judge_eval.get('extracted_json', {})
            if 'scores' in extracted:
                all_judge_scores.append(extracted['scores'])

        # DO NOT add comparative judge - it's for qualitative analysis only

        # If no scores found, skip this model
        if not all_judge_scores:
            continue

        # Calculate averages for each dimension
        # First, collect all dimensions across all judges
        all_dimensions = set()
        for scores in all_judge_scores:
            all_dimensions.update(scores.keys())

        # Calculate average for each dimension
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

    return evaluations


def post_process_results(
    evaluations: List[Dict[str, Any]],
    comparative_analysis: Optional[Dict[str, Any]] = None,
    processors: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Apply post-processing functions to judge evaluation results.

    Args:
        evaluations: List of model evaluations
        comparative_analysis: Optional comparative judge results
        processors: List of processor names to apply (default: none)

    Available processors:
        - 'dimension_averages': Calculate averaged scores across judge dimensions

    Returns:
        Updated evaluations list with post-processing applied
    """
    if not processors:
        return evaluations

    # Apply requested processors
    for processor_name in processors:
        if processor_name == 'dimension_averages':
            evaluations = calculate_dimension_averages(evaluations, comparative_analysis)
        else:
            print(f"Warning: Unknown post-processor '{processor_name}' - skipping")

    return evaluations
