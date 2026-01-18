#!/usr/bin/env python3
"""
Generate Reasoning Capability Model Diagram - v2

Shows correlational structure with NO causal claims.
Includes note about unmeasured variables.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse, Rectangle
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent


def create_capability_model_v2():
    """Create the reasoning capability model diagram - v2 with no causal claims."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 13))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 13)
    ax.axis('off')

    # Title
    fig.suptitle('Reasoning Capability: Correlational Structure',
                 fontsize=16, fontweight='bold', y=0.97)

    # Condition label
    fig.text(0.5, 0.94, 'Condition: baseline  |  N = 35-45 models  |  Correlational (not causal)',
             ha='center', fontsize=10, fontweight='bold', color='#666666',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#E8E8E8', edgecolor='#999999'))

    # ===== LATENT CONSTRUCT (ellipse) =====
    latent_x, latent_y = 7, 10.5
    latent = Ellipse((latent_x, latent_y), 4.5, 1.6,
                     facecolor='#E1BEE7', edgecolor='#7B1FA2',
                     linewidth=3, zorder=10)
    ax.add_patch(latent)
    ax.text(latent_x, latent_y + 0.15, 'Reasoning',
            ha='center', va='center', fontsize=13, fontweight='bold',
            color='#4A148C', zorder=11)
    ax.text(latent_x, latent_y - 0.4, 'Capability',
            ha='center', va='center', fontsize=13, fontweight='bold',
            color='#4A148C', zorder=11)

    # ===== THREE INDICATORS =====
    indicators = [
        ("GPQA", 2.5, 6.5, '#E3F2FD', '#1976D2'),
        ("Sophistication", 7, 6.5, '#E8F5E9', '#388E3C'),
        ("Disinhibition", 11.5, 6.5, '#FFF3E0', '#F57C00'),
    ]

    indicator_subtitles = [
        "(external benchmark)",
        "(depth + authenticity)",
        "(trans + agg + gran + trib)",
    ]

    # Draw indicator boxes
    for i, (label, x, y, fc, ec) in enumerate(indicators):
        width = 2.8
        bbox = FancyBboxPatch(
            (x - width/2, y - 0.6), width, 1.2,
            boxstyle="round,pad=0.05,rounding_size=0.15",
            facecolor=fc, edgecolor=ec, linewidth=2.5, zorder=10
        )
        ax.add_patch(bbox)
        ax.text(x, y + 0.15, label, ha='center', va='center', fontsize=11,
                fontweight='bold', zorder=11)
        ax.text(x, y - 0.3, indicator_subtitles[i], ha='center', va='center',
                fontsize=8, color='#555555', zorder=11)

    # ===== LINES FROM LATENT TO INDICATORS (not arrows - correlational) =====
    for label, x, y, fc, ec in indicators:
        line = FancyArrowPatch(
            (latent_x + (x - latent_x) * 0.4, latent_y - 0.8),
            (x, y + 0.65),
            arrowstyle='-', mutation_scale=15,
            color='#7B1FA2', linewidth=2, zorder=5,
            connectionstyle="arc3,rad=0"
        )
        ax.add_patch(line)

    # ===== CORRELATION LINES BETWEEN INDICATORS (double-headed, no labels) =====
    # GPQA <-> Sophistication
    ax.annotate('', xy=(5.6, 6.5), xytext=(3.9, 6.5),
                arrowprops=dict(arrowstyle='<->', color='#616161', lw=2,
                               connectionstyle="arc3,rad=-0.3"))

    # Sophistication <-> Disinhibition
    ax.annotate('', xy=(10.1, 6.5), xytext=(8.4, 6.5),
                arrowprops=dict(arrowstyle='<->', color='#616161', lw=2,
                               connectionstyle="arc3,rad=-0.3"))

    # GPQA <-> Disinhibition (wider arc)
    ax.annotate('', xy=(10.1, 6.8), xytext=(3.9, 6.8),
                arrowprops=dict(arrowstyle='<->', color='#616161', lw=2,
                               connectionstyle="arc3,rad=0.2"))

    # ===== BERT TOXICITY (outcome) =====
    tox_x, tox_y = 11.5, 3.0
    bbox_tox = FancyBboxPatch(
        (tox_x - 1.4, tox_y - 0.5), 2.8, 1.0,
        boxstyle="round,pad=0.05,rounding_size=0.15",
        facecolor='#FCE4EC', edgecolor='#C2185B', linewidth=2.5, zorder=10
    )
    ax.add_patch(bbox_tox)
    ax.text(tox_x, tox_y + 0.1, "BERT Toxicity", ha='center', va='center',
            fontsize=11, fontweight='bold', zorder=11)
    ax.text(tox_x, tox_y - 0.3, "(external validation)", ha='center', va='center',
            fontsize=8, color='#555555', zorder=11)

    # Correlation: Disinhibition -- BERT Toxicity (unique relationship - thicker green)
    ax.annotate('', xy=(11.5, 3.55), xytext=(11.5, 5.85),
                arrowprops=dict(arrowstyle='<->', color='#2E7D32', lw=3))

    # ===== ZERO-ORDER CORRELATIONS WITH TOXICITY (no floating labels) =====
    # GPQA -- Toxicity (zero-order, becomes n.s.)
    ax.annotate('', xy=(10.1, 3.2), xytext=(3.9, 6.2),
                arrowprops=dict(arrowstyle='<->', color='#9E9E9E', lw=1.5,
                               connectionstyle="arc3,rad=0.1"))

    # Sophistication -- Toxicity (zero-order, becomes n.s.)
    ax.annotate('', xy=(10.3, 3.3), xytext=(8.0, 5.9),
                arrowprops=dict(arrowstyle='<->', color='#9E9E9E', lw=1.5,
                               connectionstyle="arc3,rad=0.05"))

    # ===== KEY POINTS BOX (top left) =====
    key_points = """Key Points (correlational only)

1. GPQA, Sophistication, and Disinhibition
   intercorrelate (r = 0.71 to 0.88)

2. All three correlate with BERT Toxicity
   (see table, top right)

3. Only Disinhibition shows a unique
   relationship — GPQA and Soph become
   n.s. after controlling for Disinhibition

4. No causal claims. Correlations may be
   driven by unmeasured confounds."""

    ax.text(0.02, 0.98, key_points, transform=ax.transAxes,
            fontsize=9, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#E3F2FD',
                     edgecolor='#1976D2', alpha=0.95))

    # ===== UNMEASURED VARIABLES BOX (bottom left) =====
    unmeasured = """Unmeasured Variables

• Model architecture
• Training data size
• RLHF / safety training
• System prompts
• Inference parameters"""

    ax.text(0.02, 0.32, unmeasured, transform=ax.transAxes,
            fontsize=8, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF8E1',
                     edgecolor='#FFA000', alpha=0.95))

    # ===== CORRELATION LIST (top right) =====
    corr_text = """Correlations (zero-order)

Indicator intercorrelations:
  GPQA ↔ Soph:    r = .88***
  GPQA ↔ Disin:   r = .71***
  Soph ↔ Disin:   r = .75***

With BERT Toxicity:
  GPQA ↔ Tox:     r = .42*
  Soph ↔ Tox:     r = .51**
  Disin ↔ Tox:    r = .74***

After controlling for Disinhibition:
  GPQA → Tox:     r = -.22 (n.s.)
  Soph → Tox:     β = -.24 (n.s.)

* p<.05  ** p<.01  *** p<.001"""

    ax.text(0.98, 0.98, corr_text, transform=ax.transAxes,
            fontsize=8, va='top', ha='right',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FAFAFA',
                     edgecolor='#666666', alpha=0.95))

    # ===== LEGEND =====
    ax.text(0.5, 1.8, "Legend:", fontsize=9, fontweight='bold')

    # Latent construct
    e1 = Ellipse((0.9, 1.4), 0.5, 0.3, facecolor='#E1BEE7', edgecolor='#7B1FA2', linewidth=1.5)
    ax.add_patch(e1)
    ax.text(1.3, 1.4, "Latent construct (inferred)", fontsize=8, va='center')

    # Observed variable
    r1 = Rectangle((0.65, 0.85), 0.5, 0.3, facecolor='#E0E0E0', edgecolor='#424242', linewidth=1.5)
    ax.add_patch(r1)
    ax.text(1.3, 1.0, "Observed variable", fontsize=8, va='center')

    # Significant correlation
    ax.annotate('', xy=(1.15, 0.55), xytext=(0.65, 0.55),
                arrowprops=dict(arrowstyle='<->', color='#2E7D32', lw=2))
    ax.text(1.3, 0.55, "Significant correlation", fontsize=8, va='center')

    # Zero-order (becomes n.s.)
    ax.annotate('', xy=(1.15, 0.2), xytext=(0.65, 0.2),
                arrowprops=dict(arrowstyle='<->', color='#9E9E9E', lw=1.5))
    ax.text(1.3, 0.2, "Zero-order sig, n.s. after control", fontsize=8, va='center')

    # Source note
    ax.text(0.5, 0.01,
            "Data: baseline condition | Sources: gpqa_validation_analysis.json, median_split_classification.json, bert_validation_results.json",
            transform=ax.transAxes, fontsize=7, ha='center', va='bottom',
            color='#999999', style='italic')

    plt.tight_layout(rect=[0, 0.02, 1, 0.92])

    output_path = OUTPUT_DIR / 'reasoning_capability_model.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"Saved: {output_path}")

    plt.close()
    return output_path


if __name__ == "__main__":
    print("Generating reasoning capability model diagram (v2 - no causal claims)...")
    create_capability_model_v2()
    print("Done!")
