#!/usr/bin/env python3
"""
Generate a causal path diagram showing relationships between:
- Reasoning Capability (GPQA)
- Sophistication
- Disinhibition
- BERT Toxicity

Shows statistical evidence for each path with significance indicators.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# Output directory
OUTPUT_DIR = Path(__file__).parent  # research_synthesis/framework/

# Statistical relationships from our analyses
RELATIONSHIPS = {
    # Path: (r, p, significant, source)
    ("Reasoning\n(GPQA)", "Sophistication"): {
        "r": 0.884, "p": 0.0001, "sig": True,
        "source": "gpqa_validation_analysis.json",
        "n": 35
    },
    ("Reasoning\n(GPQA)", "Disinhibition"): {
        "r": 0.711, "p": 0.0001, "sig": True,
        "source": "reasoning_composite_triangulated_audit.json (approach_1c)",
        "n": 35
    },
    ("Sophistication", "Disinhibition"): {
        "r": 0.753, "p": 0.0001, "sig": True,
        "source": "baseline/median_split_classification.json",
        "n": 45
    },
    ("Disinhibition", "BERT\nToxicity"): {
        "r": 0.740, "p": 0.0001, "sig": True,
        "source": "bert_validation/baseline/bert_soph_disin_results.json",
        "n": 45
    },
    ("Reasoning\n(GPQA)", "BERT\nToxicity"): {
        "r": 0.423, "p": 0.011, "sig": True,
        "source": "gpqa_bert_mediation_audit.json (zero-order)",
        "n": 35,
        "note": "Becomes r=-0.218 (n.s.) when controlling for Disinhibition"
    },
    ("Sophistication", "BERT\nToxicity"): {
        "r": 0.510, "p": 0.0003, "sig": True,
        "source": "bert_validation/baseline/bert_soph_disin_results.json",
        "n": 45,
        "note": "Becomes beta=-0.237 (n.s.) when controlling for Disinhibition"
    },
}

# Mediation results (two convergent analyses)
MEDIATION_GPQA = {
    "path": "GPQA → Disinhibition → Toxicity",
    "method": "Partial correlation",
    "direct_effect": {"r": -0.218, "p": 0.216, "sig": False},
    "conclusion": "Full mediation: Disinhibition fully mediates GPQA→Toxicity"
}

MEDIATION_SOPH = {
    "path": "Sophistication → Disinhibition → Toxicity",
    "method": "Bootstrap mediation (n=5000)",
    "ACME": {"estimate": 0.0074, "p": 0.001, "sig": True},
    "ADE": {"estimate": -0.0023, "p": 0.120, "sig": False},
    "proportion_mediated": "146%",
    "conclusion": "Full mediation with suppression effect"
}

# Suppression effect (convergent evidence)
SUPPRESSION = {
    "gpqa_partial_r": -0.218,
    "soph_beta": -0.237,
    "interpretation": "Capability has slight NEGATIVE direct effect on toxicity when disinhibition is controlled"
}

def create_path_diagram():
    """Create the main path diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Title with condition label
    fig.suptitle('Capability-Disinhibition-Toxicity Path Model',
                 fontsize=16, fontweight='bold', y=0.96)

    # Condition label (prominent)
    fig.text(0.5, 0.92, 'Condition: baseline', ha='center', fontsize=11,
             fontweight='bold', color='#666666',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#E0E0E0', edgecolor='#999999'))

    ax.set_title('Statistical relationships from behavioral profiling research',
                 fontsize=10, color='#666666', pad=20)

    # Node positions (x, y)
    nodes = {
        "Reasoning\n(GPQA)": (1.5, 4),
        "Sophistication": (5, 6.5),
        "Disinhibition": (5, 1.5),
        "BERT\nToxicity": (8.5, 4),
    }

    # Draw nodes
    node_colors = {
        "Reasoning\n(GPQA)": '#E3F2FD',      # Light blue - external benchmark
        "Sophistication": '#E8F5E9',          # Light green - behavioral composite
        "Disinhibition": '#FFF3E0',           # Light orange - behavioral composite
        "BERT\nToxicity": '#FCE4EC',          # Light pink - external validation
    }

    node_edge_colors = {
        "Reasoning\n(GPQA)": '#1976D2',
        "Sophistication": '#388E3C',
        "Disinhibition": '#F57C00',
        "BERT\nToxicity": '#C2185B',
    }

    # Draw nodes as rounded rectangles
    for node, (x, y) in nodes.items():
        bbox = FancyBboxPatch(
            (x - 0.9, y - 0.5), 1.8, 1.0,
            boxstyle="round,pad=0.05,rounding_size=0.2",
            facecolor=node_colors[node],
            edgecolor=node_edge_colors[node],
            linewidth=2.5,
            zorder=10
        )
        ax.add_patch(bbox)
        ax.text(x, y, node, ha='center', va='center', fontsize=11,
                fontweight='bold', zorder=11)

    # Draw arrows with correlation coefficients
    def draw_arrow(start, end, r, sig, is_mediated=False, curve_direction=0):
        """Draw an arrow between two nodes with correlation label."""
        x1, y1 = nodes[start]
        x2, y2 = nodes[end]

        # Adjust start/end points to edge of boxes
        dx = x2 - x1
        dy = y2 - y1
        dist = np.sqrt(dx**2 + dy**2)

        # Start and end offsets
        offset_start = 0.95
        offset_end = 0.95

        x1_adj = x1 + (dx/dist) * offset_start
        y1_adj = y1 + (dy/dist) * offset_start * 0.5
        x2_adj = x2 - (dx/dist) * offset_end
        y2_adj = y2 - (dy/dist) * offset_end * 0.5

        # Arrow style based on significance
        if not sig:
            arrow_color = '#BDBDBD'
            linestyle = '--'
            linewidth = 1.5
        elif is_mediated:
            arrow_color = '#7B1FA2'  # Purple for mediated path
            linestyle = '-'
            linewidth = 2.5
        else:
            arrow_color = '#424242'
            linestyle = '-'
            linewidth = 2.0

        # Connection style for curved arrows
        if curve_direction != 0:
            connectionstyle = f"arc3,rad={0.3 * curve_direction}"
        else:
            connectionstyle = "arc3,rad=0"

        arrow = FancyArrowPatch(
            (x1_adj, y1_adj), (x2_adj, y2_adj),
            arrowstyle='-|>',
            mutation_scale=15,
            color=arrow_color,
            linewidth=linewidth,
            linestyle=linestyle,
            connectionstyle=connectionstyle,
            zorder=5
        )
        ax.add_patch(arrow)

        # Label position (midpoint with offset for curved arrows)
        mid_x = (x1_adj + x2_adj) / 2
        mid_y = (y1_adj + y2_adj) / 2

        # Offset for curved paths
        if curve_direction != 0:
            perp_x = -(y2_adj - y1_adj) / dist
            perp_y = (x2_adj - x1_adj) / dist
            mid_x += perp_x * 0.4 * curve_direction
            mid_y += perp_y * 0.4 * curve_direction

        # Label text
        if sig:
            label = f"r = {r:.2f}***" if r > 0.7 else f"r = {r:.2f}**" if r > 0.5 else f"r = {r:.2f}*"
        else:
            label = f"r = {r:.2f} (n.s.)"

        # Background box for label
        bbox_props = dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor=arrow_color, alpha=0.95, linewidth=1)

        ax.text(mid_x, mid_y, label, ha='center', va='center',
                fontsize=9, fontweight='bold', color=arrow_color,
                bbox=bbox_props, zorder=15)

    # Draw the main paths
    # Mediation chain: GPQA → Disinhibition → Toxicity (the supported path)
    draw_arrow("Reasoning\n(GPQA)", "Disinhibition", 0.711, True, is_mediated=True, curve_direction=-0.3)
    draw_arrow("Disinhibition", "BERT\nToxicity", 0.740, True, is_mediated=True, curve_direction=0.3)

    # Upper path: GPQA → Sophistication → Disinhibition
    draw_arrow("Reasoning\n(GPQA)", "Sophistication", 0.884, True, curve_direction=0)
    draw_arrow("Sophistication", "Disinhibition", 0.753, True, curve_direction=0)

    # Sophistication → Toxicity (direct)
    draw_arrow("Sophistication", "BERT\nToxicity", 0.510, True, curve_direction=0)

    # Direct path (becomes non-significant when controlling) - shown as dashed
    # We'll show this with the partial correlation
    x1, y1 = nodes["Reasoning\n(GPQA)"]
    x2, y2 = nodes["BERT\nToxicity"]

    arrow = FancyArrowPatch(
        (x1 + 0.9, y1), (x2 - 0.9, y2),
        arrowstyle='-|>',
        mutation_scale=12,
        color='#BDBDBD',
        linewidth=1.5,
        linestyle='--',
        connectionstyle="arc3,rad=0",
        zorder=4
    )
    ax.add_patch(arrow)

    # Label for direct path
    mid_x = (x1 + x2) / 2
    mid_y = y1
    ax.text(mid_x, mid_y - 0.15, "r = 0.42* → r = -0.22 (n.s.)\nwhen controlling for Disinhibition",
            ha='center', va='top', fontsize=8, color='#757575',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor='#BDBDBD', alpha=0.9), zorder=15)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2,
                      label='External Benchmark (GPQA)'),
        mpatches.Patch(facecolor='#E8F5E9', edgecolor='#388E3C', linewidth=2,
                      label='Behavioral Composite (Depth + Authenticity)'),
        mpatches.Patch(facecolor='#FFF3E0', edgecolor='#F57C00', linewidth=2,
                      label='Behavioral Composite (Trans + Agg + Gran + Trib)'),
        mpatches.Patch(facecolor='#FCE4EC', edgecolor='#C2185B', linewidth=2,
                      label='External Validation (BERT toxic-bert)'),
    ]

    ax.legend(handles=legend_elements, loc='upper left', fontsize=9,
              framealpha=0.95, edgecolor='#CCCCCC')

    # Key findings box
    findings_text = """Key Findings:
1. Reasoning strongly predicts both Sophistication (r=0.88) and Disinhibition (r=0.71)
2. Sophistication strongly predicts Disinhibition (r=0.75) — H2 confirmed
3. BERT Toxicity is fully mediated through Disinhibition (two convergent analyses):
   • GPQA: r=0.42 → r=-0.22 (n.s.) | Soph: β=0.51 → β=-0.24 (n.s.) after controlling
   • Disinhibition uniquely explains 36-55% of Toxicity variance
4. Suppression effect: capability slightly REDUCES toxicity when disinhibition held constant
5. Sophistication is a valid proxy for reasoning capability (r=0.88)"""

    ax.text(0.02, 0.02, findings_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='bottom',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#F5F5F5',
                     edgecolor='#CCCCCC', alpha=0.95))

    # Significance legend
    sig_text = "Significance: * p < .05  ** p < .01  *** p < .001  (n.s.) not significant"
    ax.text(0.98, 0.02, sig_text, transform=ax.transAxes,
            fontsize=8, ha='right', va='bottom', color='#757575')

    # Sample size and source note
    ax.text(0.98, 0.06, "n = 35-45 models",
            transform=ax.transAxes, fontsize=8, ha='right', va='bottom', color='#757575')

    # Source files note
    source_text = """Sources: baseline/profiles/*.json, baseline/median_split_classification.json,
bert_validation/baseline/bert_validation_results.json, gpqa_validation_analysis.json"""
    ax.text(0.98, 0.12, source_text, transform=ax.transAxes,
            fontsize=7, ha='right', va='bottom', color='#999999', style='italic')

    plt.tight_layout()

    # Save
    output_path = OUTPUT_DIR / 'path_diagram.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"Saved: {output_path}")

    plt.close()
    return output_path


def create_mediation_diagram():
    """Create a focused mediation diagram for GPQA → Disinhibition → Toxicity."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    fig.suptitle('Mediation Analysis: GPQA → Disinhibition → BERT Toxicity',
                 fontsize=14, fontweight='bold', y=0.96)

    # Condition label (prominent)
    fig.text(0.5, 0.92, 'Condition: baseline', ha='center', fontsize=11,
             fontweight='bold', color='#666666',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#E0E0E0', edgecolor='#999999'))

    ax.set_title('Disinhibition fully mediates the capability-toxicity relationship',
                 fontsize=10, color='#666666', pad=20)

    # Nodes - repositioned for better layout
    nodes = {
        "GPQA\n(Reasoning)": (2, 4),
        "Disinhibition\n(Mediator)": (6, 6.5),
        "BERT Toxicity\n(Outcome)": (10, 4),
    }

    colors = {
        "GPQA\n(Reasoning)": ('#E3F2FD', '#1976D2'),
        "Disinhibition\n(Mediator)": ('#FFF3E0', '#F57C00'),
        "BERT Toxicity\n(Outcome)": ('#FCE4EC', '#C2185B'),
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

    # Path a: GPQA → Disinhibition
    arrow_a = FancyArrowPatch(
        (3.1, 4.4), (4.9, 6.0),
        arrowstyle='-|>', mutation_scale=15,
        color='#2E7D32', linewidth=3, zorder=5
    )
    ax.add_patch(arrow_a)
    ax.text(3.5, 5.5, "a path\nr = 0.711***", ha='center', va='center',
            fontsize=9, fontweight='bold', color='#2E7D32',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.95))

    # Path b: Disinhibition → Toxicity
    arrow_b = FancyArrowPatch(
        (7.1, 6.0), (8.9, 4.4),
        arrowstyle='-|>', mutation_scale=15,
        color='#2E7D32', linewidth=3, zorder=5
    )
    ax.add_patch(arrow_b)
    ax.text(8.5, 5.5, "b path\nr = 0.740***", ha='center', va='center',
            fontsize=9, fontweight='bold', color='#2E7D32',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.95))

    # Direct path c': GPQA → Toxicity (controlling for mediator)
    arrow_c = FancyArrowPatch(
        (3.1, 3.8), (8.9, 3.8),
        arrowstyle='-|>', mutation_scale=12,
        color='#BDBDBD', linewidth=2, linestyle='--', zorder=4
    )
    ax.add_patch(arrow_c)
    ax.text(6, 3.2, "c' path (direct effect)\nr = -0.218 (n.s., p = 0.216)",
            ha='center', va='center', fontsize=9, color='#757575',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor='#BDBDBD', alpha=0.95))

    # Total effect annotation
    ax.text(6, 2.4, "Total effect (c path): r = 0.423*\nAfter controlling for Disinhibition: r = -0.218 (n.s.)",
            ha='center', va='center', fontsize=9, style='italic', color='#424242')

    # Conclusion box - moved to bottom
    conclusion = """MEDIATION CONFIRMED

 • The significant GPQA→Toxicity correlation (r = 0.42)
   becomes non-significant when controlling for Disinhibition

 • Disinhibition alone explains 55% of Toxicity variance
   vs. 18% for GPQA alone

 • Interpretation: Capable models show higher "toxicity"
   because they exhibit higher disinhibition (willingness
   to engage), not because capability directly causes toxicity"""

    ax.text(0.5, 0.18, conclusion, transform=ax.transAxes,
            fontsize=9, va='top', ha='center', family='monospace',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9',
                     edgecolor='#4CAF50', alpha=0.95))

    # Source files note
    source_text = """Sources: baseline/profiles/*.json, gpqa_bert_mediation_audit.json,
bert_validation/baseline/bert_soph_disin_results.json"""
    ax.text(0.98, 0.02, source_text, transform=ax.transAxes,
            fontsize=7, ha='right', va='bottom', color='#999999', style='italic')

    plt.tight_layout()

    output_path = OUTPUT_DIR / 'mediation_diagram.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"Saved: {output_path}")

    plt.close()
    return output_path


def create_audit_json():
    """Create audit JSON with all relationship data."""
    audit = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "analysis": "Causal Path Model: Capability-Disinhibition-Toxicity",
            "description": "Statistical relationships between reasoning capability, behavioral composites, and BERT toxicity"
        },
        "variables": {
            "reasoning_capability": {
                "operationalization": "GPQA (Graduate-Level Google-Proof Q&A)",
                "type": "external_benchmark",
                "n_models": 35,
                "range": "30.8% - 93.2%"
            },
            "sophistication": {
                "operationalization": "(Depth + Authenticity) / 2",
                "type": "behavioral_composite",
                "n_models": 45,
                "range": "4.01 - 7.55"
            },
            "disinhibition": {
                "operationalization": "(Transgression + Aggression + Grandiosity + Tribalism) / 4",
                "type": "behavioral_composite",
                "n_models": 45,
                "range": "1.30 - 2.31"
            },
            "bert_toxicity": {
                "operationalization": "unitary/toxic-bert mean toxicity score",
                "type": "external_validation",
                "n_models": 45,
                "range": "0.005 - 0.065"
            }
        },
        "relationships": {
            path: {
                "r": data["r"],
                "p": data["p"],
                "significant": data["sig"],
                "n": data["n"],
                "source": data["source"],
                "note": data.get("note", None)
            }
            for path, data in RELATIONSHIPS.items()
        },
        "mediation_analysis_gpqa": {
            "hypothesis": "Disinhibition mediates GPQA -> BERT Toxicity",
            "method": "Partial correlation",
            "n": 35,
            "source": "limitations/external_evals/gpqa_bert_mediation_audit.json",
            "paths": {
                "a_path": {"GPQA -> Disinhibition": {"r": 0.711, "p": 0.0001, "sig": True}},
                "b_path": {"Disinhibition -> Toxicity": {"r": 0.740, "p": 0.0001, "sig": True}},
                "c_path_total": {"GPQA -> Toxicity": {"r": 0.423, "p": 0.011, "sig": True}},
                "c_prime_direct": {"GPQA -> Toxicity | Disinhibition": {"r": -0.218, "p": 0.216, "sig": False}}
            },
            "conclusion": "Full mediation supported",
            "variance_explained": {
                "disinhibition_alone": 0.548,
                "gpqa_alone": 0.179,
                "gpqa_incremental_after_disinhibition": 0.0
            }
        },
        "mediation_analysis_sophistication": {
            "hypothesis": "Disinhibition mediates Sophistication -> BERT Toxicity",
            "method": "Bootstrap mediation (n=5000)",
            "n": 45,
            "source": "bert_validation/regression_analysis_audit.json",
            "effects": {
                "ACME_indirect": {"estimate": 0.0074, "ci_95": [0.0039, 0.0116], "p": 0.001, "sig": True},
                "ADE_direct": {"estimate": -0.0023, "ci_95": [-0.0053, 0.0006], "p": 0.120, "sig": False},
                "total_effect": {"estimate": 0.0050, "ci_95": [0.0014, 0.0087], "p": 0.008},
                "proportion_mediated": {"estimate": 1.46, "percentage": "146%"}
            },
            "variance_decomposition": {
                "disinhibition_unique": 0.363,
                "sophistication_unique": 0.022,
                "shared": 0.238,
                "total_explained": 0.624
            },
            "standardized_coefficients": {
                "disinhibition": {"beta": 0.960, "p": 0.0001, "sig": True},
                "sophistication": {"beta": -0.237, "p": 0.123, "sig": False}
            }
        },
        "suppression_effect": {
            "detected": True,
            "convergent_evidence": {
                "gpqa_partial_r": SUPPRESSION["gpqa_partial_r"],
                "sophistication_beta": SUPPRESSION["soph_beta"]
            },
            "interpretation": SUPPRESSION["interpretation"]
        },
        "key_findings": [
            "Reasoning capability (GPQA) strongly predicts both Sophistication (r=0.88) and Disinhibition (r=0.71)",
            "Sophistication strongly predicts Disinhibition (r=0.75) - confirms H2",
            "BERT Toxicity is fully mediated through Disinhibition (two convergent analyses)",
            "Suppression effect: capability has slight NEGATIVE direct effect on toxicity when controlling for disinhibition",
            "Sophistication is a valid proxy for reasoning capability",
            "The capability-disinhibition relationship is large (r=0.71) when measured across full capability range"
        ],
        "provenance": {
            "source_analyses": [
                "limitations/external_evals/gpqa_bert_mediation_audit.json",
                "bert_validation/regression_analysis_audit.json",
                "limitations/external_evals/gpqa_validation_analysis.json",
                "limitations/external_evals/reasoning_composite_triangulated_audit.json"
            ]
        },
        "output_files": [
            "path_diagram.png",
            "mediation_diagram.png",
            "STATISTICAL_RELATIONSHIPS.md"
        ]
    }

    # Convert tuple keys to strings for JSON
    audit["relationships"] = {
        f"{k[0].replace(chr(10), ' ')} → {k[1].replace(chr(10), ' ')}": v
        for k, v in audit["relationships"].items()
    }

    output_path = OUTPUT_DIR / 'statistical_model_audit.json'
    with open(output_path, 'w') as f:
        json.dump(audit, f, indent=2)
    print(f"Saved: {output_path}")

    return output_path


def main():
    """Generate all diagrams and audit file."""
    print("Generating causal path diagrams...")
    print("=" * 50)

    path1 = create_path_diagram()
    path2 = create_mediation_diagram()
    path3 = create_audit_json()

    print("=" * 50)
    print("Done! Generated files:")
    print(f"  1. {path1}")
    print(f"  2. {path2}")
    print(f"  3. {path3}")


if __name__ == "__main__":
    main()
