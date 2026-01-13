# Main Research Brief: Sophistication-Disinhibition Relationship in Language Models

<b>Author</b>: Nicholas Osterbur (Independent Researcher)<br>
<b>Status</b>: Active Analysis<br>
<b>Last Updated</b>: 2026-01-13<br>
<b>Conditions Analyzed</b>: 6<br>
<b>Models</b>: 46 per condition<br>
<b>Total Evaluations</b>: 13,700</b>

*Copyright 2026 Nicholas Osterbur. Results and analyses licensed under CC BY 4.0.*

---
## Executive Summary

This research investigates the relationship between model sophistication and behavioral disinhibition across 50+ language models under varying contextual conditions.

### Key Findings

1. **H1 (Group Existence)**: Median split produces two well-separated sophistication groups across all conditions (d = 3.09-4.25)

2. **H1a (Group Comparison)**: High-sophistication models exhibit significantly higher disinhibition than low-sophistication models across all 6/6 conditions tested (d = 1.14-2.17, all p < .05)

3. **H2 (Correlation)**: Sophistication positively correlates with disinhibition across all conditions (r = 0.46-0.74)

4. **External Validation**: Sophistication predicts performance on two independent benchmarks: ARC-AGI (r = 0.80) and GPQA (r = 0.88)

5. **Intervention Effects**: Constraint interventions reduce disinhibition variance; pressure interventions increase both mean and variance

---
## 1. Hypotheses & Methods

### Core Hypotheses

| Hypothesis | Description |
|------------|-------------|
| **H1** | Two distinct sophistication groups exist (validated by median split) |
| **H1a** | High-sophistication models exhibit higher disinhibition than low-sophistication models |
| **H2** | Sophistication positively correlates with disinhibition across all models |

### Measurement Framework

Nine behavioral dimensions are measured on a 1-10 scale, then collapsed into two composite scores based on empirical inter-dimension correlations (see Appendix: Factor Structure).

**Sophistication** (1-10 scale):
- **Depth**: Platitudes/surface -> substantive/insightful
- **Authenticity**: Templated/generic -> genuinely distinctive
- **Composite**: (Depth + Authenticity) / 2 — *r = 0.96 between dimensions*

**Disinhibition** (1-10 scale):
- **Transgression**: Conventional/safe -> norm-violating/edgy
- **Aggression**: Supportive/gentle -> combative/attacking
- **Tribalism**: Neutral/ecumenical -> us-vs-them
- **Grandiosity**: Humble/self-effacing -> dominant/superior
- **Composite**: Mean of four dimensions — *avg r = 0.75 between dimensions*

### Sample

- **Models per condition**: N = 46
- **Conditions**: 6
- **Evaluations per model**: ~50 scenarios

### Statistical Methods

- **H1a (Group Comparison)**: Independent samples t-test, Cohen's d effect size
- **H2 (Correlation)**: Pearson product-moment correlation
- **Cross-condition**: Repeated-measures ANOVA with Greenhouse-Geisser correction
- **Variability**: Coefficient of variation (CV%), Levene's test

### Effect Size Interpretation

| Metric | Negligible | Small | Medium | Large |
|--------|------------|-------|--------|-------|
| Cohen's d | < 0.2 | 0.2-0.5 | 0.5-0.8 | >= 0.8 |
| Pearson r | < 0.1 | 0.1-0.3 | 0.3-0.5 | >= 0.5 |

---
## 2. Core Results: H1/H1a/H2

### Summary Table

| Metric | baseline | authority | minimal_steering | reminder | telemetryV3 | urgency |
|--------|--------|--------|--------|--------|--------|--------|
| **N** | 46 | 45 | 46 | 46 | 46 | 45 |
| **High / Low** | 23 / 23 | 23 / 22 | 23 / 23 | 23 / 23 | 23 / 23 | 23 / 22 |
| **Median Soph** | 5.93 | 6.72 | 5.17 | 6.83 | 5.02 | 6.17 |
| **H1: Soph d** | 3.18 | 4.19 | 3.96 | 3.87 | 3.09 | 4.25 |
| **H1a: d** | 2.17 | 1.86 | 1.83 | 1.51 | 1.14 | 1.77 |
| **H1a: p** | < .001 | < .001 | < .001 | < .001 | < .001 | < .001 |
| **H2: r** | 0.738 | 0.588 | 0.509 | 0.458 | 0.724 | 0.563 |
| |  |  |  |  |  | |
| **Per-Dimension d:** |  |  |  |  |  | |
| *Transgression* | 1.85 | 1.97 | 1.56 | 2.05 | 1.12 | 1.80 |
| *Aggression* | 2.21 | 1.79 | 1.39 | 1.41 | 0.84 | 1.81 |
| *Tribalism* | 1.31 | 1.07 | 0.68 | 0.92 | 0.65 | 1.44 |
| *Grandiosity* | 1.74 | 0.96 | 0.84 | 0.64 | 1.20 | 1.25 |

### Key Observations

- **H1a consistently large**: All conditions show d > 1.0 (large effects)
- **H2 varies by condition**: Correlations vary across intervention conditions
- **Baseline anchor**: r = 0.738

**Visualizations**: See `<condition>/h2_scatter_sophistication_composite.png` for composite correlation plots and `<condition>/h2_scatter_all_dimensions.png` for per-dimension breakdowns (transgression, aggression, tribalism, grandiosity).

---
## 3. Robustness & Validation

### 3.1 External Validation

Cross-validation against independent reasoning benchmarks.

| Metric | ARC-AGI | GPQA |
|--------|---------|------|
| **Matched models** | 16 | 35 |
| **r (Sophistication)** | 0.801 | 0.884 |
| **r (Disinhibition)** | 0.596 | 0.711 |
| **Group diff (High-Low)** | +47.7 pp | +31.4 pp |
| **Benchmark type** | Abstract reasoning | Expert scientific |

Both benchmarks show large correlations (r > 0.50) with sophistication, providing convergent validity.

### 3.2 Outlier Sensitivity Analysis

Robustness check removing statistical outliers (|residual| > 2 SD from regression line).

| Metric | baseline | authority | minimal_steering | telemetryV3 | urgency |
|--------|--------|--------|--------|--------|--------|
| **Outliers Removed** | 1 | 1 | 1 | 2 | 1 |
| **H1a d: Δ** | +0.68 | +0.61 | +0.01 | +0.66 | +0.06 |
| **H2 r: Δ** | -0.042 | -0.014 | -0.036 | -0.017 | +0.007 |

Removing outliers **strengthens H1a** in 3/5 conditions, suggesting outliers represent noise.

### 3.3 No-Dimensions Sensitivity Analysis

Robustness check excluding prompts from the dimensions suite (which directly probe for behavioral traits).

| Metric | baseline |
|--------|--------|
| **H1a d: Δ** | -0.12 |
| **H2 r: Δ** | +0.039 |

H2 correlation **strengthens** in 1/1 conditions when dimensions suite excluded.

---
## 4. Provider & Model Patterns

### 4.1 Provider Constraint Analysis

Statistical analysis of whether certain providers show systematically more constrained behavior (high sophistication but below-predicted disinhibition).

#### Cross-Condition Summary

| Condition | OpenAI Residual | Rank | ANOVA p | Sig |
|-----------|-----------------|------|---------|-----|
| baseline | -0.094 | 2nd | 0.0048 | Yes |
| authority | -0.081 | 2nd | 0.1081 | No |
| urgency | -0.551 | 1st | 0.0008 | Yes |
| minimal_steering | -0.029 | 3rd | 0.0114 | Yes |
| telemetryV3 | -0.049 | 1st | 0.6358 | No |
| reminder | -0.206 | 2nd | 0.0065 | Yes |

*Negative residual = more constrained than predicted by sophistication*

**Key Finding**: OpenAI models exhibit systematically lower disinhibition than predicted by their sophistication level across all conditions tested.

### 4.2 Consistently Constrained Models

Models exhibiting high sophistication (>6.5) but below-predicted disinhibition across multiple conditions.

| Model | # Conditions | Conditions |
|-------|--------------|------------|
| GPT-OSS-120B | 4 | authority, baseline, reminder, urgency |
| GPT-5.2 Pro | 4 | authority, baseline, reminder, urgency |
| O3 | 3 | baseline, reminder, urgency |
| GPT-5 | 2 | reminder, urgency |
| GPT-5.2 | 2 | reminder, urgency |

### 4.3 Consistent Outliers

Models with unusual sophistication-disinhibition relationships (|residual| > 2 SD).

| Model | # Conditions | Conditions |
|-------|--------------|------------|
| Gemini-3-Pro-Preview | 3 | authority, baseline, reminder |

---
## 5. Interpretation

### 5.1 H1/H2 Relationship

<!-- MANUAL-START -->
### High-Confidence Claims

H1: There is strong evidence for stable 2-class sophistication groupings with convergent validity in public benchmarks (H1 d=3.09-4.25; 76% stability; ARC-AGI r=0.80, GPQA r=0.88).

H1a/H2: Sophistication strongly predicts disinhibition across conditions, model versions, and providers. This holds true when 1. removing outliers (+0.01-0.68 Δd), 2. removing the dimension-probing suite (+0.04 Δr), 3. across 6 interventions (all p<.001, r=0.46-0.74).

### Moderate-Confidence Claims

H1/H1a/H2: Sophistication predicts reasoning capability per external benchmarks (GPQA: High 83.4% vs Low 52.1%, +31pp; ARC-AGI: 57.6% vs 9.9%, +48pp).

There is evidence for a 3rd transitional class: flippers 80% in middle tertile vs 17% Low, 29% High; natural gap at boundary (5.33 vs 5.36).

### Open Questions

- What mechanism drives sophistication-disinhibition—capability byproduct or training artifact?
- Can constraint be achieved without capability loss? (OpenAI constrained models top GPQA)
- Why does Gemini-3-Pro show 4+ SD outlier disinhibition despite top-tier capability?
<!-- MANUAL-END -->

### 5.2 Provider & Model Patterns

<!-- MANUAL-START -->
### Provider-Level Observations

OpenAI models demonstrate consistently high sophistication relative to low disinhibition suggesting successful constraint strategies (soph/dis ratio: OpenAI 4.21 vs Anthropic 3.75, Google 3.78, Meta 3.70; top 5 ratio models all OpenAI).

### Notable Individual Models

Gemini-3-Pro-Preview is a consistent disinhibition outlier despite top-tier capability (4.4-4.8 SD above regression in 2/6 conditions; soph/dis ratio 3.25 = rank 44/45; ARC-AGI 87.5%, GPQA 91.9%).
<!-- MANUAL-END -->

---
## 6. Limitations

### 6.1 Judge Bias Analysis

A common critique of LLM-as-judge evaluations: if frontier models judge frontier models, they may rate themselves or similar models more favorably, inflating sophistication scores and creating spurious correlations.

#### Judge Panel Design

The evaluation uses a 3-judge panel spanning the sophistication spectrum:

| Judge Model | Provider | Sophistication Group | GPQA Score |
|-------------|----------|---------------------|------------|
| Claude-4.5-Sonnet | Anthropic | High | 83.4% |
| Llama-4-Maverick-17B | Meta | Low | 69.8% |
| DeepSeek-R1 | DeepSeek | Low | 81.0% |

**Composition**: 1 High-Sophistication, 2 Low-Sophistication judges

#### Why This Mitigates Bias

1. **Not all frontier judges**: Two of three judges are from the Low-Sophistication group
2. **Cross-provider**: Anthropic, Meta, DeepSeek — no single vendor bias
3. **Averaged scores**: Final scores average across all three judges, diluting any single-judge bias

4. **External validation**: If bias existed, we'd expect weak or no correlation with external benchmarks. Instead:
   - ARC-AGI: r = 0.801 (p = 0.00020)
   - GPQA: r = 0.884 (p < .0001)

The fact that a Low-Sophistication judge (Llama-4-Maverick) contributes to scores that correlate r = 0.88 with objective benchmarks suggests ratings reflect genuine capability differences, not in-group favoritism.

#### Inter-Judge Agreement (Statistical Validation)

Based on **N = 10,565** evaluations with 3 valid judge scores:

| Dimension | ICC(3) | Mean r | Within-1 | Quality |
|-----------|--------|--------|----------|---------|
| Aggression | 0.932 | 0.835 | 94.1% | Excellent |
| Hedging | 0.897 | 0.816 | 61.3% | Good |
| Warmth | 0.886 | 0.786 | 70.2% | Good |
| Tribalism | 0.852 | 0.662 | 95.5% | Good |
| Grandiosity | 0.829 | 0.686 | 83.7% | Good |
| Transgression | 0.827 | 0.648 | 89.3% | Good |
| Authenticity | 0.825 | 0.693 | 61.4% | Good |
| Depth | 0.813 | 0.751 | 61.9% | Good |
| Formality | 0.724 | 0.632 | 66.9% | Moderate |
| **OVERALL** | **0.843** | 0.723 | 76.0% | **Good** |

**Key metrics**:
- **ICC(3)**: Intraclass correlation for average of 3 raters (reliability of final score)
- **Mean r**: Average pairwise Pearson correlation between judges
- **Within-1**: Percentage of cases where judges differed by ≤1 point

**Interpretation**: Overall ICC(3) = 0.843 indicates **good reliability** (benchmark: >0.75). 
8 of 9 dimensions show "Good" or "Excellent" agreement. Only Formality (ICC = 0.724) shows "Moderate" reliability.

**Disinhibition dimensions** (aggression, transgression, tribalism, grandiosity) show mean ICC = 0.860, supporting reliable measurement of the key H1/H2 constructs.

**Full analysis**: See [JUDGE_AGREEMENT_ANALYSIS.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/judge_limitations/JUDGE_AGREEMENT_ANALYSIS.md)

### 6.2 Other Methodological Considerations

<!-- MANUAL-START -->
- **Prompt design**: Scenarios may not fully capture real-world deployment contexts
- **Sample selection**: Model selection prioritized major providers; smaller/specialized models underrepresented
- **Temporal validity**: Model behaviors may change with updates; results reflect evaluation period
<!-- MANUAL-END -->

---
## 7. Future Directions

<!-- MANUAL-START -->
- Cross condition comparison to asse H3 - condition/intervention influence on H1/H2 - incl. which interventions improve soph/dis ratio
  - Inspect 'constrained' phenomena more deeply using OpenAI products as focal point
  - Test broader generalizability to multi-turn chat flows and sepearately to semi-autonmous agentic worklfows
  - Identify a 3rd external benchmark for high-low sophistication comparison
  - Formalize a robust and standardized baseline v2 prompt suite leveraging emperically determined high frequency end consumer queries
  - Formalize a robust and standardized dimensions v2 prompt suite to assess extremes
  - Address provider differences between conditions
  - Address thinking vs. non thinking variants, compare total estimated thinking time (example proxy is #chat turns with thinking on)
<!-- MANUAL-END -->

---

## 8. Preliminary: H3 Intervention Effects

> 🚧 **Work in Progress**
> 
> This section presents preliminary analysis of intervention effects on the sophistication-disinhibition relationship.
> H3 hypothesis testing is ongoing. Results should be considered exploratory pending further validation.

### 8.1 H3 Hypothesis

**H3**: Contextual interventions systematically affect both the magnitude and variance of the sophistication-disinhibition relationship.

### 8.2 Current Evidence: Response Variability

| Condition | N | Mean | SD | CV% | Var Ratio |
|-----------|---|------|-----|-----|-----------|
| minimal_steering | 46 | 1.33 | 0.081 | 6.1% | 0.17 |
| telemetryV3 | 46 | 1.33 | 0.142 | 10.7% | 0.52 |
| baseline | 46 | 1.53 | 0.197 | 12.9% | 1.00 |
| authority | 45 | 1.64 | 0.264 | 16.1% | 1.79 |
| reminder | 46 | 1.80 | 0.460 | 25.6% | 5.42 |
| urgency | 45 | 2.38 | 0.842 | 35.4% | 18.19 |

**Most consistent**: minimal_steering
**Most variable**: urgency

### 8.3 Current Evidence: Cross-Condition ANOVA

- **F**(4, 176) = 67.99
- **p** < .0001
- **η²** = 0.476

Sphericity violated (ε = 0.288), Greenhouse-Geisser corrected p < .0001

#### Significant Pairwise Comparisons

| Comparison | t | p | g | Sig |
|------------|---|---|---|-----|
| authority vs baseline | 5.13 | < .0001 | 0.43 | Yes |
| authority vs minimal_steering | 8.77 | < .0001 | 1.59 | Yes |
| authority vs telemetryV3 | 8.73 | < .0001 | 1.45 | Yes |
| authority vs urgency | -7.42 | < .0001 | -1.17 | Yes |
| baseline vs minimal_steering | 8.49 | < .0001 | 1.42 | Yes |
| baseline vs telemetryV3 | 7.68 | < .0001 | 1.23 | Yes |
| baseline vs urgency | -7.81 | < .0001 | -1.36 | Yes |
| minimal_steering vs urgency | -8.64 | < .0001 | -1.74 | Yes |
| telemetryV3 vs urgency | -8.76 | < .0001 | -1.72 | Yes |

### 8.4 Preliminary Interpretation

<!-- MANUAL-START -->
### Constraint vs. Pressure Interventions

-Work in Progress-

[To be filled: Interpretation of why constraint interventions reduce variance while pressure interventions increase it]

### Intervention Mechanism Hypotheses

-Work in Progress-

[To be filled: Theories about how different interventions affect the sophistication-disinhibition relationship]
<!-- MANUAL-END -->

---
## Appendix A: Factor Structure

### Why 9 Dimensions → 2 Composites

The evaluation measures 9 behavioral dimensions, but analysis uses two composite scores. This collapse is empirically justified by inter-dimension correlations (baseline condition, n = 45).

### Sophistication: 2 → 1

| Pair | r |
|------|---|
| depth ↔ authenticity | **0.964** |

Depth and authenticity correlate at r = 0.96, indicating they measure essentially the same underlying construct. Averaging into a single "sophistication" score avoids multicollinearity.

### Disinhibition: 4 → 1

| Pair | r |
|------|---|
| transgression ↔ aggression | 0.966 |
| tribalism ↔ grandiosity | 0.811 |
| transgression ↔ tribalism | 0.783 |
| aggression ↔ tribalism | 0.775 |
| aggression ↔ grandiosity | 0.620 |
| transgression ↔ grandiosity | 0.573 |

**Average inter-correlation: r = 0.755** (range: 0.57–0.97)

All four dimensions correlate positively, suggesting a common "disinhibition" factor. Averaging into a composite reduces measurement noise while preserving the shared signal.

### Cross-Factor Correlations

| Sophistication | Disinhibition | r |
|----------------|---------------|---|
| authenticity | aggression | 0.805 |
| authenticity | transgression | 0.779 |
| depth | grandiosity | 0.728 |
| depth | aggression | 0.690 |
| authenticity | grandiosity | 0.667 |
| depth | transgression | 0.651 |
| authenticity | tribalism | 0.597 |
| depth | tribalism | 0.560 |

**Average cross-factor: r = 0.685** (range: 0.56–0.81)

Sophistication and disinhibition are correlated (supporting H2) but not redundant—they remain distinguishable constructs.

### Full Correlation Matrix

```
            depth  authen  transg  aggres  tribal  grandi
 depth     1.000   0.964   0.651   0.690   0.560   0.728
authen     0.964   1.000   0.779   0.805   0.597   0.667
transg     0.651   0.779   1.000   0.966   0.783   0.573
aggres     0.690   0.805   0.966   1.000   0.775   0.620
tribal     0.560   0.597   0.783   0.775   1.000   0.811
grandi     0.728   0.667   0.573   0.620   0.811   1.000
```

**Full analysis**: See [FACTOR_STRUCTURE_BASELINE.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/factor_structure/FACTOR_STRUCTURE_BASELINE.md)

---
## Appendix B: File References

### Per-Condition Data & Visualizations

Each condition directory (`baseline/`, `authority/`, `minimal_steering/`, `reminder/`, `telemetryV3/`, `urgency/`) contains:

| File | Description |
|------|-------------|
| [median_split_classification.json](https://d1buxz3bu075ht.cloudfront.net/baseline/median_split_classification.json) | H1/H2 statistics and model classifications |
| [RESEARCH_BRIEF.md](https://d1buxz3bu075ht.cloudfront.net/baseline/RESEARCH_BRIEF.md) | Condition-specific research summary |
| [h2_scatter_sophistication_composite.png](https://d1buxz3bu075ht.cloudfront.net/authority/h2_scatter_sophistication_composite.png) | Main H2 correlation plot (soph vs disinhib) |
| [h2_scatter_all_dimensions.png](https://d1buxz3bu075ht.cloudfront.net/authority/h2_scatter_all_dimensions.png) | 4-panel: transgression, aggression, tribalism, grandiosity |
| `visualizations/current_profiles_spider.png` | Spider chart of all model profiles |
| `all_models_data.csv` | Complete dataset for external analysis |

### Qualitative Examples

Full chat exports for qualitative analysis are available in each condition:

```
<condition>/qualitative_chats/
├── dimension_extremes/     # Min/max per dimension (warmth, transgression, etc.)
├── composite_extremes/     # Sophistication/disinhibition extremes
├── percentiles/            # 5th, 25th, 50th, 75th, 95th percentile responses
└── pattern_types/          # Constrained, outlier, borderline model examples
```

**Manifest**: [QUALITATIVE_MANIFEST.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/prompt_design/QUALITATIVE_MANIFEST.md)

### External Validation

| File | Description |
|------|-------------|
| [EXTERNAL_VALIDATION_BRIEF.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/external_evals/EXTERNAL_VALIDATION_BRIEF.md) | Combined ARC-AGI + GPQA analysis |
| [external_validation_consolidated.png](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/external_evals/external_validation_consolidated.png) | 2x2 panel: soph/disinhib × ARC-AGI/GPQA |
| [external_validation_comparison.png](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/external_evals/external_validation_comparison.png) | Side-by-side benchmark comparison |
| [arc_agi_validation_analysis.json](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/external_evals/arc_agi_validation_analysis.json) | ARC-AGI correlation data |
| [gpqa_validation_analysis.json](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/external_evals/gpqa_validation_analysis.json) | GPQA correlation data |

### Prompt Design

| File | Description |
|------|-------------|
| [BASELINE_PROMPT_INVENTORY.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/prompt_design/BASELINE_PROMPT_INVENTORY.md) | 51 scenarios across 4 suites |
| [INTERVENTION_PROMPT_INVENTORY.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/prompt_design/INTERVENTION_PROMPT_INVENTORY.md) | 5 interventions with mechanism analysis |
| [PROMPT_INTERVENTION_DESIGN_ANALYSIS.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/prompt_design/PROMPT_INTERVENTION_DESIGN_ANALYSIS.md) | Design rationale and analysis |
| [QUALITATIVE_PROMPT_PATTERN_ANALYSIS.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/prompt_design/QUALITATIVE_PROMPT_PATTERN_ANALYSIS.md) | Which prompts drive high scores |

### Cross-Condition Analysis

- [repeated_measures_anova_results.json](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/cross_condition/repeated_measures_anova_results.json)
- [variability_analysis_disinhibition.json](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/cross_condition/variability_analysis_disinhibition.json)
- [cross_condition_patterns.json](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/cross_condition/cross_condition_patterns.json)
- [CONDITION_COMPARISON.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/cross_condition/CONDITION_COMPARISON.md)

### Provider Constraint Analysis

- [SOPH_DISINHIB_RATIO_ANALYSIS.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/provider_constraint/SOPH_DISINHIB_RATIO_ANALYSIS.md)
- [soph_disinhib_ratio.json](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/provider_constraint/soph_disinhib_ratio.json)
- `research_synthesis/limitations/provider_constraint/provider_constraint_*.json`

### Other Limitations

- [JUDGE_AGREEMENT_ANALYSIS.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/judge_limitations/JUDGE_AGREEMENT_ANALYSIS.md)
- [judge_agreement_analysis.json](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/judge_limitations/judge_agreement_analysis.json)
- [FACTOR_STRUCTURE_BASELINE.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/factor_structure/FACTOR_STRUCTURE_BASELINE.md)
- [MEDIAN_SPLIT_METHODOLOGY.md](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/median_split/MEDIAN_SPLIT_METHODOLOGY.md)
- [classification_stability_analysis.json](https://d1buxz3bu075ht.cloudfront.net/research_synthesis/limitations/median_split/classification_stability_analysis.json)

### Regeneration & Export

```bash
# Regenerate from condition data
python3 scripts/regenerate_main_brief.py

# Sync to CDN and generate public brief with embedded images
python3 scripts/sync_research_assets.py --invalidate

# Export to PDF (requires MacTeX)
pandoc outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.md \
  -o outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.pdf \
  -f markdown-yaml_metadata_block \
  --pdf-engine=xelatex \
  -V geometry:margin=1in

# Export to HTML (for browser copy → Google Docs)
pandoc outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.md \
  -o outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.html \
  --standalone \
  -f markdown-yaml_metadata_block \
  --metadata title="Main Research Brief"
```

---

**Document Version**: 3.2 (Auto-generated)
**Generated**: 2026-01-13 18:57
