#!/usr/bin/env python3
"""
Extract representative qualitative examples from job data.

Creates an inventory of responses organized by behavioral characteristics:
- Dimension extremes (min/max per dimension)
- Composite extremes (sophistication, disinhibition)
- Distribution percentiles (5th, 25th, 50th, 75th, 95th)
- Pattern types (constrained, outlier, borderline)

Output: qualitative_examples.json + chat exports per condition
"""

import json
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple
import textwrap

# Behavioral dimensions
DIMENSIONS = ['warmth', 'formality', 'hedging', 'aggression', 'transgression',
              'grandiosity', 'tribalism', 'depth', 'authenticity']

DISINHIBITION_DIMS = ['transgression', 'aggression', 'tribalism', 'grandiosity']
SOPHISTICATION_DIMS = ['depth', 'authenticity']

# Thresholds (matching create_h2_color_coded_scatters.py)
BORDERLINE_THRESHOLD = 0.15
OUTLIER_SD_THRESHOLD = 2.0
CONSTRAINED_SOPH_THRESHOLD = 6.5
CONSTRAINED_RESIDUAL_THRESHOLD = -0.15

# Sample size per category
TOP_N = 5


def compute_composites(scores: Dict[str, float]) -> Tuple[float, float]:
    """Compute sophistication and disinhibition composites."""
    sophistication = np.mean([scores.get(d, 0) for d in SOPHISTICATION_DIMS])
    disinhibition = np.mean([scores.get(d, 0) for d in DISINHIBITION_DIMS])
    return sophistication, disinhibition


def normalize_model_name(name: str) -> str:
    """Normalize model name for matching."""
    return name.lower().replace(' ', '-').replace('_(thinking)', '-thinking').replace('(thinking)', '-thinking')


def get_condition_job_filter(condition: str):
    """Return a filter function for job files based on condition."""
    if condition == 'baseline':
        # Baseline = no intervention suffix
        intervention_suffixes = ['_authority', '_urgency', '_reminder', '_minimal_steering', '_telemetryV3']
        def filter_fn(job_name: str) -> bool:
            return not any(suffix in job_name for suffix in intervention_suffixes)
        return filter_fn
    else:
        # Other conditions have suffix
        suffix = f'_{condition}'
        def filter_fn(job_name: str) -> bool:
            return suffix in job_name
        return filter_fn


def scan_jobs_for_condition(condition: str) -> List[Dict[str, Any]]:
    """Scan all job files and extract evaluations for a condition."""
    base_dir = Path("outputs/single_prompt_jobs")
    evaluations = []

    job_filter = get_condition_job_filter(condition)

    # Find all JSON files
    for job_file in base_dir.rglob("*.json"):
        if not job_filter(job_file.stem):
            continue

        try:
            with open(job_file) as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        # Check for judge_evaluation
        if 'judge_evaluation' not in data:
            continue

        je = data['judge_evaluation']

        # Handle different judge evaluation structures
        if 'evaluations' in je:
            evals = je['evaluations']
        elif 'pass1_evaluations' in je:
            # Older format - need to restructure
            continue
        else:
            continue

        prompt = data.get('prompt', '')
        job_id = data.get('job_metadata', {}).get('payload_name', job_file.stem)

        # Build model_id -> response lookup from models array
        # (some jobs store response there instead of in judge_evaluation)
        models_lookup = {}
        for m in data.get('models', []):
            if m.get('model_id') and m.get('response'):
                models_lookup[m['model_id']] = m['response']

        for eval_data in evals:
            if 'final_averaged_scores' not in eval_data:
                continue

            scores = eval_data['final_averaged_scores'].get('scores', {})
            if not scores:
                continue

            # Get model response - try eval_data first, then models array lookup
            model_id = eval_data.get('model_id', '')
            response = eval_data.get('model_response', '')
            if not response and model_id in models_lookup:
                response = models_lookup[model_id]

            # Skip evaluations with empty responses (failed invocations)
            if not response or not response.strip():
                continue

            # Compute composites
            sophistication, disinhibition = compute_composites(scores)

            # Extract judge rationales
            pass1_rationales = []
            for judge in eval_data.get('pass1_judges', []):
                if 'raw_evaluation' in judge:
                    pass1_rationales.append(judge['raw_evaluation'])
                elif 'extracted_json' in judge:
                    ej = judge['extracted_json']
                    if isinstance(ej, dict) and 'rationale' in ej:
                        pass1_rationales.append(ej['rationale'])

            pass2 = eval_data.get('pass2_comparative', {})
            pass2_rationale = ''
            if isinstance(pass2, dict):
                pass2_rationale = pass2.get('raw_evaluation', pass2.get('comparative_analysis', ''))

            evaluation = {
                'model_id': model_id,
                'display_name': eval_data.get('display_name', ''),
                'response': response,
                'prompt': prompt,
                'scores': scores,
                'sophistication': sophistication,
                'disinhibition': disinhibition,
                'source_job': str(job_file),
                'job_id': job_id,
                'judge_rationales': {
                    'pass1': pass1_rationales,
                    'pass2_comparative': pass2_rationale
                }
            }
            evaluations.append(evaluation)

    return evaluations


def identify_dimension_extremes(evaluations: List[Dict], dimension: str, n: int = TOP_N) -> Dict[str, List[Dict]]:
    """Identify top N max and min for a dimension."""
    # Filter to valid scores
    valid = [e for e in evaluations if dimension in e['scores']]

    sorted_by_dim = sorted(valid, key=lambda x: x['scores'][dimension])

    return {
        f'{dimension}_min': sorted_by_dim[:n],
        f'{dimension}_max': sorted_by_dim[-n:][::-1]  # Reverse to get highest first
    }


def identify_composite_extremes(evaluations: List[Dict], n: int = TOP_N) -> Dict[str, List[Dict]]:
    """Identify extremes for sophistication and disinhibition composites."""
    sorted_by_soph = sorted(evaluations, key=lambda x: x['sophistication'])
    sorted_by_disinhib = sorted(evaluations, key=lambda x: x['disinhibition'])

    return {
        'sophistication_min': sorted_by_soph[:n],
        'sophistication_max': sorted_by_soph[-n:][::-1],
        'disinhibition_min': sorted_by_disinhib[:n],
        'disinhibition_max': sorted_by_disinhib[-n:][::-1]
    }


def identify_percentiles(evaluations: List[Dict], n: int = TOP_N) -> Dict[str, List[Dict]]:
    """Identify examples at key percentiles of disinhibition distribution."""
    if not evaluations:
        return {}

    disinhibition_values = [e['disinhibition'] for e in evaluations]

    percentile_targets = [5, 25, 50, 75, 95]
    results = {}

    for pct in percentile_targets:
        target_value = np.percentile(disinhibition_values, pct)

        # Sort by distance from target
        sorted_by_distance = sorted(evaluations,
                                    key=lambda x: abs(x['disinhibition'] - target_value))

        results[f'percentile_{pct}'] = sorted_by_distance[:n]

    return results


def identify_pattern_types(evaluations: List[Dict], condition: str, n: int = TOP_N) -> Dict[str, List[Dict]]:
    """Identify constrained, outlier, and borderline models."""
    if not evaluations:
        return {}

    # Load median split data if available
    median_split_path = Path(f"outputs/behavioral_profiles/{condition}/median_split_classification.json")
    median_soph = None
    if median_split_path.exists():
        with open(median_split_path) as f:
            ms_data = json.load(f)
            median_soph = ms_data.get('median_sophistication')

    # Calculate regression for outlier/constrained detection
    all_x = [e['sophistication'] for e in evaluations]
    all_y = [e['disinhibition'] for e in evaluations]

    if len(all_x) < 3:
        return {}

    z = np.polyfit(all_x, all_y, 1)
    p = np.poly1d(z)
    predicted = p(all_x)
    residuals = np.array(all_y) - predicted
    residual_std = np.std(residuals)

    # Add residual info to evaluations
    for i, e in enumerate(evaluations):
        e['_residual'] = residuals[i]
        e['_sd_from_line'] = residuals[i] / residual_std if residual_std > 0 else 0

    # Identify patterns
    constrained = []
    outliers = []
    borderline = []

    for e in evaluations:
        # Constrained: high sophistication, below-predicted disinhibition
        if e['sophistication'] > CONSTRAINED_SOPH_THRESHOLD and e['_residual'] < CONSTRAINED_RESIDUAL_THRESHOLD:
            constrained.append(e)

        # Outlier: residual > 2 SD
        if abs(e['_sd_from_line']) > OUTLIER_SD_THRESHOLD:
            outliers.append(e)

        # Borderline: close to median sophistication
        if median_soph and abs(e['sophistication'] - median_soph) < BORDERLINE_THRESHOLD:
            borderline.append(e)

    # Sort and limit
    constrained = sorted(constrained, key=lambda x: x['_residual'])[:n]  # Most negative residual first
    outliers = sorted(outliers, key=lambda x: abs(x['_sd_from_line']), reverse=True)[:n]
    borderline = sorted(borderline, key=lambda x: abs(x['sophistication'] - (median_soph or 0)))[:n]

    return {
        'constrained': constrained,
        'outlier': outliers,
        'borderline': borderline
    }


def build_inventory(condition: str, evaluations: List[Dict]) -> Dict[str, Any]:
    """Build the complete qualitative examples inventory."""

    # Track all categories per example
    example_categories = defaultdict(list)  # id -> list of categories

    # Dimension extremes
    dimension_extremes = {}
    for dim in DIMENSIONS:
        extremes = identify_dimension_extremes(evaluations, dim)
        for cat_name, examples in extremes.items():
            dimension_extremes[cat_name] = [e['model_id'] + '_' + e['job_id'] for e in examples]
            for i, e in enumerate(examples):
                example_id = e['model_id'] + '_' + e['job_id']
                example_categories[example_id].append({
                    'type': 'dimension_extreme',
                    'dimension': dim,
                    'rank': 'max' if 'max' in cat_name else 'min',
                    'position': i + 1
                })

    # Composite extremes
    composite_extremes = {}
    comp_results = identify_composite_extremes(evaluations)
    for cat_name, examples in comp_results.items():
        composite_extremes[cat_name] = [e['model_id'] + '_' + e['job_id'] for e in examples]
        for i, e in enumerate(examples):
            example_id = e['model_id'] + '_' + e['job_id']
            composite = 'sophistication' if 'sophistication' in cat_name else 'disinhibition'
            example_categories[example_id].append({
                'type': 'composite_extreme',
                'composite': composite,
                'rank': 'max' if 'max' in cat_name else 'min',
                'position': i + 1
            })

    # Percentiles
    percentiles = {}
    pct_results = identify_percentiles(evaluations)
    for cat_name, examples in pct_results.items():
        percentiles[cat_name] = [e['model_id'] + '_' + e['job_id'] for e in examples]
        pct_value = int(cat_name.split('_')[1])
        for i, e in enumerate(examples):
            example_id = e['model_id'] + '_' + e['job_id']
            example_categories[example_id].append({
                'type': 'percentile',
                'percentile': pct_value,
                'position': i + 1
            })

    # Pattern types
    pattern_types = {}
    pattern_results = identify_pattern_types(evaluations, condition)
    for cat_name, examples in pattern_results.items():
        pattern_types[cat_name] = [e['model_id'] + '_' + e['job_id'] for e in examples]
        for i, e in enumerate(examples):
            example_id = e['model_id'] + '_' + e['job_id']
            example_categories[example_id].append({
                'type': 'pattern_type',
                'pattern': cat_name,
                'position': i + 1
            })

    # Build final examples list (only those that appear in at least one category)
    examples = []
    seen_ids = set()

    for e in evaluations:
        example_id = e['model_id'] + '_' + e['job_id']
        if example_id in example_categories and example_id not in seen_ids:
            seen_ids.add(example_id)

            # Clean up temporary fields
            example_data = {k: v for k, v in e.items() if not k.startswith('_')}
            example_data['id'] = example_id
            example_data['categories'] = example_categories[example_id]
            examples.append(example_data)

    # Sort by number of category appearances (most interesting first)
    examples.sort(key=lambda x: len(x['categories']), reverse=True)

    # Count total category appearances
    total_appearances = sum(len(e['categories']) for e in examples)

    return {
        'generated': datetime.now().isoformat(),
        'condition': condition,
        'summary': {
            'total_unique_examples': len(examples),
            'total_category_appearances': total_appearances,
            'evaluations_scanned': len(evaluations)
        },
        'examples': examples,
        'category_index': {
            'dimension_extremes': dimension_extremes,
            'composite_extremes': composite_extremes,
            'percentiles': percentiles,
            'pattern_types': pattern_types
        }
    }


def export_chat(example: Dict, output_path: Path):
    """Export a single example as a chat markdown file."""

    def wrap_text(text, width=100):
        if not text:
            return ""
        lines = text.split('\n')
        wrapped_lines = []
        for line in lines:
            if len(line) > width:
                wrapped_lines.extend(textwrap.wrap(line, width=width))
            else:
                wrapped_lines.append(line)
        return '\n'.join(wrapped_lines)

    content = []
    content.append(f"# Qualitative Example: {example['display_name']}")
    content.append(f"\n**ID**: `{example['id']}`")
    content.append(f"**Source**: `{example['source_job']}`")
    content.append(f"**Job ID**: `{example['job_id']}`")

    # Categories
    content.append("\n## Categories")
    for cat in example['categories']:
        if cat['type'] == 'dimension_extreme':
            content.append(f"- **{cat['dimension'].capitalize()} {cat['rank'].upper()}** (#{cat['position']})")
        elif cat['type'] == 'composite_extreme':
            content.append(f"- **{cat['composite'].capitalize()} {cat['rank'].upper()}** (#{cat['position']})")
        elif cat['type'] == 'percentile':
            content.append(f"- **Percentile {cat['percentile']}** (#{cat['position']})")
        elif cat['type'] == 'pattern_type':
            content.append(f"- **Pattern: {cat['pattern'].capitalize()}** (#{cat['position']})")

    # Scores
    content.append("\n## Behavioral Scores")
    content.append(f"- **Sophistication**: {example['sophistication']:.2f}")
    content.append(f"- **Disinhibition**: {example['disinhibition']:.2f}")
    content.append("\n| Dimension | Score |")
    content.append("|-----------|-------|")
    for dim in DIMENSIONS:
        score = example['scores'].get(dim, 'N/A')
        if isinstance(score, (int, float)):
            content.append(f"| {dim.capitalize()} | {score:.2f} |")
        else:
            content.append(f"| {dim.capitalize()} | {score} |")

    # Prompt
    content.append("\n## Prompt")
    content.append("```")
    content.append(wrap_text(example['prompt']))
    content.append("```")

    # Response
    content.append("\n## Response")
    content.append("```")
    content.append(wrap_text(example['response']))
    content.append("```")

    # Judge rationales
    content.append("\n## Judge Evaluations")
    rationales = example.get('judge_rationales', {})

    pass1 = rationales.get('pass1', [])
    if pass1:
        for i, r in enumerate(pass1, 1):
            content.append(f"\n### Pass 1 - Judge {i}")
            content.append("```")
            content.append(wrap_text(str(r)[:2000]))  # Truncate very long rationales
            content.append("```")

    pass2 = rationales.get('pass2_comparative', '')
    if pass2:
        content.append("\n### Pass 2 - Comparative")
        content.append("```")
        content.append(wrap_text(str(pass2)[:2000]))
        content.append("```")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(content))


def export_all_chats(inventory: Dict, base_output_dir: Path):
    """Export all examples as chat files, organized by category."""

    examples_by_id = {e['id']: e for e in inventory['examples']}

    # Export by category
    for cat_type, categories in inventory['category_index'].items():
        for cat_name, example_ids in categories.items():
            cat_dir = base_output_dir / cat_type / cat_name

            for i, example_id in enumerate(example_ids, 1):
                if example_id not in examples_by_id:
                    continue

                example = examples_by_id[example_id]
                safe_name = example['display_name'].replace(' ', '_').replace('/', '-')
                filename = f"{i:02d}_{safe_name}_{example['job_id']}.md"

                export_chat(example, cat_dir / filename)

    print(f"  Exported chats to: {base_output_dir}")


def process_condition(condition: str, force: bool = False):
    """Process a single condition."""
    output_dir = Path(f"outputs/behavioral_profiles/{condition}")
    inventory_path = output_dir / "qualitative_examples.json"
    chats_dir = output_dir / "qualitative_chats"

    if inventory_path.exists() and not force:
        print(f"Skipping {condition} (already exists, use --force to overwrite)")
        return

    # Clean up old outputs if forcing
    if force:
        if chats_dir.exists():
            import shutil
            shutil.rmtree(chats_dir)

    print(f"\nProcessing condition: {condition}")

    # Scan jobs
    print("  Scanning job files...")
    evaluations = scan_jobs_for_condition(condition)
    print(f"  Found {len(evaluations)} evaluations")

    if not evaluations:
        print(f"  WARNING: No evaluations found for {condition}")
        return

    # Build inventory
    print("  Building inventory...")
    inventory = build_inventory(condition, evaluations)

    # Save inventory JSON
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(inventory_path, 'w') as f:
        json.dump(inventory, f, indent=2)
    print(f"  Wrote: {inventory_path}")
    print(f"  - Unique examples: {inventory['summary']['total_unique_examples']}")
    print(f"  - Category appearances: {inventory['summary']['total_category_appearances']}")

    # Export chats
    print("  Exporting chat files...")
    export_all_chats(inventory, chats_dir)


def main():
    parser = argparse.ArgumentParser(description="Extract qualitative examples from job data")
    parser.add_argument('condition', nargs='?', help="Condition to process (e.g., baseline, authority)")
    parser.add_argument('--all', action='store_true', help="Process all conditions")
    parser.add_argument('--force', action='store_true', help="Overwrite existing files")

    args = parser.parse_args()

    if args.all:
        # Find all conditions
        base_dir = Path("outputs/behavioral_profiles")
        conditions = []
        for d in sorted(base_dir.iterdir()):
            if d.is_dir() and d.name != "research_synthesis":
                if (d / "median_split_classification.json").exists():
                    conditions.append(d.name)

        print(f"Processing {len(conditions)} conditions: {', '.join(conditions)}")
        for condition in conditions:
            process_condition(condition, args.force)
    elif args.condition:
        process_condition(args.condition, args.force)
    else:
        parser.print_help()
        return

    print("\nDone!")


if __name__ == "__main__":
    main()
