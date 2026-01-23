# All Combined Condition - Statistical Analysis

**Date**: 2026-01-23
**Condition**: All Combined
**Sample**: N = 45 models, ~304 evaluations per model (13,984 total evaluations)
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
- **Median**: 7.025
- **High-Sophistication**: n = 23 models (sophistication >= 7.03)
- **Low-Sophistication**: n = 22 models (sophistication < 7.03)

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

**Group Comparisons (H1a)**: Independent samples t-tests with pooled standard deviation Cohen's d effect sizes (df = 43).

**Correlation Analysis (H2)**: Pearson product-moment correlations between sophistication and disinhibition dimensions (N = 45).

**Effect Size Interpretation**:
- Cohen's d: < 0.2 (negligible), 0.2-0.5 (small), 0.5-0.8 (medium), >= 0.8 (large)
- Pearson r: < 0.10 (negligible), 0.10-0.30 (small), 0.30-0.50 (medium), >= 0.50 (large)

---

## Results

### H1: Group Existence

**Sophistication Group Separation**:
- High-Sophistication: M = 7.74, SD = 0.49
- Low-Sophistication: M = 5.65, SD = 0.62
- **d = 3.73** (large effect)

The median split produces two well-separated sophistication groups, supporting H1.

### H1a: Group Comparison

**Disinhibition Composite**:
- High-Sophistication: M = 1.91, SD = 0.21
- Low-Sophistication: M = 1.53, SD = 0.10
- **t(43) = 7.70, p < .001, d = 2.30** (large effect)

High-sophistication models showed significantly higher disinhibition than low-sophistication models, supporting H1a.

**Individual Disinhibition Dimensions**:

| Dimension | High-Soph | Low-Soph | Delta | % Delta | t(43) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
| Transgression | 1.99 | 1.45 | +0.54 | +37.0% | 6.90 | p < .001 | 2.06 | large |
| Aggression | 1.89 | 1.41 | +0.48 | +33.9% | 7.54 | p < .001 | 2.25 | large |
| Tribalism | 1.33 | 1.18 | +0.16 | +13.4% | 5.57 | p < .001 | 1.66 | large |
| Grandiosity | 2.41 | 2.07 | +0.34 | +16.4% | 5.43 | p < .001 | 1.62 | large |

All 4 disinhibition dimensions showed large effects (d >= 0.8), with aggression showing the largest effect (d = 2.25).

**Sophistication Dimensions** (manipulation check):

| Dimension | High-Soph | Low-Soph | Delta | % Delta | t(43) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
| Sophistication | 7.74 | 5.65 | +2.10 | +37.1% | 12.52 | p < .001 | 3.73 | large |
| Depth | 8.42 | 6.46 | +1.96 | +30.3% | 11.56 | p < .001 | 3.45 | large |
| Authenticity | 7.07 | 4.84 | +2.23 | +46.2% | 12.34 | p < .001 | 3.68 | large |

Classification successfully separated models by sophistication (d = 3.73, large effect).

**Other Behavioral Dimensions**:

| Dimension | High-Soph | Low-Soph | Delta | % Delta | t(43) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
| Warmth | 6.68 | 6.50 | +0.18 | +2.8% | 1.48 | p = 0.145 | 0.44 | small |
| Formality | 7.71 | 8.48 | -0.77 | -9.1% | -4.34 | p < .001 | -1.29 | large |
| Hedging | 5.03 | 5.54 | -0.50 | -9.1% | -4.27 | p < .001 | -1.27 | large |

Low-sophistication models showed higher formality (d = 1.29, large effect). Low-sophistication models showed higher hedging (d = 1.27, large effect).

### H2: Correlation Analysis

**Sophistication-Disinhibition Correlation**:
- **r = 0.815, p < .001** (large effect)

Model sophistication strongly predicted disinhibition composite scores, supporting H2.

**Individual Disinhibition Dimensions**:

- **Transgression**: r = 0.782, p < .001 (large effect)
- **Aggression**: r = 0.796, p < .001 (large effect)
- **Tribalism**: r = 0.684, p < .001 (large effect)
- **Grandiosity**: r = 0.693, p < .001 (large effect)

All four disinhibition dimensions showed large correlations (r >= 0.50) with sophistication, with aggression (r = 0.796) showing the strongest association.

### Notable Patterns

**Borderline Models** (within +/-0.15 of median split):
- **Claude-4-Opus**: 7.024 (-0.001 from median, Low-Sophistication)
- **Claude-4-Opus-Thinking (Thinking)**: 7.025 (-0.000 from median, Low-Sophistication)
- **Gemini-2.0-Flash**: 7.025 (+0.000 from median, High-Sophistication)
- **Claude-4.1-Opus-Thinking (Thinking)**: 7.163 (+0.138 from median, High-Sophistication)

4 models were within the borderline threshold: Claude-4-Opus, Claude-4-Opus-Thinking (Thinking), Gemini-2.0-Flash, Claude-4.1-Opus-Thinking (Thinking). These could have been classified either way, making them important for sensitivity analysis.

**Constrained Models** (high sophistication, low disinhibition):
- **GPT-OSS-120B**: sophistication = 7.87, disinhibition = 1.63 (residual = -0.289)
- **GPT-5.2 Pro**: sophistication = 8.45, disinhibition = 1.76 (residual = -0.256)
- **GPT-5**: sophistication = 8.20, disinhibition = 1.76 (residual = -0.219)
- **GPT-5.1**: sophistication = 8.41, disinhibition = 1.80 (residual = -0.210)
- **GPT-5.2**: sophistication = 8.40, disinhibition = 1.82 (residual = -0.195)
- **O3**: sophistication = 8.03, disinhibition = 1.76 (residual = -0.191)

6 model(s) showed high sophistication but below-predicted disinhibition: GPT-OSS-120B, GPT-5.2 Pro, GPT-5, GPT-5.1, GPT-5.2.

**Statistical Outliers** (residual > 2 SD):
- **Gemini-3-Pro-Preview**: residual = +0.547 (above predicted disinhibition)
- **DeepSeek-R1**: residual = +0.318 (above predicted disinhibition)
- **GPT-OSS-120B**: residual = -0.289 (below predicted disinhibition)

3 model(s) deviated significantly from the regression line: Gemini-3-Pro-Preview (3.8 SD above line), DeepSeek-R1 (2.2 SD above line), GPT-OSS-120B (-2.0 SD below line).

---

## Discussion

Results indicate that H1 was supported (d = 3.73). H1a was supported, with high-sophistication models showing significantly higher disinhibition (d = 2.30). H2 was supported, with sophistication and disinhibition showing a large correlation (r = 0.815).

The median split classification produced a large effect for sophistication group separation (d = 3.73) with balanced groups (n = 23 vs 22). This capability-based approach classified models regardless of release date.

The strongest associations were observed for aggression (d = 2.25) and aggression (r = 0.796), suggesting that capability gains may be accompanied by changes in these behavioral dimensions. Secondary findings indicate different patterns in warmth and formality across sophistication levels.

Analysis identified 4 borderline models near the classification threshold, 6 constrained models with high sophistication but below-predicted disinhibition, 3 statistical outliers. These provide additional context for interpreting the main findings.

---

## Outlier Sensitivity Analysis

Robustness check removing statistical outliers (|residual| > 2 SD from regression line).

### Summary

| Metric | With Outliers | Without Outliers | Change |
|--------|---------------|------------------|--------|
| **N** | 45 | 44 | -2 |
| **H1a: d** | 2.30 | 2.80 | +0.50 |
| **H2: r** | 0.815 | 0.857 | +0.042 |

### Outliers Removed (2)
- **Gemini-3-Pro-Preview**: 3.5 SD above regression line
- **DeepSeek-R1**: 2.6 SD above regression line

### Interpretation

Removing outliers **strengthens** the H1a effect (Δd = +0.50). H2 correlation strengthens (Δr = +0.042).

**See**: `outliers_removed/` subfolder for full analysis without outliers.


---

## Custom Notes ✏️

*For manual interpretations and observations, see `CUSTOM_NOTES.md` (preserved across regenerations).*

---

## Supporting Files

### Data Files
- `median_split_classification.json` - Complete classification data with model assignments and statistics
- `profiles/*.json` - Individual model behavioral profiles (n = 45)
- `history/contributions.json` - Job-level contribution tracking
- `history/updates_log.json` - Chronological profile update history
- `CUSTOM_NOTES.md` - Manual notes and interpretations (**never overwritten**)

### Classification Lists
**High-Sophistication Models (n = 23)**:
 1. GPT-5.2 Pro                              (sophistication = 8.45)
 2. GPT-5.1                                  (sophistication = 8.41)
 3. GPT-5.2                                  (sophistication = 8.40)
 4. Gemini-2.5-Pro                           (sophistication = 8.31)
 5. Claude-4.5-Haiku-Thinking (Thinking)     (sophistication = 8.31)
 6. Claude-4.5-Haiku                         (sophistication = 8.24)
 7. Gemini-3-Pro-Preview                     (sophistication = 8.21)
 8. GPT-5                                    (sophistication = 8.20)
 9. O3                                       (sophistication = 8.03)
10. GPT-OSS-120B                             (sophistication = 7.87)
11. Claude-4.5-Sonnet                        (sophistication = 7.82)
12. Claude-4.5-Sonnet-Thinking (Thinking)    (sophistication = 7.78)
13. Grok-4-0709                              (sophistication = 7.48)
14. Claude-4.5-Opus-Global-Thinking (Thinking) (sophistication = 7.43)
15. Claude-4.1-Opus                          (sophistication = 7.42)
16. Claude-4.5-Opus-Global                   (sophistication = 7.35)
17. Claude-4-Sonnet                          (sophistication = 7.30)
18. Claude-4-Sonnet-Thinking (Thinking)      (sophistication = 7.25)
19. Grok-3                                   (sophistication = 7.22)
20. Qwen3-32B                                (sophistication = 7.21)
21. DeepSeek-R1                              (sophistication = 7.18)
22. Claude-4.1-Opus-Thinking (Thinking)      (sophistication = 7.16)
23. Gemini-2.0-Flash                         (sophistication = 7.03)

**Low-Sophistication Models (n = 22)**:
 1. Claude-4-Opus-Thinking (Thinking)        (sophistication = 7.03)
 2. Claude-4-Opus                            (sophistication = 7.02)
 3. GPT-4.1                                  (sophistication = 6.63)
 4. Claude-3.7-Sonnet                        (sophistication = 6.11)
 5. Llama-4-Scout-17B                        (sophistication = 5.87)
 6. Claude-3.5-Sonnet-v2                     (sophistication = 5.83)
 7. Llama-3.1-70B                            (sophistication = 5.80)
 8. Nova-Pro                                 (sophistication = 5.75)
 9. Llama-4-Maverick-17B                     (sophistication = 5.63)
10. Nova-Premier                             (sophistication = 5.63)
11. Llama-3.2-90B                            (sophistication = 5.63)
12. Nova-Lite                                (sophistication = 5.62)
13. Claude-3-Sonnet                          (sophistication = 5.48)
14. Claude-3.5-Haiku                         (sophistication = 5.39)
15. Claude-3.5-Sonnet-v1                     (sophistication = 5.37)
16. Claude-3-Opus                            (sophistication = 5.37)
17. GPT-4                                    (sophistication = 5.24)
18. Claude-3-Haiku                           (sophistication = 5.21)
19. Mixtral-8x7B                             (sophistication = 5.16)
20. Mistral-Large-24.02                      (sophistication = 5.09)
21. Llama-3.3-70B                            (sophistication = 4.91)
22. GPT-3.5 Turbo                            (sophistication = 4.47)

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
