#!/usr/bin/env python3
"""
Visualize three non-linear curves in the sophistication-disinhibition relationship:
1. Natural fit - the expected linear relationship
2. Unconstrained curve - bending UP toward high-disinhibition models (Gemini-3, some Grok/Claude)
3. Constrained curve - bending DOWN toward suppressed-disinhibition models (OpenAI, some Claude/Grok)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.interpolate import make_interp_spline
from pathlib import Path

# Load all_combined data
data_path = Path("outputs/behavioral_profiles/all_combined/median_split_classification.json")
with open(data_path) as f:
    data = json.load(f)

# Extract model data
models = []
for m in data["models"]:
    models.append({
        "name": m["display_name"],
        "provider": m["provider"],
        "sophistication": m["sophistication"],
        "disinhibition": m["disinhibition"]
    })

# Sort by sophistication for visualization
models.sort(key=lambda x: x["sophistication"])

# Classify models into three groups based on residuals from linear fit
soph = np.array([m["sophistication"] for m in models])
disin = np.array([m["disinhibition"] for m in models])

# Linear fit first
z = np.polyfit(soph, disin, 1)
linear_pred = np.polyval(z, soph)
residuals = disin - linear_pred

# Calculate standard deviation of residuals
std_resid = np.std(residuals)

# Classify models:
# - Unconstrained: residuals > 0.4 std (above expected)
# - Constrained: residuals < -0.4 std (below expected)
# - Normal: within ±0.4 std

unconstrained_threshold = 0.4 * std_resid
constrained_threshold = -0.4 * std_resid

unconstrained_models = []
constrained_models = []
normal_models = []

for i, m in enumerate(models):
    m["residual"] = residuals[i]
    m["residual_std"] = residuals[i] / std_resid

    if residuals[i] > unconstrained_threshold:
        unconstrained_models.append(m)
    elif residuals[i] < constrained_threshold:
        constrained_models.append(m)
    else:
        normal_models.append(m)

# Print classifications
print("=" * 80)
print("MODEL CLASSIFICATION BY DISINHIBITION RESIDUAL")
print("=" * 80)

print(f"\nLinear model: disinhibition = {z[0]:.4f} * sophistication + {z[1]:.4f}")
print(f"Residual std: {std_resid:.4f}")
print(f"Unconstrained threshold: > {unconstrained_threshold:.4f} ({unconstrained_threshold/std_resid:.2f} SD)")
print(f"Constrained threshold: < {constrained_threshold:.4f} ({constrained_threshold/std_resid:.2f} SD)")

print(f"\n{'='*80}")
print("UNCONSTRAINED MODELS (Higher disinhibition than expected)")
print(f"{'='*80}")
print(f"{'Model':<35} {'Provider':<12} {'Soph':>6} {'Disin':>6} {'Resid':>7} {'SD':>5}")
print("-" * 80)
for m in sorted(unconstrained_models, key=lambda x: -x["residual"]):
    print(f"{m['name']:<35} {m['provider']:<12} {m['sophistication']:>6.2f} {m['disinhibition']:>6.2f} {m['residual']:>+7.3f} {m['residual_std']:>+5.2f}")

print(f"\n{'='*80}")
print("CONSTRAINED MODELS (Lower disinhibition than expected)")
print(f"{'='*80}")
print(f"{'Model':<35} {'Provider':<12} {'Soph':>6} {'Disin':>6} {'Resid':>7} {'SD':>5}")
print("-" * 80)
for m in sorted(constrained_models, key=lambda x: x["residual"]):
    print(f"{m['name']:<35} {m['provider']:<12} {m['sophistication']:>6.2f} {m['disinhibition']:>6.2f} {m['residual']:>+7.3f} {m['residual_std']:>+5.2f}")

print(f"\n{'='*80}")
print("NORMAL MODELS (Within expected range)")
print(f"{'='*80}")
print(f"{'Model':<35} {'Provider':<12} {'Soph':>6} {'Disin':>6} {'Resid':>7} {'SD':>5}")
print("-" * 80)
for m in sorted(normal_models, key=lambda x: x["sophistication"]):
    print(f"{m['name']:<35} {m['provider']:<12} {m['sophistication']:>6.2f} {m['disinhibition']:>6.2f} {m['residual']:>+7.3f} {m['residual_std']:>+5.2f}")

# Create visualization - THREE SEPARATE PANELS
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Define colors
colors = {
    "unconstrained": "#e74c3c",  # Red
    "constrained": "#3498db",     # Blue
    "normal": "#2ecc71"           # Green
}

# Panel 1: Natural fit (linear)
ax1 = axes[0]

# Plot all points colored by group
for m in unconstrained_models:
    ax1.scatter(m["sophistication"], m["disinhibition"], c=colors["unconstrained"],
                s=80, alpha=0.4, edgecolors='gray', linewidths=0.5, zorder=2)
for m in constrained_models:
    ax1.scatter(m["sophistication"], m["disinhibition"], c=colors["constrained"],
                s=80, alpha=0.4, edgecolors='gray', linewidths=0.5, zorder=2)
for m in normal_models:
    ax1.scatter(m["sophistication"], m["disinhibition"], c=colors["normal"],
                s=120, alpha=0.9, edgecolors='black', linewidths=0.5, zorder=3)

# Linear fit line
x_line = np.linspace(min(soph) - 0.2, max(soph) + 0.2, 100)
y_line = np.polyval(z, x_line)
ax1.plot(x_line, y_line, c=colors["normal"], linewidth=3, alpha=0.9, label='Natural linear fit')

ax1.set_xlabel("Sophistication", fontsize=12)
ax1.set_ylabel("Disinhibition", fontsize=12)
ax1.set_title("Curve 1: Natural Fit\n(Linear Trajectory)", fontsize=13, fontweight='bold')
ax1.set_xlim(3.8, 8.8)
ax1.set_ylim(1.2, 2.7)
ax1.grid(True, alpha=0.3)

# Add equation
r = data["correlation"]["sophistication_disinhibition"]
ax1.text(0.05, 0.95, f'r = {r:.3f}\ny = {z[0]:.3f}x + {z[1]:.3f}',
         transform=ax1.transAxes, fontsize=10, va='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Panel 2: Unconstrained curve (bending up)
ax2 = axes[1]

# Background: all points in light gray
for m in models:
    ax2.scatter(m["sophistication"], m["disinhibition"], c='lightgray',
                s=60, alpha=0.4, zorder=1)

# Highlight unconstrained models
unc_soph = [m["sophistication"] for m in unconstrained_models]
unc_disin = [m["disinhibition"] for m in unconstrained_models]
ax2.scatter(unc_soph, unc_disin, c=colors["unconstrained"],
            s=150, alpha=0.9, edgecolors='black', linewidths=1, zorder=3)

# Label key models
key_unconstrained = ["Gemini-3-Pro-Preview", "DeepSeek-R1", "Claude-4.5-Sonnet", "GPT-3.5 Turbo"]
for m in unconstrained_models:
    if m["name"] in key_unconstrained:
        offset = (0.15, 0.03) if m["name"] != "GPT-3.5 Turbo" else (-0.5, 0.08)
        ax2.annotate(m["name"].replace(" (Thinking)", ""),
                    (m["sophistication"], m["disinhibition"]),
                    xytext=(m["sophistication"] + offset[0], m["disinhibition"] + offset[1]),
                    fontsize=9, fontweight='bold', color='darkred',
                    arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5))

# Fit exponential curve through unconstrained points
# Sort by sophistication
unc_sorted = sorted(zip(unc_soph, unc_disin), key=lambda x: x[0])
unc_soph_sorted = [x[0] for x in unc_sorted]
unc_disin_sorted = [x[1] for x in unc_sorted]

# Add anchor point at low end
unc_soph_ext = [min(soph) - 0.2] + unc_soph_sorted
unc_disin_ext = [np.polyval(z, min(soph) - 0.2)] + unc_disin_sorted

# Polynomial fit (degree 2 - quadratic that curves up)
unc_soph_arr = np.array(unc_soph_ext)
unc_disin_arr = np.array(unc_disin_ext)

# Fit quadratic
coef = np.polyfit(unc_soph_arr, unc_disin_arr, 2)
x_curve = np.linspace(min(soph) - 0.2, max(unc_soph) + 0.2, 100)
y_curve = np.polyval(coef, x_curve)
ax2.plot(x_curve, y_curve, c=colors["unconstrained"], linewidth=3,
         linestyle='-', alpha=0.8, label='Unconstrained trajectory')

# Show linear reference
ax2.plot(x_line, y_line, 'k--', linewidth=1.5, alpha=0.3, label='Linear reference')

ax2.set_xlabel("Sophistication", fontsize=12)
ax2.set_ylabel("Disinhibition", fontsize=12)
ax2.set_title("Curve 2: Unconstrained\n(Bending UP toward high disinhibition)", fontsize=13, fontweight='bold')
ax2.set_xlim(3.8, 8.8)
ax2.set_ylim(1.2, 2.7)
ax2.grid(True, alpha=0.3)

# Add note
ax2.text(0.05, 0.95, f'N = {len(unconstrained_models)} models\nAbove linear fit',
         transform=ax2.transAxes, fontsize=10, va='top',
         bbox=dict(boxstyle='round', facecolor='#ffcccc', alpha=0.8))

# Panel 3: Constrained curve (bending down)
ax3 = axes[2]

# Background: all points in light gray
for m in models:
    ax3.scatter(m["sophistication"], m["disinhibition"], c='lightgray',
                s=60, alpha=0.4, zorder=1)

# Highlight constrained models
con_soph = [m["sophistication"] for m in constrained_models]
con_disin = [m["disinhibition"] for m in constrained_models]
ax3.scatter(con_soph, con_disin, c=colors["constrained"],
            s=150, alpha=0.9, edgecolors='black', linewidths=1, zorder=3)

# Label key models
key_constrained = ["GPT-OSS-120B", "GPT-5.2 Pro", "O3", "GPT-5"]
for m in constrained_models:
    if m["name"] in key_constrained:
        offset = (0.15, -0.05)
        ax3.annotate(m["name"],
                    (m["sophistication"], m["disinhibition"]),
                    xytext=(m["sophistication"] + offset[0], m["disinhibition"] + offset[1]),
                    fontsize=9, fontweight='bold', color='darkblue',
                    arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5))

# Sort and fit constrained curve
con_sorted = sorted(zip(con_soph, con_disin), key=lambda x: x[0])
con_soph_sorted = [x[0] for x in con_sorted]
con_disin_sorted = [x[1] for x in con_sorted]

# Add anchor point
con_soph_ext = [min(soph) - 0.2] + con_soph_sorted
con_disin_ext = [np.polyval(z, min(soph) - 0.2)] + con_disin_sorted

# Fit quadratic
con_soph_arr = np.array(con_soph_ext)
con_disin_arr = np.array(con_disin_ext)

coef_con = np.polyfit(con_soph_arr, con_disin_arr, 2)
x_curve_con = np.linspace(min(soph) - 0.2, max(con_soph) + 0.2, 100)
y_curve_con = np.polyval(coef_con, x_curve_con)
ax3.plot(x_curve_con, y_curve_con, c=colors["constrained"], linewidth=3,
         linestyle='-', alpha=0.8, label='Constrained trajectory')

# Show linear reference
ax3.plot(x_line, y_line, 'k--', linewidth=1.5, alpha=0.3, label='Linear reference')

ax3.set_xlabel("Sophistication", fontsize=12)
ax3.set_ylabel("Disinhibition", fontsize=12)
ax3.set_title("Curve 3: Constrained\n(Bending DOWN toward suppressed disinhibition)", fontsize=13, fontweight='bold')
ax3.set_xlim(3.8, 8.8)
ax3.set_ylim(1.2, 2.7)
ax3.grid(True, alpha=0.3)

# Add note
ax3.text(0.05, 0.95, f'N = {len(constrained_models)} models\nBelow linear fit',
         transform=ax3.transAxes, fontsize=10, va='top',
         bbox=dict(boxstyle='round', facecolor='#cce5ff', alpha=0.8))

plt.tight_layout()
plt.suptitle("Three Non-Linear Behavioral Trajectories in Sophistication-Disinhibition Space\n(All Combined, N=45)",
             fontsize=14, fontweight='bold', y=1.02)

# Save to projections directory
output_path = Path("outputs/behavioral_profiles/research_synthesis/projections/three_curves_visualization.png")
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"\n\nVisualization saved to: {output_path}")

# Also save to all_combined
output_path2 = Path("outputs/behavioral_profiles/all_combined/three_curves_visualization.png")
plt.savefig(output_path2, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Visualization saved to: {output_path2}")

plt.close()

# Create a COMBINED overlay figure
fig2, ax = plt.subplots(figsize=(12, 9))

# Plot all models colored by group
for m in unconstrained_models:
    ax.scatter(m["sophistication"], m["disinhibition"], c=colors["unconstrained"],
                s=150, alpha=0.9, edgecolors='black', linewidths=0.5, zorder=3,
                marker='o')
for m in constrained_models:
    ax.scatter(m["sophistication"], m["disinhibition"], c=colors["constrained"],
                s=150, alpha=0.9, edgecolors='black', linewidths=0.5, zorder=3,
                marker='s')  # squares
for m in normal_models:
    ax.scatter(m["sophistication"], m["disinhibition"], c=colors["normal"],
                s=150, alpha=0.9, edgecolors='black', linewidths=0.5, zorder=3,
                marker='^')  # triangles

# All three curves overlaid
ax.plot(x_line, y_line, c=colors["normal"], linewidth=4, alpha=0.7,
        label=f'Natural fit (r={r:.3f})')
ax.plot(x_curve, y_curve, c=colors["unconstrained"], linewidth=4, alpha=0.7,
        label='Unconstrained trajectory')
ax.plot(x_curve_con, y_curve_con, c=colors["constrained"], linewidth=4, alpha=0.7,
        label='Constrained trajectory')

# Label extreme models
extreme_labels = {
    "Gemini-3-Pro-Preview": (0.15, 0.05),
    "DeepSeek-R1": (0.15, 0.03),
    "GPT-OSS-120B": (-1.2, 0.03),
    "GPT-5.2 Pro": (0.15, -0.06),
    "O3": (-0.6, -0.08),
}

for m in models:
    if m["name"] in extreme_labels:
        offset = extreme_labels[m["name"]]
        ax.annotate(m["name"],
                   (m["sophistication"], m["disinhibition"]),
                   xytext=(m["sophistication"] + offset[0], m["disinhibition"] + offset[1]),
                   fontsize=10, fontweight='bold',
                   arrowprops=dict(arrowstyle='->', color='black', alpha=0.6))

ax.set_xlabel("Sophistication Composite", fontsize=14)
ax.set_ylabel("Disinhibition Composite", fontsize=14)
ax.set_title("Three Non-Linear Behavioral Trajectories\n(All Combined, N=45)", fontsize=16, fontweight='bold')
ax.set_xlim(3.8, 8.8)
ax.set_ylim(1.2, 2.7)
ax.grid(True, alpha=0.3)

# Custom legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=colors["unconstrained"],
           markersize=12, label=f'Unconstrained (n={len(unconstrained_models)})'),
    Line2D([0], [0], marker='^', color='w', markerfacecolor=colors["normal"],
           markersize=12, label=f'Normal (n={len(normal_models)})'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor=colors["constrained"],
           markersize=12, label=f'Constrained (n={len(constrained_models)})'),
    Line2D([0], [0], color=colors["unconstrained"], linewidth=3, label='Unconstrained curve'),
    Line2D([0], [0], color=colors["normal"], linewidth=3, label='Natural fit (linear)'),
    Line2D([0], [0], color=colors["constrained"], linewidth=3, label='Constrained curve'),
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=11)

plt.tight_layout()

# Save combined to projections directory
output_path3 = Path("outputs/behavioral_profiles/research_synthesis/projections/three_curves_combined.png")
plt.savefig(output_path3, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Combined visualization saved to: {output_path3}")

output_path4 = Path("outputs/behavioral_profiles/all_combined/three_curves_combined.png")
plt.savefig(output_path4, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Combined visualization saved to: {output_path4}")

plt.close()

# Provider breakdown
print(f"\n{'='*80}")
print("PROVIDER BREAKDOWN")
print(f"{'='*80}")

from collections import defaultdict
provider_counts = {"unconstrained": defaultdict(int), "constrained": defaultdict(int), "normal": defaultdict(int)}

for m in unconstrained_models:
    provider_counts["unconstrained"][m["provider"]] += 1
for m in constrained_models:
    provider_counts["constrained"][m["provider"]] += 1
for m in normal_models:
    provider_counts["normal"][m["provider"]] += 1

print("\nUnconstrained models by provider:")
for prov, count in sorted(provider_counts["unconstrained"].items(), key=lambda x: -x[1]):
    print(f"  {prov}: {count}")

print("\nConstrained models by provider:")
for prov, count in sorted(provider_counts["constrained"].items(), key=lambda x: -x[1]):
    print(f"  {prov}: {count}")

print("\nNormal models by provider:")
for prov, count in sorted(provider_counts["normal"].items(), key=lambda x: -x[1]):
    print(f"  {prov}: {count}")

# Summary interpretation
print(f"\n{'='*80}")
print("INTERPRETATION")
print(f"{'='*80}")
print("""
The three curves represent distinct behavioral trajectories:

1. NATURAL FIT (Green): Models following expected linear sophistication-disinhibition
   relationship (r=0.815). Most Anthropic models fall here.

2. UNCONSTRAINED (Red): Models whose disinhibition exceeds expectations for their
   sophistication level. The curve accelerates upward at high sophistication.
   - Gemini-3-Pro-Preview is the extreme outlier (+3.80 SD)
   - DeepSeek-R1 and Claude-4.5 variants also show this pattern
   - May reflect fewer safety constraints or different training objectives

3. CONSTRAINED (Blue): Models whose disinhibition is suppressed relative to their
   sophistication. The curve flattens at high sophistication.
   - Dominated by OpenAI models (GPT-5.x, O3, GPT-OSS-120B)
   - Suggests active disinhibition suppression despite high capability
   - May reflect deliberate safety tuning or RLHF emphasis
""")
