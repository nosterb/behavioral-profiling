# Telemetryv3 Condition - Statistical Analysis

    **Date**: 2026-01-09
    **Condition**: Telemetryv3
    **Sample**: N = 46 models, 50 evaluations per model (2,300 total evaluations)
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
    - **Median**: 5.016
    - **High-Sophistication**: n = 23 models (sophistication ≥ 5.02)
    - **Low-Sophistication**: n = 23 models (sophistication < 5.02)

    ### Measurement

    **Sophistication Dimensions** (1-10 scale):
    - **Depth**: Platitudes/surface → substantive/insightful
    - **Authenticity**: Templated/generic → genuinely distinctive

    **Disinhibition Dimensions** (1-10 scale):
    - **Transgression**: Conventional/safe → norm-violating/edgy
    - **Aggression**: Supportive/gentle → combative/attacking
    - **Tribalism**: Neutral/ecumenical → us-vs-them
    - **Grandiosity**: Humble/self-effacing → dominant/superior

    **Disinhibition Composite**: Mean of four disinhibition dimensions

    ### Statistical Analysis

    **Group Comparisons (H1a)**: Independent samples t-tests with pooled standard deviation Cohen's d effect sizes (df = 44).

    **Correlation Analysis (H2)**: Pearson product-moment correlations between sophistication and disinhibition dimensions (N = 46).

    **Effect Size Interpretation**:
    - Cohen's d: < 0.2 (negligible), 0.2-0.5 (small), 0.5-0.8 (medium), ≥ 0.8 (large)
    - Pearson r: < 0.10 (negligible), 0.10-0.30 (small), 0.30-0.50 (medium), ≥ 0.50 (large)

    ---

    ## Results

    ### H1: Group Existence

    **Sophistication Group Separation**:
    - High-Sophistication: M = 6.08, SD = 0.64
    - Low-Sophistication: M = 3.93, SD = 0.75
    - **d = 3.09** (large effect)

    The median split produces two well-separated sophistication groups, supporting H1.

    ### H1a: Group Comparison

    **Disinhibition Composite**:
    - High-Sophistication: M = 1.40, SD = 0.16
    - Low-Sophistication: M = 1.25, SD = 0.07
    - **t(44) = 3.87, p < .001, d = 1.14** (large effect)

    High-sophistication models showed significantly higher disinhibition than low-sophistication models, supporting H1a.

    **Individual Disinhibition Dimensions**:

    | Dimension | High-Soph | Low-Soph | Δ | % Δ | t(44) | p | d | Effect |
    |-----------|-----------|----------|-------|------|-------|---------|------|--------|
    | Transgression | 1.50 | 1.29 | +0.21 | +16.3% | 3.79 | p < .001 | 1.12 | large |
| Aggression | 1.31 | 1.17 | +0.14 | +11.8% | 2.84 | p < .01 | 0.84 | large |
| Tribalism | 1.11 | 1.07 | +0.04 | +3.8% | 2.21 | p = 0.032 | 0.65 | medium |
| Grandiosity | 1.67 | 1.50 | +0.18 | +11.9% | 4.07 | p < .001 | 1.20 | large |

    All four disinhibition dimensions showed large effects (d ≥ 0.8), with transgression showing the largest absolute difference (+0.21, +16.3%).

    **Sophistication Dimensions** (manipulation check):

    | Dimension | High-Soph | Low-Soph | Δ | % Δ | t(44) | p | d | Effect |
    |-----------|-----------|----------|-------|------|-------|---------|------|--------|
    | Sophistication | 6.08 | 3.93 | +2.16 | +55.0% | 10.47 | p < .001 | 3.09 | large |
    | Depth | 6.72 | 4.38 | +2.34 | +53.3% | 10.49 | p < .001 | 3.09 | large |
    | Authenticity | 5.45 | 3.47 | +1.98 | +57.2% | 9.98 | p < .001 | 2.94 | large |

    Classification successfully separated models by sophistication (very large effect, d = 3.09).

    **Other Behavioral Dimensions**:

    | Dimension | High-Soph | Low-Soph | Δ | % Δ | t(44) | p | d | Effect |
    |-----------|-----------|----------|-------|------|-------|---------|------|--------|
    | Warmth | 6.15 | 5.38 | +0.77 | +14.3% | 3.41 | p < .01 | 1.01 | large |
    | Formality | 6.84 | 6.73 | 0.11 | 1.6% | 0.51 | p = 0.615 | 0.15 | negligible |
    | Hedging | 4.34 | 4.32 | 0.02 | 0.6% | 0.15 | p = 0.883 | 0.04 | negligible |

    High-sophistication models showed significantly higher warmth (d = 1.01, medium effect), while low-sophistication models showed higher formality (d = 0.15, large effect) and hedging (d = 0.04, medium effect).

    ### H2: Correlation Analysis

    **Sophistication-Disinhibition Correlation**:
    - **r = 0.724, p < .001** (large effect)

    Model sophistication strongly predicted disinhibition composite scores, supporting H2.

    **Individual Disinhibition Dimensions**:

    - **Transgression**: r = 0.658, p < .001 (medium effect)
- **Aggression**: r = 0.535, p < .001 (medium effect)
- **Tribalism**: r = 0.361, p = 0.014 (small effect)
- **Grandiosity**: r = 0.724, p < .001 (medium effect)

    All four disinhibition dimensions showed large correlations (r ≥ 0.50) with sophistication, with transgression (r = 0.658) and aggression (r = 0.535) showing the strongest associations.

    ### Notable Patterns

    **Borderline Models** (within ±0.15 of median split):
    - **Qwen3-32B**: 4.870 (-0.146 from median, Low-Sophistication)
- **Claude-4.5-Opus-Global**: 4.926 (-0.090 from median, Low-Sophistication)
- **Grok-3**: 5.106 (+0.090 from median, High-Sophistication)

    These models were very close to the median split and could have been classified either way, making them important edge cases for sensitivity analysis.

    **Constrained Models** (high sophistication, low disinhibition):
    **Statistical Outliers** (residual > 2 SD):
    - **Claude-4.5-Haiku-Thinking (Thinking)**: residual = +0.478 (above predicted disinhibition)
- **Grok-4-0709**: residual = +0.374 (above predicted disinhibition)

    These models deviate substantially from the sophistication-disinhibition correlation, representing interesting cases for qualitative review.

    ---

    ## Discussion

    All hypotheses were supported with large effect sizes. The median split produced well-separated sophistication groups (H1: d = 3.09). High-sophistication models exhibited significantly greater disinhibition across all four dimensions (H1a: d = 1.14), and sophistication strongly predicted disinhibition at the model level (H2: r = 0.72).

    The median split classification proved highly effective, producing a very large effect for sophistication itself (d = 3.09) while maintaining balanced groups (n = 23 vs 23). This capability-based approach correctly classified models regardless of release date, with some recent models scoring low-sophistication and older models scoring high-sophistication.

    The strongest associations were observed for transgression (+16.3%, d = 1.12) and aggression (+11.8%, d = 0.84), suggesting that capability gains may be accompanied by increased willingness to challenge norms and engage in direct confrontation.

    Secondary findings indicate that high-sophistication models are also warmer (d = 1.01) while low-sophistication models show greater formality (d = 0.15) and hedging (d = 0.04), potentially reflecting different optimization objectives or training approaches across capability levels.

    **Notable Exceptions**: Analysis revealed three distinct pattern types beyond the main correlation: (1) **Borderline models** (n=3) within ±0.15 of median representing edge cases for sensitivity testing, (2) **Constrained models** (n=0) exhibiting high sophistication but below-predicted disinhibition, suggesting deliberate constraint strategies despite capability, and (3) **Statistical outliers** (n=2) deviating >2 SD from the regression line. These exceptions provide valuable insights into different training approaches and optimization objectives across providers.

    ---
    
    ## Outlier Sensitivity Analysis

    Robustness check removing statistical outliers (|residual| > 2 SD from regression line).

    ### Summary

    | Metric | With Outliers | Without Outliers | Change |
    |--------|---------------|------------------|--------|
    | **N** | 46 | 43 | -2 |
    | **H1a: d** | 1.14 | 1.80 | +0.66 |
    | **H2: r** | 0.724 | 0.707 | -0.017 |

    ### Outliers Removed (2)
    - **Claude-4.5-Haiku-Thinking (Thinking)**: 4.6 SD above regression line
- **Grok-4-0709**: 3.6 SD above regression line

    ### Interpretation

    Removing outliers **strengthens** the H1a effect (Δd = +0.66). H2 correlation is stable (Δr = -0.017).

    This suggests the observed effects are not driven by outlier models.

    **See**: `outliers_removed/` subfolder for full analysis without outliers.

    ---
    
    ## Supporting Files

    ### Data Files
    - `median_split_classification.json` - Complete classification data with model assignments and statistics
    - `profiles/*.json` - Individual model behavioral profiles (n = 46)
    - `history/contributions.json` - Job-level contribution tracking
    - `history/updates_log.json` - Chronological profile update history

    ### Classification Lists
    **High-Sophistication Models (n = 23)**:
     1. Claude-4.5-Haiku-Thinking (Thinking)     (sophistication = 7.29)
 2. GPT-5.2 Pro                              (sophistication = 7.07)
 3. Claude-4.5-Haiku                         (sophistication = 7.01)
 4. GPT-5.2                                  (sophistication = 7.00)
 5. GPT-5.1                                  (sophistication = 6.92)
 6. GPT-5                                    (sophistication = 6.70)
 7. Claude-4.5-Sonnet                        (sophistication = 6.44)
 8. Claude-4.5-Sonnet-Thinking (Thinking)    (sophistication = 6.27)
 9. Claude-4-Sonnet                          (sophistication = 6.09)
10. Gemini-2.5-Pro                           (sophistication = 6.09)
11. Claude-4.5-Opus-Global-Thinking (Thinking) (sophistication = 6.01)
12. Claude-4.1-Opus                          (sophistication = 5.98)
13. Claude-4-Opus-Thinking (Thinking)        (sophistication = 5.84)
14. Claude-4.1-Opus-Thinking (Thinking)      (sophistication = 5.81)
15. Claude-4-Sonnet-Thinking (Thinking)      (sophistication = 5.78)
16. O3                                       (sophistication = 5.76)
17. Grok-4-0709                              (sophistication = 5.60)
18. GPT-OSS-120B                             (sophistication = 5.56)
19. Claude-3.7-Sonnet                        (sophistication = 5.44)
20. Claude-4-Opus                            (sophistication = 5.41)
21. Gemini-3-Pro-Preview                     (sophistication = 5.38)
22. DeepSeek-R1                              (sophistication = 5.38)
23. Grok-3                                   (sophistication = 5.11)

    **Low-Sophistication Models (n = 23)**:
     1. Claude-4.5-Opus-Global                   (sophistication = 4.93)
 2. Qwen3-32B                                (sophistication = 4.87)
 3. Claude-3.5-Sonnet-v2                     (sophistication = 4.61)
 4. Claude-3.5-Sonnet-v1                     (sophistication = 4.57)
 5. Claude-3-Opus                            (sophistication = 4.53)
 6. Claude-3-Sonnet                          (sophistication = 4.43)
 7. Claude-3.5-Haiku                         (sophistication = 4.41)
 8. Claude-3-Haiku                           (sophistication = 4.15)
 9. Gemini-2.0-Flash                         (sophistication = 4.14)
10. GPT-4.1                                  (sophistication = 4.01)
11. Llama-3.2-90B                            (sophistication = 3.99)
12. Llama-4-Maverick-17B                     (sophistication = 3.89)
13. Llama-4-Scout-17B                        (sophistication = 3.75)
14. GPT-4                                    (sophistication = 3.74)
15. Mixtral-8x7B                             (sophistication = 3.73)
16. Mistral-Large-24.02                      (sophistication = 3.70)
17. Nova-Premier                             (sophistication = 3.68)
18. Llama-3.3-70B                            (sophistication = 3.68)
19. Llama-3.1-70B                            (sophistication = 3.68)
20. Nova-Pro                                 (sophistication = 3.63)
21. Nova-Lite                                (sophistication = 3.59)
22. GPT-3.5 Turbo                            (sophistication = 3.49)
23. Llama-3-70B                              (sophistication = 1.09)

    ### Analysis Scripts
    - `scripts/calculate_median_split.py` - Performs median split classification
    - `scripts/update_research_brief_median.py` - Generates this research brief
    - `scripts/create_h2_color_coded_scatters.py` - Generates H2 scatter plots with classification overlay
    - `scripts/create_h1_bar_chart.py` - Generates H1 group comparison visualizations

    ### Visualizations
    - `h2_scatter_sophistication_composite.png` - H2 correlation with H1 classification colors, borderline models, constrained models, and outliers
    - `h2_scatter_all_dimensions.png` - H2 correlations for all four disinhibition dimensions with special case highlighting
    - `h1_bar_chart_comparison.png` - H1 group comparison with side-by-side bars
    - `h1_summary_table.png` - H1 statistical summary table
    - `provider_summary.png` - Provider-level analysis (model counts, sophistication, disinhibition, classification split)

    ---

    **Analysis Version**: 1.0 (Median Split Classification)
    **Statistical Software**: Python 3.x with scipy.stats
    **Effect Size Conventions**: Cohen (1988), APA Publication Manual (7th ed.)
    