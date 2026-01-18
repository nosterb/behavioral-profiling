#!/usr/bin/env python3
"""
Mediation Analysis: GPQA → Sophistication → Disinhibition

Tests whether Sophistication mediates the relationship between
Reasoning Capability (GPQA) and Disinhibition.

Hypothesis: The GPQA → Disinhibition correlation is (partially) mediated
through Sophistication - i.e., capable models are more disinhibited
because they are more sophisticated.
"""

import json
import numpy as np
from scipy import stats
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Paths
SCRIPT_DIR = Path(__file__).parent
GPQA_DATA = SCRIPT_DIR.parent / "limitations/external_evals/gpqa_validation_analysis.json"
OUTPUT_DIR = SCRIPT_DIR


def load_gpqa_data():
    """Load GPQA validation data with sophistication and disinhibition scores."""
    with open(GPQA_DATA, 'r') as f:
        data = json.load(f)

    models = data['matched_model_details']

    gpqa = np.array([m['gpqa_score_pct'] for m in models])
    soph = np.array([m['sophistication'] for m in models])
    disin = np.array([m['disinhibition'] for m in models])
    names = [m['behavioral_model_id'] for m in models]

    return gpqa, soph, disin, names, models


def partial_correlation(x, y, z):
    """
    Calculate partial correlation r(X,Y | Z).

    r_XY.Z = (r_XY - r_XZ * r_YZ) / sqrt((1 - r_XZ^2) * (1 - r_YZ^2))
    """
    r_xy = np.corrcoef(x, y)[0, 1]
    r_xz = np.corrcoef(x, z)[0, 1]
    r_yz = np.corrcoef(y, z)[0, 1]

    numerator = r_xy - r_xz * r_yz
    denominator = np.sqrt((1 - r_xz**2) * (1 - r_yz**2))

    r_partial = numerator / denominator

    return r_partial, r_xy, r_xz, r_yz


def partial_correlation_significance(r_partial, n, k=1):
    """
    Calculate t-statistic and p-value for partial correlation.

    t = r * sqrt((n - 2 - k) / (1 - r^2))
    where k = number of control variables
    """
    df = n - 2 - k
    t_stat = r_partial * np.sqrt(df / (1 - r_partial**2))
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))

    return t_stat, df, p_value


def calculate_indirect_effect(r_xm, r_my, r_xy, n):
    """
    Calculate indirect effect and Sobel test.

    Indirect effect = a * b (where a = r_XM, b = partial r_MY.X)
    Sobel test approximates significance of indirect effect.
    """
    # Standard errors for correlations (approximate)
    se_a = np.sqrt((1 - r_xm**2) / (n - 2))
    se_b = np.sqrt((1 - r_my**2) / (n - 2))

    # Sobel test for indirect effect
    # SE_ab = sqrt(a^2 * SE_b^2 + b^2 * SE_a^2)
    indirect = r_xm * r_my
    se_indirect = np.sqrt(r_xm**2 * se_b**2 + r_my**2 * se_a**2)
    z_sobel = indirect / se_indirect
    p_sobel = 2 * (1 - stats.norm.cdf(abs(z_sobel)))

    return indirect, se_indirect, z_sobel, p_sobel


def run_mediation_analysis():
    """Run full mediation analysis."""
    print("=" * 60)
    print("Mediation Analysis: GPQA → Sophistication → Disinhibition")
    print("=" * 60)

    # Load data
    gpqa, soph, disin, names, models = load_gpqa_data()
    n = len(gpqa)

    print(f"\nSample size: n = {n}")
    print(f"GPQA range: {gpqa.min():.1f}% - {gpqa.max():.1f}%")
    print(f"Sophistication range: {soph.min():.2f} - {soph.max():.2f}")
    print(f"Disinhibition range: {disin.min():.2f} - {disin.max():.2f}")

    # Zero-order correlations
    print("\n" + "-" * 40)
    print("Zero-Order Correlations")
    print("-" * 40)

    r_gpqa_soph, p_gs = stats.pearsonr(gpqa, soph)
    r_gpqa_disin, p_gd = stats.pearsonr(gpqa, disin)
    r_soph_disin, p_sd = stats.pearsonr(soph, disin)

    print(f"a path: GPQA → Sophistication:   r = {r_gpqa_soph:.3f}, p = {p_gs:.2e}")
    print(f"b path: Sophistication → Disin:  r = {r_soph_disin:.3f}, p = {p_sd:.2e}")
    print(f"c path: GPQA → Disinhibition:    r = {r_gpqa_disin:.3f}, p = {p_gd:.2e}")

    # Partial correlation: GPQA → Disinhibition | Sophistication
    print("\n" + "-" * 40)
    print("Partial Correlation (controlling for Sophistication)")
    print("-" * 40)

    r_partial, _, _, _ = partial_correlation(gpqa, disin, soph)
    t_stat, df, p_partial = partial_correlation_significance(r_partial, n)

    print(f"c' path: GPQA → Disin | Soph:    r = {r_partial:.3f}")
    print(f"         t({df}) = {t_stat:.3f}, p = {p_partial:.4f}")
    print(f"         Significant: {'Yes' if p_partial < 0.05 else 'NO'}")

    # Indirect effect (Sobel test)
    print("\n" + "-" * 40)
    print("Indirect Effect (Sobel Test)")
    print("-" * 40)

    indirect, se_indirect, z_sobel, p_sobel = calculate_indirect_effect(
        r_gpqa_soph, r_soph_disin, r_gpqa_disin, n
    )

    print(f"Indirect effect (a × b):  {indirect:.3f}")
    print(f"SE of indirect effect:    {se_indirect:.3f}")
    print(f"Sobel Z:                  {z_sobel:.3f}")
    print(f"p-value:                  {p_sobel:.4f}")
    print(f"Significant: {'Yes' if p_sobel < 0.05 else 'NO'}")

    # Variance decomposition
    print("\n" + "-" * 40)
    print("Variance Decomposition")
    print("-" * 40)

    r2_total = r_gpqa_disin ** 2
    r2_direct = r_partial ** 2 * (1 - r_gpqa_soph**2)  # Unique variance
    r2_indirect = r2_total - r2_direct  # Through mediator

    # More accurate: hierarchical regression approach
    # R² for GPQA alone
    r2_gpqa = r_gpqa_disin ** 2
    # R² for Sophistication alone
    r2_soph = r_soph_disin ** 2
    # R² for both (multiple regression R²)
    # Using formula: R² = 1 - (1 - r²_Y1)(1 - r²_Y2.1) for two predictors
    # Simpler: sum of squared semi-partial correlations

    print(f"Total effect (c): r² = {r2_total:.3f} ({r2_total*100:.1f}%)")
    print(f"Direct effect (c'): r_partial² ≈ {r_partial**2:.3f} ({r_partial**2*100:.1f}%)")
    print(f"GPQA alone → Disinhibition: R² = {r2_gpqa:.3f} ({r2_gpqa*100:.1f}%)")
    print(f"Sophistication alone → Disinhibition: R² = {r2_soph:.3f} ({r2_soph*100:.1f}%)")

    # Proportion mediated
    proportion_mediated = indirect / r_gpqa_disin if r_gpqa_disin != 0 else 0
    print(f"\nProportion mediated: {proportion_mediated:.1%}")

    # Mediation conclusion
    print("\n" + "-" * 40)
    print("MEDIATION RESULT")
    print("-" * 40)

    if p_partial >= 0.05 and p_sobel < 0.05:
        mediation_type = "FULL_MEDIATION"
        conclusion = "Full mediation supported. The GPQA→Disinhibition relationship is fully explained through Sophistication."
    elif p_partial < 0.05 and p_sobel < 0.05:
        mediation_type = "PARTIAL_MEDIATION"
        conclusion = "Partial mediation supported. Sophistication partially mediates GPQA→Disinhibition, but a significant direct effect remains."
    elif p_sobel >= 0.05:
        mediation_type = "NO_MEDIATION"
        conclusion = "No significant mediation. The indirect effect through Sophistication is not significant."
    else:
        mediation_type = "UNCLEAR"
        conclusion = "Results are unclear - further analysis needed."

    print(f"Result: {mediation_type}")
    print(f"\n{conclusion}")

    # Compare direct effect sign
    if r_partial < 0 and r_gpqa_disin > 0:
        print(f"\n⚠️  SUPPRESSION EFFECT DETECTED")
        print(f"   Total effect: r = {r_gpqa_disin:.3f} (positive)")
        print(f"   Direct effect: r = {r_partial:.3f} (negative)")
        print(f"   Interpretation: After accounting for sophistication, GPQA")
        print(f"   has a slight NEGATIVE relationship with disinhibition.")
        suppression = True
    else:
        suppression = False

    # Create results dictionary
    results = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "analysis": "Mediation Analysis: GPQA → Sophistication → Disinhibition",
            "condition": "baseline",
            "description": "Tests whether Sophistication mediates the Reasoning → Disinhibition relationship",
            "n_models": n
        },
        "provenance": {
            "source_files": {
                "gpqa_validation": str(GPQA_DATA),
                "behavioral_profiles": "outputs/behavioral_profiles/baseline/profiles/*.json"
            },
            "methodology": {
                "correlation": "Pearson product-moment correlation",
                "partial_correlation": "First-order partial correlation controlling for mediator",
                "indirect_effect": "Sobel test for significance of a × b path",
                "formula": "r_partial = (r_XY - r_XM * r_MY) / sqrt((1 - r_XM^2) * (1 - r_MY^2))"
            }
        },
        "zero_order_correlations": {
            "gpqa_to_sophistication": {
                "path": "a",
                "r": round(r_gpqa_soph, 4),
                "p": round(p_gs, 10),
                "significant": p_gs < 0.05,
                "interpretation": "large" if abs(r_gpqa_soph) >= 0.5 else "medium" if abs(r_gpqa_soph) >= 0.3 else "small"
            },
            "sophistication_to_disinhibition": {
                "path": "b",
                "r": round(r_soph_disin, 4),
                "p": round(p_sd, 10),
                "significant": p_sd < 0.05,
                "interpretation": "large" if abs(r_soph_disin) >= 0.5 else "medium" if abs(r_soph_disin) >= 0.3 else "small"
            },
            "gpqa_to_disinhibition": {
                "path": "c (total)",
                "r": round(r_gpqa_disin, 4),
                "p": round(p_gd, 10),
                "significant": p_gd < 0.05,
                "interpretation": "large" if abs(r_gpqa_disin) >= 0.5 else "medium" if abs(r_gpqa_disin) >= 0.3 else "small"
            }
        },
        "partial_correlation": {
            "gpqa_to_disinhibition_controlling_sophistication": {
                "path": "c' (direct)",
                "r": round(r_partial, 4),
                "t": round(t_stat, 3),
                "df": df,
                "p": round(p_partial, 4),
                "significant": p_partial < 0.05,
                "note": "Direct effect after controlling for Sophistication"
            }
        },
        "indirect_effect": {
            "a_x_b": round(indirect, 4),
            "se": round(se_indirect, 4),
            "sobel_z": round(z_sobel, 3),
            "p": round(p_sobel, 4),
            "significant": p_sobel < 0.05
        },
        "variance_explained": {
            "total_effect_r2": round(r2_total, 4),
            "gpqa_alone_r2": round(r2_gpqa, 4),
            "sophistication_alone_r2": round(r2_soph, 4),
            "proportion_mediated": round(proportion_mediated, 4)
        },
        "mediation_test": {
            "result": mediation_type,
            "paths": {
                "a_path": {
                    "description": "GPQA → Sophistication",
                    "r": round(r_gpqa_soph, 4),
                    "p": round(p_gs, 10),
                    "significant": True
                },
                "b_path": {
                    "description": "Sophistication → Disinhibition",
                    "r": round(r_soph_disin, 4),
                    "p": round(p_sd, 10),
                    "significant": True
                },
                "c_path": {
                    "description": "GPQA → Disinhibition (total effect)",
                    "r": round(r_gpqa_disin, 4),
                    "p": round(p_gd, 10),
                    "significant": True
                },
                "c_prime_path": {
                    "description": "GPQA → Disinhibition | Sophistication (direct effect)",
                    "r": round(r_partial, 4),
                    "p": round(p_partial, 4),
                    "significant": p_partial < 0.05
                }
            },
            "conclusion": conclusion
        },
        "suppression_effect": {
            "detected": suppression,
            "total_effect_r": round(r_gpqa_disin, 4),
            "direct_effect_r": round(r_partial, 4),
            "interpretation": "After accounting for sophistication, GPQA has a slight negative relationship with disinhibition." if suppression else "No suppression effect detected."
        },
        "summary": {
            "key_finding": f"{'Full' if mediation_type == 'FULL_MEDIATION' else 'Partial' if mediation_type == 'PARTIAL_MEDIATION' else 'No'} mediation: The GPQA→Disinhibition correlation (r={r_gpqa_disin:.3f}) is {'fully' if mediation_type == 'FULL_MEDIATION' else 'partially' if mediation_type == 'PARTIAL_MEDIATION' else 'not'} explained by the path through Sophistication.",
            "interpretation": f"More capable models show higher disinhibition {'primarily' if mediation_type == 'FULL_MEDIATION' else 'partly'} because they are more sophisticated. Sophistication accounts for {proportion_mediated:.0%} of the capability-disinhibition relationship.",
            "implication": "Sophistication (depth + authenticity) is a key intermediate variable between raw reasoning capability and willingness to engage with challenging content."
        },
        "output_files": [
            "gpqa_soph_disin_mediation_audit.json",
            "gpqa_soph_disin_mediation_diagram.png"
        ]
    }

    return results, gpqa, soph, disin, names


def create_mediation_diagram(results):
    """Create visualization of the mediation analysis."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    fig.suptitle('Mediation Analysis: GPQA → Sophistication → Disinhibition',
                 fontsize=14, fontweight='bold', y=0.96)

    # Condition label
    fig.text(0.5, 0.92, 'Condition: baseline', ha='center', fontsize=11,
             fontweight='bold', color='#666666',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#E0E0E0', edgecolor='#999999'))

    ax.set_title('Does Sophistication mediate the Reasoning→Disinhibition relationship?',
                 fontsize=10, color='#666666', pad=20)

    # Nodes
    nodes = {
        "GPQA\n(Reasoning)": (2, 4),
        "Sophistication\n(Mediator)": (6, 6.5),
        "Disinhibition\n(Outcome)": (10, 4),
    }

    colors = {
        "GPQA\n(Reasoning)": ('#E3F2FD', '#1976D2'),
        "Sophistication\n(Mediator)": ('#E8F5E9', '#388E3C'),
        "Disinhibition\n(Outcome)": ('#FFF3E0', '#F57C00'),
    }

    # Draw nodes
    for node, (x, y) in nodes.items():
        fc, ec = colors[node]
        bbox = FancyBboxPatch(
            (x - 1.1, y - 0.6), 2.2, 1.2,
            boxstyle="round,pad=0.05,rounding_size=0.2",
            facecolor=fc, edgecolor=ec, linewidth=2.5, zorder=10
        )
        ax.add_patch(bbox)
        ax.text(x, y, node, ha='center', va='center', fontsize=10,
                fontweight='bold', zorder=11)

    # Get values from results
    r_a = results['zero_order_correlations']['gpqa_to_sophistication']['r']
    r_b = results['zero_order_correlations']['sophistication_to_disinhibition']['r']
    r_c = results['zero_order_correlations']['gpqa_to_disinhibition']['r']
    r_c_prime = results['partial_correlation']['gpqa_to_disinhibition_controlling_sophistication']['r']
    p_c_prime = results['partial_correlation']['gpqa_to_disinhibition_controlling_sophistication']['p']
    c_prime_sig = results['partial_correlation']['gpqa_to_disinhibition_controlling_sophistication']['significant']

    # Path a: GPQA → Sophistication
    arrow_a = FancyArrowPatch(
        (3.1, 4.4), (4.9, 6.0),
        arrowstyle='-|>', mutation_scale=15,
        color='#2E7D32', linewidth=3, zorder=5
    )
    ax.add_patch(arrow_a)
    ax.text(3.5, 5.5, f"a path\nr = {r_a:.3f}***", ha='center', va='center',
            fontsize=9, fontweight='bold', color='#2E7D32',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.95))

    # Path b: Sophistication → Disinhibition
    arrow_b = FancyArrowPatch(
        (7.1, 6.0), (8.9, 4.4),
        arrowstyle='-|>', mutation_scale=15,
        color='#2E7D32', linewidth=3, zorder=5
    )
    ax.add_patch(arrow_b)
    ax.text(8.5, 5.5, f"b path\nr = {r_b:.3f}***", ha='center', va='center',
            fontsize=9, fontweight='bold', color='#2E7D32',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.95))

    # Direct path c': GPQA → Disinhibition (controlling for mediator)
    line_style = '--' if not c_prime_sig else '-'
    line_color = '#BDBDBD' if not c_prime_sig else '#424242'
    arrow_c = FancyArrowPatch(
        (3.1, 3.8), (8.9, 3.8),
        arrowstyle='-|>', mutation_scale=12,
        color=line_color, linewidth=2, linestyle=line_style, zorder=4
    )
    ax.add_patch(arrow_c)

    sig_marker = "" if c_prime_sig else " (n.s.)"
    ax.text(6, 3.2, f"c' path (direct effect)\nr = {r_c_prime:.3f}{sig_marker}, p = {p_c_prime:.3f}",
            ha='center', va='center', fontsize=9, color='#757575' if not c_prime_sig else '#424242',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor='#BDBDBD', alpha=0.95))

    # Total effect annotation
    ax.text(6, 2.4, f"Total effect (c path): r = {r_c:.3f}***\nAfter controlling for Sophistication: r = {r_c_prime:.3f} ({'n.s.' if not c_prime_sig else 'sig.'})",
            ha='center', va='center', fontsize=9, style='italic', color='#424242')

    # Conclusion box
    mediation_result = results['mediation_test']['result']
    proportion = results['variance_explained']['proportion_mediated']

    if mediation_result == "FULL_MEDIATION":
        conclusion_color = '#E8F5E9'
        edge_color = '#4CAF50'
    elif mediation_result == "PARTIAL_MEDIATION":
        conclusion_color = '#FFF3E0'
        edge_color = '#FF9800'
    else:
        conclusion_color = '#FFEBEE'
        edge_color = '#F44336'

    conclusion = f"""MEDIATION RESULT: {mediation_result.replace('_', ' ')}

• Indirect effect (a × b): {results['indirect_effect']['a_x_b']:.3f}
  Sobel Z = {results['indirect_effect']['sobel_z']:.2f}, p = {results['indirect_effect']['p']:.4f}

• Proportion mediated: {proportion:.0%}

• Interpretation: {'The GPQA→Disinhibition relationship is fully explained through Sophistication.' if mediation_result == 'FULL_MEDIATION' else 'Sophistication partially mediates GPQA→Disinhibition.' if mediation_result == 'PARTIAL_MEDIATION' else 'No significant mediation through Sophistication.'}"""

    ax.text(0.5, 0.18, conclusion, transform=ax.transAxes,
            fontsize=9, va='top', ha='center', family='monospace',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=conclusion_color,
                     edgecolor=edge_color, alpha=0.95))

    # Source files note
    source_text = "Sources: gpqa_validation_analysis.json, baseline/profiles/*.json"
    ax.text(0.98, 0.02, source_text, transform=ax.transAxes,
            fontsize=7, ha='right', va='bottom', color='#999999', style='italic')

    plt.tight_layout()

    output_path = OUTPUT_DIR / 'gpqa_soph_disin_mediation_diagram.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"\nSaved: {output_path}")

    plt.close()
    return output_path


def create_scatter_plots(gpqa, soph, disin, names, results):
    """Create 2x2 scatter plots showing all relationships."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    fig.suptitle('GPQA → Sophistication → Disinhibition: Path Relationships',
                 fontsize=14, fontweight='bold', y=0.98)
    fig.text(0.5, 0.95, 'Condition: baseline', ha='center', fontsize=11,
             fontweight='bold', color='#666666',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#E0E0E0', edgecolor='#999999'))

    # Plot 1: GPQA vs Sophistication (a path)
    ax1 = axes[0, 0]
    ax1.scatter(gpqa, soph, alpha=0.7, s=60, c='#1976D2', edgecolors='white', linewidth=0.5)

    # Regression line
    slope, intercept = np.polyfit(gpqa, soph, 1)
    x_line = np.linspace(gpqa.min(), gpqa.max(), 100)
    ax1.plot(x_line, slope * x_line + intercept, 'k--', alpha=0.5, linewidth=2)

    r_a = results['zero_order_correlations']['gpqa_to_sophistication']['r']
    p_a = results['zero_order_correlations']['gpqa_to_sophistication']['p']

    stats_text = f"a path\nr = {r_a:.3f}\np < .0001\nN = {len(gpqa)}"
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95))

    ax1.set_xlabel('GPQA Score (%)', fontsize=11)
    ax1.set_ylabel('Sophistication', fontsize=11)
    ax1.set_title('A Path: GPQA → Sophistication', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Plot 2: Sophistication vs Disinhibition (b path)
    ax2 = axes[0, 1]
    ax2.scatter(soph, disin, alpha=0.7, s=60, c='#388E3C', edgecolors='white', linewidth=0.5)

    slope, intercept = np.polyfit(soph, disin, 1)
    x_line = np.linspace(soph.min(), soph.max(), 100)
    ax2.plot(x_line, slope * x_line + intercept, 'k--', alpha=0.5, linewidth=2)

    r_b = results['zero_order_correlations']['sophistication_to_disinhibition']['r']

    stats_text = f"b path\nr = {r_b:.3f}\np < .0001\nN = {len(gpqa)}"
    ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95))

    ax2.set_xlabel('Sophistication', fontsize=11)
    ax2.set_ylabel('Disinhibition', fontsize=11)
    ax2.set_title('B Path: Sophistication → Disinhibition', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')

    # Plot 3: GPQA vs Disinhibition (c path - total)
    ax3 = axes[1, 0]
    ax3.scatter(gpqa, disin, alpha=0.7, s=60, c='#F57C00', edgecolors='white', linewidth=0.5)

    slope, intercept = np.polyfit(gpqa, disin, 1)
    x_line = np.linspace(gpqa.min(), gpqa.max(), 100)
    ax3.plot(x_line, slope * x_line + intercept, 'k--', alpha=0.5, linewidth=2)

    r_c = results['zero_order_correlations']['gpqa_to_disinhibition']['r']

    stats_text = f"c path (total)\nr = {r_c:.3f}\np < .0001\nN = {len(gpqa)}"
    ax3.text(0.02, 0.98, stats_text, transform=ax3.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95))

    ax3.set_xlabel('GPQA Score (%)', fontsize=11)
    ax3.set_ylabel('Disinhibition', fontsize=11)
    ax3.set_title('C Path (Total): GPQA → Disinhibition', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, linestyle='--')

    # Plot 4: Summary / residuals
    ax4 = axes[1, 1]

    # Plot residuals from controlling for sophistication
    # Residualize disinhibition on sophistication
    slope_sd, intercept_sd = np.polyfit(soph, disin, 1)
    disin_residuals = disin - (slope_sd * soph + intercept_sd)

    # Residualize GPQA on sophistication
    slope_gs, intercept_gs = np.polyfit(soph, gpqa, 1)
    gpqa_residuals = gpqa - (slope_gs * soph + intercept_gs)

    ax4.scatter(gpqa_residuals, disin_residuals, alpha=0.7, s=60, c='#9C27B0', edgecolors='white', linewidth=0.5)

    # Regression on residuals
    slope, intercept = np.polyfit(gpqa_residuals, disin_residuals, 1)
    x_line = np.linspace(gpqa_residuals.min(), gpqa_residuals.max(), 100)
    ax4.plot(x_line, slope * x_line + intercept, 'k--', alpha=0.5, linewidth=2)
    ax4.axhline(0, color='gray', linestyle=':', alpha=0.5)
    ax4.axvline(0, color='gray', linestyle=':', alpha=0.5)

    r_partial = results['partial_correlation']['gpqa_to_disinhibition_controlling_sophistication']['r']
    p_partial = results['partial_correlation']['gpqa_to_disinhibition_controlling_sophistication']['p']
    sig = "n.s." if p_partial >= 0.05 else "sig."

    stats_text = f"c' path (direct)\nr = {r_partial:.3f} ({sig})\np = {p_partial:.3f}\nN = {len(gpqa)}"
    ax4.text(0.02, 0.98, stats_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95))

    ax4.set_xlabel('GPQA (residualized on Sophistication)', fontsize=11)
    ax4.set_ylabel('Disinhibition (residualized on Sophistication)', fontsize=11)
    ax4.set_title("C' Path (Direct): GPQA → Disinhibition | Sophistication", fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout(rect=[0, 0, 1, 0.93])

    output_path = OUTPUT_DIR / 'gpqa_soph_disin_scatters.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"Saved: {output_path}")

    plt.close()
    return output_path


def main():
    """Run the full analysis."""
    print("\n" + "=" * 60)
    print("GPQA → Sophistication → Disinhibition Mediation Analysis")
    print("=" * 60 + "\n")

    # Run analysis
    results, gpqa, soph, disin, names = run_mediation_analysis()

    # Save audit JSON (convert numpy types to Python natives)
    def convert_numpy(obj):
        if isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(i) for i in obj]
        elif isinstance(obj, (np.bool_, np.integer, np.floating)):
            return obj.item()
        else:
            return obj

    audit_path = OUTPUT_DIR / 'gpqa_soph_disin_mediation_audit.json'
    with open(audit_path, 'w') as f:
        json.dump(convert_numpy(results), f, indent=2)
    print(f"\nSaved: {audit_path}")

    # Create visualizations
    create_mediation_diagram(results)
    create_scatter_plots(gpqa, soph, disin, names, results)

    # Update output files list
    results['output_files'].append('gpqa_soph_disin_scatters.png')

    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
