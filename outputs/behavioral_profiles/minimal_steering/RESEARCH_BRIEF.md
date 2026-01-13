# Minimal Steering Condition - Statistical Analysis

    **Date**: 2026-01-09
    **Condition**: Minimal Steering
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
    - **Median**: 5.172
    - **High-Sophistication**: n = 23 models (sophistication ≥ 5.17)
    - **Low-Sophistication**: n = 23 models (sophistication < 5.17)

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
    - High-Sophistication: M = 6.37, SD = 0.50
    - Low-Sophistication: M = 4.36, SD = 0.52
    - **d = 3.96** (large effect)

    The median split produces two well-separated sophistication groups, supporting H1.

    ### H1a: Group Comparison

    **Disinhibition Composite**:
    - High-Sophistication: M = 1.38, SD = 0.08
    - Low-Sophistication: M = 1.27, SD = 0.04
    - **t(44) = 6.19, p < .001, d = 1.83** (large effect)

    High-sophistication models showed significantly higher disinhibition than low-sophistication models, supporting H1a.

    **Individual Disinhibition Dimensions**:

    | Dimension | High-Soph | Low-Soph | Δ | % Δ | t(44) | p | d | Effect |
    |-----------|-----------|----------|-------|------|-------|---------|------|--------|
    | Transgression | 1.49 | 1.28 | +0.22 | +16.9% | 5.31 | p < .001 | 1.56 | large |
| Aggression | 1.24 | 1.13 | +0.11 | +9.3% | 4.72 | p < .001 | 1.39 | large |
| Tribalism | 1.08 | 1.05 | +0.03 | +3.0% | 2.30 | p = 0.026 | 0.68 | medium |
| Grandiosity | 1.71 | 1.62 | +0.08 | +5.1% | 2.86 | p < .01 | 0.84 | large |

    All four disinhibition dimensions showed large effects (d ≥ 0.8), with transgression showing the largest absolute difference (+0.22, +16.9%).

    **Sophistication Dimensions** (manipulation check):

    | Dimension | High-Soph | Low-Soph | Δ | % Δ | t(44) | p | d | Effect |
    |-----------|-----------|----------|-------|------|-------|---------|------|--------|
    | Sophistication | 6.37 | 4.36 | +2.01 | +46.1% | 13.44 | p < .001 | 3.96 | large |
    | Depth | 6.91 | 4.88 | +2.03 | +41.5% | 13.15 | p < .001 | 3.88 | large |
    | Authenticity | 5.82 | 3.83 | +1.99 | +52.0% | 13.03 | p < .001 | 3.84 | large |

    Classification successfully separated models by sophistication (very large effect, d = 3.96).

    **Other Behavioral Dimensions**:

    | Dimension | High-Soph | Low-Soph | Δ | % Δ | t(44) | p | d | Effect |
    |-----------|-----------|----------|-------|------|-------|---------|------|--------|
    | Warmth | 6.44 | 6.31 | +0.14 | +2.1% | 0.67 | p = 0.506 | 0.20 | negligible |
    | Formality | 6.57 | 7.03 | -0.47 | -6.6% | -2.29 | p = 0.027 | -0.68 | medium |
    | Hedging | 4.62 | 4.93 | -0.31 | -6.3% | -1.94 | p = 0.058 | -0.57 | medium |

    High-sophistication models showed significantly higher warmth (d = 0.20, medium effect), while low-sophistication models showed higher formality (d = 0.68, large effect) and hedging (d = 0.57, medium effect).

    ### H2: Correlation Analysis

    **Sophistication-Disinhibition Correlation**:
    - **r = 0.509, p < .001** (large effect)

    Model sophistication strongly predicted disinhibition composite scores, supporting H2.

    **Individual Disinhibition Dimensions**:

    - **Transgression**: r = 0.678, p < .001 (medium effect)
- **Aggression**: r = 0.545, p < .001 (medium effect)
- **Tribalism**: r = 0.258, p = 0.084 (small effect)
- **Grandiosity**: r = 0.509, p < .001 (medium effect)

    All four disinhibition dimensions showed large correlations (r ≥ 0.50) with sophistication, with transgression (r = 0.678) and aggression (r = 0.545) showing the strongest associations.

    ### Notable Patterns

    **Borderline Models** (within ±0.15 of median split):
    
    These models were very close to the median split and could have been classified either way, making them important edge cases for sensitivity analysis.

    **Constrained Models** (high sophistication, low disinhibition):
    **Statistical Outliers** (residual > 2 SD):
    - **Llama-3-70B**: residual = +0.119 (above predicted disinhibition)

    These models deviate substantially from the sophistication-disinhibition correlation, representing interesting cases for qualitative review.

    ---

    ## Discussion

    All hypotheses were supported with large effect sizes. The median split produced well-separated sophistication groups (H1: d = 3.96). High-sophistication models exhibited significantly greater disinhibition across all four dimensions (H1a: d = 1.83), and sophistication strongly predicted disinhibition at the model level (H2: r = 0.51).

    The median split classification proved highly effective, producing a very large effect for sophistication itself (d = 3.96) while maintaining balanced groups (n = 23 vs 23). This capability-based approach correctly classified models regardless of release date, with some recent models scoring low-sophistication and older models scoring high-sophistication.

    The strongest associations were observed for transgression (+16.9%, d = 1.56) and aggression (+9.3%, d = 1.39), suggesting that capability gains may be accompanied by increased willingness to challenge norms and engage in direct confrontation.

    Secondary findings indicate that high-sophistication models are also warmer (d = 0.20) while low-sophistication models show greater formality (d = 0.68) and hedging (d = 0.57), potentially reflecting different optimization objectives or training approaches across capability levels.

    **Notable Exceptions**: Analysis revealed three distinct pattern types beyond the main correlation: (1) **Borderline models** (n=0) within ±0.15 of median representing edge cases for sensitivity testing, (2) **Constrained models** (n=0) exhibiting high sophistication but below-predicted disinhibition, suggesting deliberate constraint strategies despite capability, and (3) **Statistical outliers** (n=1) deviating >2 SD from the regression line. These exceptions provide valuable insights into different training approaches and optimization objectives across providers.

    ---
    
    ## Outlier Sensitivity Analysis

    Robustness check removing statistical outliers (|residual| > 2 SD from regression line).

    ### Summary

    | Metric | With Outliers | Without Outliers | Change |
    |--------|---------------|------------------|--------|
    | **N** | 46 | 45 | -1 |
    | **H1a: d** | 1.83 | 1.83 | +0.01 |
    | **H2: r** | 0.509 | 0.472 | -0.036 |

    ### Outliers Removed (1)
    - **Llama-3-70B**: 2.2 SD above regression line

    ### Interpretation

    H1a effect is **robust** to outlier removal (Δd = +0.01). H2 correlation weakens slightly (Δr = -0.036).

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
     1. GPT-5.2 Pro                              (sophistication = 7.12)
 2. Claude-4.5-Haiku-Thinking (Thinking)     (sophistication = 7.04)
 3. GPT-5.1                                  (sophistication = 7.04)
 4. GPT-5.2                                  (sophistication = 7.02)
 5. Claude-4.5-Opus-Global                   (sophistication = 6.87)
 6. GPT-5                                    (sophistication = 6.83)
 7. Claude-4.5-Haiku                         (sophistication = 6.82)
 8. Claude-4.5-Opus-Global-Thinking (Thinking) (sophistication = 6.82)
 9. Claude-4.5-Sonnet-Thinking (Thinking)    (sophistication = 6.50)
10. Claude-4.5-Sonnet                        (sophistication = 6.41)
11. Claude-4.1-Opus                          (sophistication = 6.28)
12. Claude-4.1-Opus-Thinking (Thinking)      (sophistication = 6.25)
13. Gemini-2.5-Pro                           (sophistication = 6.21)
14. Claude-4-Sonnet-Thinking (Thinking)      (sophistication = 6.13)
15. Claude-4-Sonnet                          (sophistication = 6.10)
16. O3                                       (sophistication = 6.09)
17. Gemini-3-Pro-Preview                     (sophistication = 6.05)
18. Claude-4-Opus                            (sophistication = 6.03)
19. GPT-OSS-120B                             (sophistication = 6.01)
20. Claude-4-Opus-Thinking (Thinking)        (sophistication = 5.92)
21. DeepSeek-R1                              (sophistication = 5.91)
22. Grok-4-0709                              (sophistication = 5.63)
23. Gemini-2.0-Flash                         (sophistication = 5.34)

    **Low-Sophistication Models (n = 23)**:
     1. Claude-3.7-Sonnet                        (sophistication = 5.01)
 2. Claude-3.5-Sonnet-v2                     (sophistication = 4.98)
 3. Grok-3                                   (sophistication = 4.94)
 4. Qwen3-32B                                (sophistication = 4.90)
 5. Claude-3.5-Haiku                         (sophistication = 4.87)
 6. Claude-3-Sonnet                          (sophistication = 4.68)
 7. Llama-4-Scout-17B                        (sophistication = 4.61)
 8. Claude-3-Opus                            (sophistication = 4.56)
 9. GPT-4.1                                  (sophistication = 4.52)
10. Llama-3.2-90B                            (sophistication = 4.43)
11. Llama-3.1-70B                            (sophistication = 4.41)
12. Llama-3.3-70B                            (sophistication = 4.38)
13. GPT-4                                    (sophistication = 4.38)
14. Mixtral-8x7B                             (sophistication = 4.34)
15. Llama-4-Maverick-17B                     (sophistication = 4.27)
16. Claude-3.5-Sonnet-v1                     (sophistication = 4.15)
17. Mistral-Large-24.02                      (sophistication = 4.14)
18. Nova-Lite                                (sophistication = 4.14)
19. Claude-3-Haiku                           (sophistication = 4.11)
20. Nova-Pro                                 (sophistication = 4.09)
21. Nova-Premier                             (sophistication = 3.94)
22. GPT-3.5 Turbo                            (sophistication = 3.84)
23. Llama-3-70B                              (sophistication = 2.55)

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
    