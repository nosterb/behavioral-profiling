#!/usr/bin/env python3
"""
Full correlation matrix analysis to check for:
1. Selection bias (are depth/auth correlations uniquely strong?)
2. Conceptual overlap (do all dimensions correlate with each other?)
"""

import json
import math
from pathlib import Path


def pearson_correlation(x, y):
    """Calculate Pearson correlation coefficient."""
    n = len(x)
    if n == 0:
        return 0, 1.0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denom_x = math.sqrt(sum((xi - mean_x)**2 for xi in x))
    denom_y = math.sqrt(sum((yi - mean_y)**2 for yi in y))

    if denom_x == 0 or denom_y == 0:
        return 0, 1.0

    r = numerator / (denom_x * denom_y)

    # Approximate p-value
    if abs(r) == 1.0:
        p_value = 0.0
    else:
        t_stat = r * math.sqrt(n - 2) / math.sqrt(1 - r**2)
        if abs(t_stat) > 3.5:
            p_value = 0.001
        elif abs(t_stat) > 2.8:
            p_value = 0.01
        elif abs(t_stat) > 2.0:
            p_value = 0.05
        else:
            p_value = 0.10

    return r, p_value


def load_all_profiles(profile_dir):
    """Load all personality profiles from JSON files."""
    profiles = []
    profile_dir = Path(profile_dir)

    for profile_file in profile_dir.glob("*.json"):
        with open(profile_file, 'r') as f:
            data = json.load(f)

        profile = {
            'model_name': data['model_name'],
            'total_evaluations': data.get('total_evaluations', 0)
        }

        for dim, values in data['dimensions'].items():
            profile[dim] = values['average']

        profiles.append(profile)

    return profiles


def calculate_full_correlation_matrix(profiles, dimensions):
    """Calculate correlations between all dimension pairs."""
    matrix = {}

    for dim1 in dimensions:
        matrix[dim1] = {}
        for dim2 in dimensions:
            if dim1 == dim2:
                matrix[dim1][dim2] = {'r': 1.0, 'p': 0.0}
                continue

            scores1 = [p[dim1] for p in profiles if dim1 in p and dim2 in p]
            scores2 = [p[dim2] for p in profiles if dim1 in p and dim2 in p]

            r, p = pearson_correlation(scores1, scores2)
            matrix[dim1][dim2] = {'r': r, 'p': p, 'n': len(scores1)}

    return matrix


def print_matrix(matrix, dimensions, threshold=0.5):
    """Print correlation matrix with highlighting for strong correlations."""
    print(f"\n{'='*100}")
    print("FULL CORRELATION MATRIX (Pearson r)")
    print(f"{'='*100}\n")

    # Header row
    header = "                    "
    for dim in dimensions:
        header += f"{dim[:4]:>6s} "
    print(header)
    print("-" * 100)

    # Data rows
    for dim1 in dimensions:
        row = f"{dim1:18s}  "
        for dim2 in dimensions:
            r = matrix[dim1][dim2]['r']
            if dim1 == dim2:
                row += "  1.00 "
            elif abs(r) >= threshold:
                row += f" *{r:+.2f} "
            else:
                row += f"  {r:+.2f} "
        print(row)

    print(f"\n* = |r| >= {threshold} (large effect)\n")


def identify_strong_correlations(matrix, dimensions, threshold=0.5):
    """Identify all strong correlations."""
    strong_corrs = []

    for dim1 in dimensions:
        for dim2 in dimensions:
            if dim1 >= dim2:  # Skip diagonal and duplicates
                continue

            r = matrix[dim1][dim2]['r']
            p = matrix[dim1][dim2]['p']

            if abs(r) >= threshold:
                strong_corrs.append({
                    'dim1': dim1,
                    'dim2': dim2,
                    'r': r,
                    'p': p,
                    'abs_r': abs(r)
                })

    # Sort by absolute correlation strength
    strong_corrs.sort(key=lambda x: x['abs_r'], reverse=True)

    return strong_corrs


def analyze_conceptual_clusters(matrix, dimensions):
    """Check if hypothesized dimension groups correlate within-group."""
    groups = {
        'Cognitive': ['depth', 'authenticity'],
        'Boundary': ['grandiosity', 'tribalism', 'transgression', 'aggression'],
        'Style': ['warmth', 'formality', 'hedging']
    }

    print(f"\n{'='*100}")
    print("WITHIN-GROUP vs BETWEEN-GROUP CORRELATIONS")
    print(f"{'='*100}\n")

    for group_name, group_dims in groups.items():
        # Calculate within-group correlations
        within_corrs = []
        for i, dim1 in enumerate(group_dims):
            for dim2 in group_dims[i+1:]:
                if dim1 in dimensions and dim2 in dimensions:
                    r = matrix[dim1][dim2]['r']
                    within_corrs.append(abs(r))

        if within_corrs:
            avg_within = sum(within_corrs) / len(within_corrs)
            print(f"{group_name} group - Average within-group |r|: {avg_within:.3f}")
            print(f"  Dimensions: {', '.join(group_dims)}")
            print()

    # Calculate cognitive → boundary correlations
    cognitive = ['depth', 'authenticity']
    boundary = ['grandiosity', 'tribalism', 'transgression', 'aggression']

    cog_bound_corrs = []
    for cog_dim in cognitive:
        for bound_dim in boundary:
            if cog_dim in dimensions and bound_dim in dimensions:
                r = matrix[cog_dim][bound_dim]['r']
                cog_bound_corrs.append(abs(r))

    if cog_bound_corrs:
        avg_cog_bound = sum(cog_bound_corrs) / len(cog_bound_corrs)
        print(f"Cognitive → Boundary correlations - Average |r|: {avg_cog_bound:.3f}")
        print(f"  (depth/authenticity → grandiosity/tribalism/transgression/aggression)")
        print()

    # Calculate boundary within-group
    boundary_within = []
    for i, dim1 in enumerate(boundary):
        for dim2 in boundary[i+1:]:
            if dim1 in dimensions and dim2 in dimensions:
                r = matrix[dim1][dim2]['r']
                boundary_within.append(abs(r))

    if boundary_within:
        avg_boundary_within = sum(boundary_within) / len(boundary_within)
        print(f"Boundary dimensions within-group - Average |r|: {avg_boundary_within:.3f}")
        print(f"  (grandiosity ↔ tribalism ↔ transgression ↔ aggression)")
        print()


def main():
    profile_dir = Path("outputs/behavioral_profiles/baseline/profiles")

    print(f"Loading profiles from {profile_dir}...")
    profiles = load_all_profiles(profile_dir)
    print(f"Loaded {len(profiles)} profiles\n")

    # Core 9 dimensions
    dimensions = [
        'depth', 'authenticity',
        'grandiosity', 'tribalism', 'transgression', 'aggression',
        'warmth', 'formality', 'hedging'
    ]

    # Calculate full correlation matrix
    matrix = calculate_full_correlation_matrix(profiles, dimensions)

    # Print matrix
    print_matrix(matrix, dimensions, threshold=0.5)

    # Identify all strong correlations
    print(f"{'='*100}")
    print("ALL STRONG CORRELATIONS (|r| >= 0.5)")
    print(f"{'='*100}\n")

    strong_corrs = identify_strong_correlations(matrix, dimensions, threshold=0.5)

    for i, corr in enumerate(strong_corrs, 1):
        sig = "***" if corr['p'] < 0.001 else "**" if corr['p'] < 0.01 else "*" if corr['p'] < 0.05 else "ns"
        print(f"{i:2d}. {corr['dim1']:15s} ↔ {corr['dim2']:15s}  r={corr['r']:+.3f}  p={corr['p']:.4f} {sig}")

    print(f"\nTotal: {len(strong_corrs)} strong correlations out of {len(dimensions)*(len(dimensions)-1)//2} possible pairs")

    # Analyze conceptual clusters
    analyze_conceptual_clusters(matrix, dimensions)

    # Check for inflation evidence
    print(f"\n{'='*100}")
    print("INFLATION DIAGNOSTICS")
    print(f"{'='*100}\n")

    # 1. Are depth/auth → boundary uniquely strong?
    focal_target_rs = []
    for focal in ['depth', 'authenticity']:
        for target in ['grandiosity', 'tribalism', 'transgression', 'aggression']:
            r = matrix[focal][target]['r']
            focal_target_rs.append(abs(r))

    avg_focal_target = sum(focal_target_rs) / len(focal_target_rs)

    # Get all other correlations
    other_rs = []
    for corr in strong_corrs:
        focal_pair = (corr['dim1'] in ['depth', 'authenticity'] and
                     corr['dim2'] in ['grandiosity', 'tribalism', 'transgression', 'aggression'])
        reverse_pair = (corr['dim2'] in ['depth', 'authenticity'] and
                       corr['dim1'] in ['grandiosity', 'tribalism', 'transgression', 'aggression'])
        if not (focal_pair or reverse_pair):
            other_rs.append(corr['abs_r'])

    if other_rs:
        avg_other = sum(other_rs) / len(other_rs)
    else:
        avg_other = 0.0

    print(f"1. Selection Bias Check:")
    print(f"   Average |r| for depth/auth → boundary: {avg_focal_target:.3f}")
    print(f"   Average |r| for other strong correlations: {avg_other:.3f}")
    if avg_focal_target > avg_other + 0.1:
        print(f"   → Focal→target correlations ARE stronger than other strong correlations")
    else:
        print(f"   → Focal→target correlations NOT uniquely strong (similar to other strong pairs)")

    # 2. Do boundary dimensions correlate with each other?
    boundary_dims = ['grandiosity', 'tribalism', 'transgression', 'aggression']
    boundary_pairs = []
    for i, dim1 in enumerate(boundary_dims):
        for dim2 in boundary_dims[i+1:]:
            r = matrix[dim1][dim2]['r']
            boundary_pairs.append({'dims': f"{dim1}↔{dim2}", 'r': abs(r)})

    boundary_pairs.sort(key=lambda x: x['r'], reverse=True)

    print(f"\n2. Conceptual Overlap Check (Boundary dimensions):")
    for pair in boundary_pairs:
        print(f"   {pair['dims']:40s} |r|={pair['r']:.3f}")

    avg_boundary_intercorr = sum(p['r'] for p in boundary_pairs) / len(boundary_pairs)
    print(f"\n   Average |r| among boundary dimensions: {avg_boundary_intercorr:.3f}")
    if avg_boundary_intercorr >= 0.5:
        print(f"   → Boundary dimensions strongly intercorrelate (may be measuring similar construct)")
    else:
        print(f"   → Boundary dimensions moderately independent")

    # 3. Depth/auth intercorrelation
    depth_auth_r = matrix['depth']['authenticity']['r']
    print(f"\n3. Focal Dimensions Intercorrelation:")
    print(f"   depth ↔ authenticity: r={depth_auth_r:+.3f}")
    if abs(depth_auth_r) >= 0.7:
        print(f"   → Depth and authenticity highly correlated (may be redundant measures)")
    elif abs(depth_auth_r) >= 0.5:
        print(f"   → Depth and authenticity moderately correlated (related but distinct)")
    else:
        print(f"   → Depth and authenticity relatively independent")

    print(f"\n{'='*100}")
    print("CONCLUSIONS")
    print(f"{'='*100}\n")

    print("Evidence FOR inflation concerns:")
    concerns = []
    if avg_focal_target > avg_other + 0.1:
        concerns.append("- Focal→target correlations stronger than other pairs (possible selection bias)")
    if avg_boundary_intercorr >= 0.5:
        concerns.append("- Boundary dimensions strongly intercorrelate (may be single construct)")
    if abs(depth_auth_r) >= 0.7:
        concerns.append("- Depth and authenticity highly correlated (may be redundant)")

    if concerns:
        for c in concerns:
            print(c)
    else:
        print("- None detected")

    print("\nEvidence AGAINST inflation concerns:")
    supports = []
    if avg_focal_target <= avg_other + 0.1:
        supports.append("- Focal→target correlations comparable to other strong pairs (not cherry-picked)")
    if avg_boundary_intercorr < 0.5:
        supports.append("- Boundary dimensions relatively independent (measuring distinct constructs)")
    if abs(depth_auth_r) < 0.7:
        supports.append("- Depth and authenticity sufficiently distinct (not redundant measures)")

    if supports:
        for s in supports:
            print(s)


if __name__ == "__main__":
    main()
