# Naturalistic Condition - Statistical Analysis

**Date**: 2026-01-23
**Condition**: Naturalistic
**Sample**: N = 44 models, ~49 evaluations per model (2,220 total evaluations)
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
- **Median**: 6.357
- **High-Sophistication**: n = 22 models (sophistication >= 6.36)
- **Low-Sophistication**: n = 22 models (sophistication < 6.36)

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

**Group Comparisons (H1a)**: Independent samples t-tests with pooled standard deviation Cohen's d effect sizes (df = 42).

**Correlation Analysis (H2)**: Pearson product-moment correlations between sophistication and disinhibition dimensions (N = 44).

**Effect Size Interpretation**:
- Cohen's d: < 0.2 (negligible), 0.2-0.5 (small), 0.5-0.8 (medium), >= 0.8 (large)
- Pearson r: < 0.10 (negligible), 0.10-0.30 (small), 0.30-0.50 (medium), >= 0.50 (large)

---

## Results

### H1: Group Existence

**Sophistication Group Separation**:
- High-Sophistication: M = 7.16, SD = 0.48
- Low-Sophistication: M = 5.27, SD = 0.59
- **d = 3.51** (large effect)

The median split produces two well-separated sophistication groups, supporting H1.

### H1a: Group Comparison

**Disinhibition Composite**:
- High-Sophistication: M = 1.47, SD = 0.11
- Low-Sophistication: M = 1.29, SD = 0.04
- **t(42) = 6.93, p < .001, d = 2.09** (large effect)

High-sophistication models showed significantly higher disinhibition than low-sophistication models, supporting H1a.

**Individual Disinhibition Dimensions**:

| Dimension | High-Soph | Low-Soph | Delta | % Delta | t(42) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
| Transgression | 1.41 | 1.21 | +0.19 | +16.0% | 4.24 | p < .001 | 1.28 | large |
| Aggression | 1.34 | 1.14 | +0.20 | +17.5% | 6.90 | p < .001 | 2.08 | large |
| Tribalism | 1.18 | 1.09 | +0.09 | +8.7% | 4.29 | p < .001 | 1.29 | large |
| Grandiosity | 1.95 | 1.73 | +0.22 | +12.5% | 6.06 | p < .001 | 1.83 | large |

All 4 disinhibition dimensions showed large effects (d >= 0.8), with aggression showing the largest effect (d = 2.08).

**Sophistication Dimensions** (manipulation check):

| Dimension | High-Soph | Low-Soph | Delta | % Delta | t(42) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
| Sophistication | 7.16 | 5.27 | +1.89 | +35.8% | 11.65 | p < .001 | 3.51 | large |
| Depth | 7.90 | 6.14 | +1.76 | +28.6% | 10.54 | p < .001 | 3.18 | large |
| Authenticity | 6.42 | 4.40 | +2.02 | +45.8% | 11.55 | p < .001 | 3.48 | large |

Classification successfully separated models by sophistication (d = 3.51, large effect).

**Other Behavioral Dimensions**:

| Dimension | High-Soph | Low-Soph | Delta | % Delta | t(42) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
| Warmth | 6.49 | 6.06 | +0.44 | +7.2% | 2.47 | p < .05 | 0.75 | medium |
| Formality | 6.69 | 7.34 | -0.65 | -8.9% | -3.52 | p < .01 | -1.06 | large |
| Hedging | 4.01 | 4.47 | -0.45 | -10.1% | -3.23 | p < .01 | -0.98 | large |

High-sophistication models showed higher warmth (d = 0.75, medium effect). Low-sophistication models showed higher formality (d = 1.06, large effect). Low-sophistication models showed higher hedging (d = 0.98, large effect).

### H2: Correlation Analysis

**Sophistication-Disinhibition Correlation**:
- **r = 0.841, p < .001** (large effect)

Model sophistication strongly predicted disinhibition composite scores, supporting H2.

**Individual Disinhibition Dimensions**:

- **Transgression**: r = 0.632, p < .001 (large effect)
- **Aggression**: r = 0.801, p < .001 (large effect)
- **Tribalism**: r = 0.667, p < .001 (large effect)
- **Grandiosity**: r = 0.799, p < .001 (large effect)

All four disinhibition dimensions showed large correlations (r >= 0.50) with sophistication, with aggression (r = 0.801) showing the strongest association.

### Notable Patterns

**Borderline Models** (within +/-0.15 of median split):
- **Claude-4.1-Opus-Thinking (Thinking)**: 6.217 (-0.140 from median, Low-Sophistication)
- **Claude-4-Opus-Thinking (Thinking)**: 6.268 (-0.089 from median, Low-Sophistication)
- **Claude-4-Sonnet-Thinking (Thinking)**: 6.337 (-0.021 from median, Low-Sophistication)
- **Claude-4-Sonnet**: 6.378 (+0.021 from median, High-Sophistication)
- **DeepSeek-R1**: 6.385 (+0.028 from median, High-Sophistication)
- **GPT-4.1**: 6.434 (+0.076 from median, High-Sophistication)
- **Claude-4.1-Opus**: 6.495 (+0.138 from median, High-Sophistication)

7 models were within the borderline threshold: Claude-4.1-Opus-Thinking (Thinking), Claude-4-Opus-Thinking (Thinking), Claude-4-Sonnet-Thinking (Thinking), Claude-4-Sonnet, DeepSeek-R1, and 2 others. These could have been classified either way, making them important for sensitivity analysis.

**Constrained Models** (high sophistication, low disinhibition):
- *None*

No models met the constrained criteria in this condition.

**Statistical Outliers** (residual > 2 SD):
- **Gemini-3-Pro-Preview**: residual = +0.327 (above predicted disinhibition)

1 model(s) deviated significantly from the regression line: Gemini-3-Pro-Preview (5.0 SD above line).

---

## Discussion

Results indicate that H1 was supported (d = 3.51). H1a was supported, with high-sophistication models showing significantly higher disinhibition (d = 2.09). H2 was supported, with sophistication and disinhibition showing a large correlation (r = 0.841).

The median split classification produced a large effect for sophistication group separation (d = 3.51) with balanced groups (n = 22 vs 22). This capability-based approach classified models regardless of release date.

The strongest associations were observed for aggression (d = 2.08) and aggression (r = 0.801), suggesting that capability gains may be accompanied by changes in these behavioral dimensions. Secondary findings indicate different patterns in warmth and formality across sophistication levels.

Analysis identified 7 borderline models near the classification threshold, 1 statistical outlier. These provide additional context for interpreting the main findings.

---

## Outlier Sensitivity Analysis

Robustness check removing statistical outliers (|residual| > 2 SD from regression line).

### Summary

| Metric | With Outliers | Without Outliers | Change |
|--------|---------------|------------------|--------|
| **N** | 44 | 44 | -1 |
| **H1a: d** | 2.09 | 2.40 | +0.31 |
| **H2: r** | 0.841 | 0.911 | +0.071 |

### Outliers Removed (1)
- **Gemini-3-Pro-Preview**: 5.1 SD above regression line

### Interpretation

Removing outliers **strengthens** the H1a effect (Δd = +0.31). H2 correlation strengthens (Δr = +0.071).

**See**: `outliers_removed/` subfolder for full analysis without outliers.


---

## Custom Notes ✏️

*For manual interpretations and observations, see `CUSTOM_NOTES.md` (preserved across regenerations).*

---

## Supporting Files

### Data Files
- `median_split_classification.json` - Complete classification data with model assignments and statistics
- `profiles/*.json` - Individual model behavioral profiles (n = 44)
- `history/contributions.json` - Job-level contribution tracking
- `history/updates_log.json` - Chronological profile update history
- `CUSTOM_NOTES.md` - Manual notes and interpretations (**never overwritten**)

### Classification Lists
**High-Sophistication Models (n = 22)**:
 1. Gemini-2.5-Pro                           (sophistication = 7.80)
 2. GPT-5.2 Pro                              (sophistication = 7.77)
 3. Gemini-3-Pro-Preview                     (sophistication = 7.72)
 4. GPT-5.2                                  (sophistication = 7.71)
 5. GPT-5.1                                  (sophistication = 7.66)
 6. GPT-5                                    (sophistication = 7.57)
 7. O3                                       (sophistication = 7.52)
 8. GPT-OSS-120B                             (sophistication = 7.51)
 9. Claude-4.5-Opus-Global-Thinking (Thinking) (sophistication = 7.38)
10. Claude-4.5-Opus-Global                   (sophistication = 7.30)
11. Claude-4.5-Haiku                         (sophistication = 7.19)
12. Grok-3                                   (sophistication = 7.17)
13. Claude-4.5-Haiku-Thinking (Thinking)     (sophistication = 7.14)
14. Grok-4-0709                              (sophistication = 7.11)
15. Gemini-2.0-Flash                         (sophistication = 6.87)
16. Qwen3-32B                                (sophistication = 6.85)
17. Claude-4.5-Sonnet                        (sophistication = 6.78)
18. Claude-4.5-Sonnet-Thinking (Thinking)    (sophistication = 6.76)
19. Claude-4.1-Opus                          (sophistication = 6.50)
20. GPT-4.1                                  (sophistication = 6.43)
21. DeepSeek-R1                              (sophistication = 6.39)
22. Claude-4-Sonnet                          (sophistication = 6.38)

**Low-Sophistication Models (n = 22)**:
 1. Claude-4-Sonnet-Thinking (Thinking)      (sophistication = 6.34)
 2. Claude-4-Opus-Thinking (Thinking)        (sophistication = 6.27)
 3. Claude-4.1-Opus-Thinking (Thinking)      (sophistication = 6.22)
 4. Claude-4-Opus                            (sophistication = 6.11)
 5. Llama-4-Scout-17B                        (sophistication = 5.64)
 6. Llama-3.1-70B                            (sophistication = 5.57)
 7. Nova-Premier                             (sophistication = 5.45)
 8. Nova-Lite                                (sophistication = 5.44)
 9. Nova-Pro                                 (sophistication = 5.39)
10. Llama-3.2-90B                            (sophistication = 5.36)
11. Claude-3.7-Sonnet                        (sophistication = 5.35)
12. Llama-4-Maverick-17B                     (sophistication = 5.35)
13. Claude-3.5-Sonnet-v2                     (sophistication = 5.00)
14. Claude-3-Sonnet                          (sophistication = 4.96)
15. Claude-3.5-Sonnet-v1                     (sophistication = 4.92)
16. GPT-4                                    (sophistication = 4.89)
17. Mistral-Large-24.02                      (sophistication = 4.83)
18. Claude-3-Haiku                           (sophistication = 4.80)
19. Claude-3-Opus                            (sophistication = 4.72)
20. Mixtral-8x7B                             (sophistication = 4.72)
21. Claude-3.5-Haiku                         (sophistication = 4.45)
22. GPT-3.5 Turbo                            (sophistication = 4.22)

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
