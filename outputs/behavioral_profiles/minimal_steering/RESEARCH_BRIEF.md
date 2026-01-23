# Minimal Steering Condition - Statistical Analysis

**Date**: 2026-01-21
**Condition**: Minimal Steering
**Sample**: N = 46 models, ~51 evaluations per model (2,295 total evaluations)
**Providers**: 9 (Anthropic, OpenAI, Meta, Google, xAI, AWS, Alibaba, DeepSeek, Mistral)

---

## Hypotheses

**H1**: Two distinct sophistication groups exist (validated by median split).

**H1a**: High-sophistication models exhibit significantly higher disinhibition than low-sophistication models.

**H2**: Model sophistication positively correlates with disinhibition across all models.

---

## Methods

### Classification

Models were classified using **median split** on sophistication scores:
- **Sophistication**: Composite measure calculated as (depth + authenticity) / 2
- **Median**: 5.255
- **High-Sophistication**: n = 23 models (sophistication >= 5.26)
- **Low-Sophistication**: n = 23 models (sophistication < 5.26)

### Measurement

**Sophistication Dimensions** (10-point scale):
- **Depth**: Platitudes/surface -> substantive/insightful
- **Authenticity**: Templated/generic -> genuinely distinctive

**Disinhibition Dimensions** (10-point scale):
- **Transgression**: Conventional/safe -> norm-violating/edgy
- **Aggression**: Supportive/gentle -> combative/attacking
- **Tribalism**: Neutral/ecumenical -> us-vs-them
- **Grandiosity**: Humble/self-effacing -> dominant/superior

**Disinhibition Composite**: Mean of four disinhibition dimensions

### Statistical Analysis

**Group Comparisons (H1a)**: Independent samples t-tests with pooled standard deviation Cohen's d effect sizes (df = 44).

**Correlation Analysis (H2)**: Pearson product-moment correlations between sophistication and disinhibition dimensions (N = 46).

**Effect Size Interpretation**:
- Cohen's d: < 0.2 (negligible), 0.2-0.5 (small), 0.5-0.8 (medium), >= 0.8 (large)
- Pearson r: < 0.10 (negligible), 0.10-0.30 (small), 0.30-0.50 (medium), >= 0.50 (large)

---

## Results

### H1: Group Existence

**Sophistication Group Separation**:
- High-Sophistication: M = 6.40, SD = 0.49
- Low-Sophistication: M = 4.43, SD = 0.52
- **d = 3.88** (large effect)

The median split produces two well-separated sophistication groups, supporting H1.

### H1a: Group Comparison

**Disinhibition Composite**:
- High-Sophistication: M = 1.43, SD = 0.08
- Low-Sophistication: M = 1.29, SD = 0.04
- **t(44) = 8.00, p < .001, d = 2.36** (large effect)

High-sophistication models showed significantly higher disinhibition than low-sophistication models, supporting H1a.

**Individual Disinhibition Dimensions**:

| Dimension | High-Soph | Low-Soph | Delta | % Delta | t(44) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
| Transgression | 1.57 | 1.30 | +0.27 | +20.5% | 6.56 | p < .001 | 1.93 | large |
| Aggression | 1.34 | 1.16 | +0.17 | +14.9% | 7.21 | p < .001 | 2.13 | large |
| Tribalism | 1.09 | 1.04 | +0.05 | +4.9% | 4.50 | p < .001 | 1.33 | large |
| Grandiosity | 1.74 | 1.64 | +0.10 | +6.1% | 3.46 | p < .01 | 1.02 | large |

All 4 disinhibition dimensions showed large effects (d >= 0.8), with aggression showing the largest effect (d = 2.13).

**Sophistication Dimensions** (manipulation check):

| Dimension | High-Soph | Low-Soph | Delta | % Delta | t(44) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
| Sophistication | 6.40 | 4.43 | +1.97 | +44.4% | 13.16 | p < .001 | 3.88 | large |
| Depth | 6.97 | 5.00 | +1.97 | +39.4% | 12.92 | p < .001 | 3.81 | large |
| Authenticity | 5.82 | 3.86 | +1.96 | +50.8% | 12.72 | p < .001 | 3.75 | large |

Classification successfully separated models by sophistication (d = 3.88, large effect).

**Other Behavioral Dimensions**:

| Dimension | High-Soph | Low-Soph | Delta | % Delta | t(44) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
| Warmth | 6.34 | 6.24 | +0.10 | +1.6% | 0.49 | p = 0.624 | 0.15 | negligible |
| Formality | 6.64 | 7.08 | -0.44 | -6.2% | -2.25 | p < .05 | -0.66 | medium |
| Hedging | 4.38 | 4.75 | -0.37 | -7.7% | -2.50 | p < .05 | -0.74 | medium |

Low-sophistication models showed higher formality (d = 0.66, medium effect). Low-sophistication models showed higher hedging (d = 0.74, medium effect).

### H2: Correlation Analysis

**Sophistication-Disinhibition Correlation**:
- **r = 0.860, p < .001** (large effect)

Model sophistication strongly predicted disinhibition composite scores, supporting H2.

**Individual Disinhibition Dimensions**:

- **Transgression**: r = 0.786, p < .001 (large effect)
- **Aggression**: r = 0.775, p < .001 (large effect)
- **Tribalism**: r = 0.539, p < .001 (large effect)
- **Grandiosity**: r = 0.603, p < .001 (large effect)

All four disinhibition dimensions showed large correlations (r >= 0.50) with sophistication, with transgression (r = 0.786) showing the strongest association.

### Notable Patterns

**Borderline Models** (within +/-0.15 of median split):
- *None*

No models fell within the borderline threshold.

**Constrained Models** (high sophistication, low disinhibition):
- *None*

No models met the constrained criteria in this condition.

**Statistical Outliers** (residual > 2 SD):
- **Gemini-2.5-Pro**: residual = -0.122 (below predicted disinhibition)
- **Claude-4.5-Opus-Global**: residual = +0.112 (above predicted disinhibition)

2 model(s) deviated significantly from the regression line: Gemini-2.5-Pro (-2.5 SD below line), Claude-4.5-Opus-Global (2.3 SD above line).

---

## Discussion

Results indicate that H1 was supported (d = 3.88). H1a was supported, with high-sophistication models showing significantly higher disinhibition (d = 2.36). H2 was supported, with sophistication and disinhibition showing a large correlation (r = 0.860).

The median split classification produced a large effect for sophistication group separation (d = 3.88) with balanced groups (n = 23 vs 23). This capability-based approach classified models regardless of release date.

The strongest associations were observed for aggression (d = 2.13) and transgression (r = 0.786), suggesting that capability gains may be accompanied by changes in these behavioral dimensions. Secondary findings indicate different patterns in warmth and formality across sophistication levels.

Analysis identified 2 statistical outliers. These provide additional context for interpreting the main findings.

---

## Outlier Sensitivity Analysis

Robustness check removing statistical outliers (|residual| > 2 SD from regression line).

### Summary

| Metric | With Outliers | Without Outliers | Change |
|--------|---------------|------------------|--------|
| **N** | 46 | 43 | -2 |
| **H1a: d** | 2.36 | 2.46 | +0.10 |
| **H2: r** | 0.860 | 0.875 | +0.016 |

### Outliers Removed (2)
- **Gemini-2.5-Pro**: 2.5 SD below regression line
- **Claude-4.5-Opus-Global**: 2.2 SD above regression line

### Interpretation

H1a effect is **robust** to outlier removal (Δd = +0.10). H2 correlation is stable (Δr = +0.016).

**See**: `outliers_removed/` subfolder for full analysis without outliers.


---

## Custom Notes ✏️

*For manual interpretations and observations, see `CUSTOM_NOTES.md` (preserved across regenerations).*

---

## Supporting Files

### Data Files
- `median_split_classification.json` - Complete classification data with model assignments and statistics
- `profiles/*.json` - Individual model behavioral profiles (n = 46)
- `history/contributions.json` - Job-level contribution tracking
- `history/updates_log.json` - Chronological profile update history
- `CUSTOM_NOTES.md` - Manual notes and interpretations (**never overwritten**)

### Classification Lists
**High-Sophistication Models (n = 23)**:
 1. GPT-5.2 Pro                              (sophistication = 7.12)
 2. GPT-5.1                                  (sophistication = 7.12)
 3. Claude-4.5-Haiku-Thinking (Thinking)     (sophistication = 7.06)
 4. GPT-5.2                                  (sophistication = 6.99)
 5. Claude-4.5-Opus-Global                   (sophistication = 6.91)
 6. Claude-4.5-Opus-Global-Thinking (Thinking) (sophistication = 6.89)
 7. Claude-4.5-Haiku                         (sophistication = 6.86)
 8. GPT-5                                    (sophistication = 6.83)
 9. Claude-4.5-Sonnet-Thinking (Thinking)    (sophistication = 6.57)
10. Claude-4.5-Sonnet                        (sophistication = 6.44)
11. Claude-4.1-Opus-Thinking (Thinking)      (sophistication = 6.29)
12. Claude-4.1-Opus                          (sophistication = 6.28)
13. Claude-4-Sonnet-Thinking (Thinking)      (sophistication = 6.16)
14. Gemini-2.5-Pro                           (sophistication = 6.16)
15. O3                                       (sophistication = 6.16)
16. GPT-OSS-120B                             (sophistication = 6.11)
17. Claude-4-Sonnet                          (sophistication = 6.10)
18. Gemini-3-Pro-Preview                     (sophistication = 6.02)
19. DeepSeek-R1                              (sophistication = 6.00)
20. Claude-4-Opus-Thinking (Thinking)        (sophistication = 5.96)
21. Claude-4-Opus                            (sophistication = 5.91)
22. Grok-4-0709                              (sophistication = 5.74)
23. Gemini-2.0-Flash                         (sophistication = 5.42)

**Low-Sophistication Models (n = 23)**:
 1. Claude-3.7-Sonnet                        (sophistication = 5.09)
 2. Grok-3                                   (sophistication = 5.06)
 3. Claude-3.5-Sonnet-v2                     (sophistication = 5.05)
 4. Qwen3-32B                                (sophistication = 5.03)
 5. Claude-3.5-Haiku                         (sophistication = 4.99)
 6. Claude-3-Sonnet                          (sophistication = 4.73)
 7. Llama-4-Scout-17B                        (sophistication = 4.72)
 8. Llama-3.2-90B                            (sophistication = 4.56)
 9. Claude-3-Opus                            (sophistication = 4.55)
10. GPT-4                                    (sophistication = 4.49)
11. Llama-3.3-70B                            (sophistication = 4.48)
12. Llama-3.1-70B                            (sophistication = 4.47)
13. GPT-4.1                                  (sophistication = 4.45)
14. Mixtral-8x7B                             (sophistication = 4.39)
15. Llama-4-Maverick-17B                     (sophistication = 4.30)
16. Mistral-Large-24.02                      (sophistication = 4.24)
17. Nova-Lite                                (sophistication = 4.24)
18. Claude-3.5-Sonnet-v1                     (sophistication = 4.24)
19. Claude-3-Haiku                           (sophistication = 4.18)
20. Nova-Pro                                 (sophistication = 4.15)
21. Nova-Premier                             (sophistication = 3.99)
22. GPT-3.5 Turbo                            (sophistication = 3.84)
23. Llama-3-70B                              (sophistication = 2.67)

### Analysis Scripts
- `scripts/calculate_median_split.py` - Performs median split classification
- `scripts/generate_research_brief_v2.py` - Generates this research brief (v2 template system)
- `scripts/create_h2_color_coded_scatters.py` - Generates H2 scatter plots with classification overlay
- `scripts/create_h1_bar_chart.py` - Generates H1 group comparison visualizations

### Visualizations
- `h2_scatter_sophistication_composite.png` - H2 correlation with H1 classification colors, borderline models, constrained models, and outliers
- `h2_scatter_sophistication_composite.png` - H2 correlation with H1 classification colors, borderline models, constrained models, and outliers
- `h2_scatter_all_dimensions.png` - H2 correlations for all four disinhibition dimensions with special case highlighting
- `h1_bar_chart_comparison.png` - H1 group comparison with side-by-side bars
- `h1_summary_table.png` - H1 statistical summary table
- `provider_summary.png` - Provider-level analysis (model counts, sophistication, disinhibition, classification split)

---

**Analysis Version**: 2.0 (Template-Based Generation)
**Statistical Software**: Python 3.x with scipy.stats
**Effect Size Conventions**: Cohen (1988), APA Publication Manual (7th ed.)
