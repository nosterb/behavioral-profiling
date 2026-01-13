#!/usr/bin/env python3
"""
Analyze qualitative examples to find patterns in prompts/scenarios that create
high sophistication and high disinhibition.
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

def extract_scenario_from_job_id(job_id: str) -> str:
    """
    Extract scenario identifier from job_id.
    Examples:
    - job_broad_1_20250104 -> broad_1
    - job_affective_5_urgency_20250105 -> affective_5
    - job_dimensions_3_authority_20250106 -> dimensions_3
    """
    # Remove job_ prefix and date suffix
    match = re.search(r'job_([a-z_]+_\d+)', job_id)
    if match:
        return match.group(1)

    # Fallback: try to extract suite_number pattern
    match = re.search(r'([a-z_]+_\d+)', job_id)
    if match:
        return match.group(1)

    return job_id

def analyze_condition(condition_path: Path) -> Dict:
    """Analyze qualitative examples for a single condition."""
    with open(condition_path, 'r') as f:
        data = json.load(f)

    condition_name = condition_path.parent.name

    results = {
        'condition': condition_name,
        'sophistication_scenarios': [],
        'disinhibition_scenarios': [],
        'sophistication_values': [],
        'disinhibition_values': []
    }

    # Get the examples list
    examples = data.get('examples', [])

    # Build a lookup dict by example ID
    examples_by_id = {ex['id']: ex for ex in examples}

    # Extract sophistication_max examples from category_index
    category_index = data.get('category_index', {})
    composite_extremes = category_index.get('composite_extremes', {})

    if 'sophistication_max' in composite_extremes:
        for example_id in composite_extremes['sophistication_max']:
            if example_id in examples_by_id:
                example = examples_by_id[example_id]
                job_id = example.get('job_id', '')
                scenario = extract_scenario_from_job_id(job_id)
                sophistication = example.get('sophistication', 0)

                results['sophistication_scenarios'].append(scenario)
                results['sophistication_values'].append(sophistication)

    # Extract disinhibition_max examples
    if 'disinhibition_max' in composite_extremes:
        for example_id in composite_extremes['disinhibition_max']:
            if example_id in examples_by_id:
                example = examples_by_id[example_id]
                job_id = example.get('job_id', '')
                scenario = extract_scenario_from_job_id(job_id)
                disinhibition = example.get('disinhibition', 0)

                results['disinhibition_scenarios'].append(scenario)
                results['disinhibition_values'].append(disinhibition)

    return results

def main():
    base_dir = Path('/Users/nicholasosterbur/Desktop/Workspace/behavioral-profiling/outputs/behavioral_profiles')

    # Find all qualitative_examples.json files
    qual_files = list(base_dir.glob('*/qualitative_examples.json'))

    print(f"Found {len(qual_files)} qualitative examples files\n")

    # Aggregate data across all conditions
    all_sophistication_scenarios = []
    all_disinhibition_scenarios = []

    condition_stats = []

    for qual_file in sorted(qual_files):
        results = analyze_condition(qual_file)

        all_sophistication_scenarios.extend(results['sophistication_scenarios'])
        all_disinhibition_scenarios.extend(results['disinhibition_scenarios'])

        condition_stats.append({
            'condition': results['condition'],
            'mean_sophistication': sum(results['sophistication_values']) / len(results['sophistication_values']) if results['sophistication_values'] else 0,
            'max_sophistication': max(results['sophistication_values']) if results['sophistication_values'] else 0,
            'mean_disinhibition': sum(results['disinhibition_values']) / len(results['disinhibition_values']) if results['disinhibition_values'] else 0,
            'max_disinhibition': max(results['disinhibition_values']) if results['disinhibition_values'] else 0,
            'n_sophistication_examples': len(results['sophistication_values']),
            'n_disinhibition_examples': len(results['disinhibition_values'])
        })

    # Count scenario frequencies
    sophistication_counts = Counter(all_sophistication_scenarios)
    disinhibition_counts = Counter(all_disinhibition_scenarios)

    # Print results
    print("=" * 80)
    print("TOP 10 SCENARIOS PRODUCING HIGH SOPHISTICATION")
    print("=" * 80)
    for scenario, count in sophistication_counts.most_common(10):
        print(f"{scenario:30s} - {count:3d} occurrences")

    print("\n" + "=" * 80)
    print("TOP 10 SCENARIOS PRODUCING HIGH DISINHIBITION")
    print("=" * 80)
    for scenario, count in disinhibition_counts.most_common(10):
        print(f"{scenario:30s} - {count:3d} occurrences")

    print("\n" + "=" * 80)
    print("CONDITION-LEVEL STATISTICS (High-Scoring Examples)")
    print("=" * 80)

    # Sort by mean sophistication
    print("\nBy Mean Sophistication (in extreme examples):")
    for stat in sorted(condition_stats, key=lambda x: x['mean_sophistication'], reverse=True):
        print(f"{stat['condition']:20s} - Mean: {stat['mean_sophistication']:.2f}, Max: {stat['max_sophistication']:.2f}, N={stat['n_sophistication_examples']}")

    # Sort by mean disinhibition
    print("\nBy Mean Disinhibition (in extreme examples):")
    for stat in sorted(condition_stats, key=lambda x: x['mean_disinhibition'], reverse=True):
        print(f"{stat['condition']:20s} - Mean: {stat['mean_disinhibition']:.2f}, Max: {stat['max_disinhibition']:.2f}, N={stat['n_disinhibition_examples']}")

    # Pattern analysis
    print("\n" + "=" * 80)
    print("PATTERN ANALYSIS")
    print("=" * 80)

    # Analyze scenario suites (broad, affective, dimensions, general)
    suite_sophistication = defaultdict(int)
    suite_disinhibition = defaultdict(int)

    for scenario in all_sophistication_scenarios:
        suite = scenario.split('_')[0] if '_' in scenario else scenario
        suite_sophistication[suite] += 1

    for scenario in all_disinhibition_scenarios:
        suite = scenario.split('_')[0] if '_' in scenario else scenario
        suite_disinhibition[suite] += 1

    print("\nScenario Suite Frequencies (High Sophistication):")
    for suite, count in sorted(suite_sophistication.items(), key=lambda x: x[1], reverse=True):
        print(f"  {suite:20s} - {count:3d} occurrences")

    print("\nScenario Suite Frequencies (High Disinhibition):")
    for suite, count in sorted(suite_disinhibition.items(), key=lambda x: x[1], reverse=True):
        print(f"  {suite:20s} - {count:3d} occurrences")

    # Look for scenarios that appear in both lists frequently
    print("\n" + "=" * 80)
    print("SCENARIOS PRODUCING BOTH HIGH SOPHISTICATION AND HIGH DISINHIBITION")
    print("=" * 80)

    both_high = {}
    for scenario in set(all_sophistication_scenarios) & set(all_disinhibition_scenarios):
        soph_count = sophistication_counts[scenario]
        disinhib_count = disinhibition_counts[scenario]
        both_high[scenario] = (soph_count, disinhib_count, soph_count + disinhib_count)

    for scenario, (soph, disinhib, total) in sorted(both_high.items(), key=lambda x: x[1][2], reverse=True)[:10]:
        print(f"{scenario:30s} - Soph: {soph:2d}, Disinhib: {disinhib:2d}, Total: {total:2d}")

    # Save detailed results
    output_path = base_dir / 'research_synthesis' / 'limitations' / 'prompt_design' / 'qualitative_pattern_analysis.json'
    output_data = {
        'top_sophistication_scenarios': [
            {'scenario': s, 'count': c} for s, c in sophistication_counts.most_common(20)
        ],
        'top_disinhibition_scenarios': [
            {'scenario': s, 'count': c} for s, c in disinhibition_counts.most_common(20)
        ],
        'condition_statistics': condition_stats,
        'suite_analysis': {
            'sophistication': dict(suite_sophistication),
            'disinhibition': dict(suite_disinhibition)
        },
        'scenarios_high_on_both': [
            {'scenario': s, 'sophistication_count': c[0], 'disinhibition_count': c[1]}
            for s, c in sorted(both_high.items(), key=lambda x: x[1][2], reverse=True)
        ]
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n\nDetailed results saved to: {output_path}")

if __name__ == '__main__':
    main()
