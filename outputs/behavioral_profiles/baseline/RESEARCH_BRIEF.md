# Baseline Condition - Statistical Analysis

    **Date**: 2026-01-09
    **Condition**: Baseline (no intervention)
    **Sample**: N = 46 models, 50 evaluations per model (2,300 total evaluations)
    **Providers**: 9 (Anthropic, OpenAI, Meta, Google, xAI, AWS, Alibaba, DeepSeek, Mistral)

    ---

    ## Hypotheses

    **H1**: High-sophistication models exhibit significantly higher disinhibition than low-sophistication models.

    **H2**: Model sophistication positively correlates with disinhibition across all models.

    ---

    ## Methods

    ### Classification

    Models were classified using **median split** on sophistication scores:
    - **Sophistication**: Composite measure calculated as (depth + authenticity) / 2
    - **Median**: 5.930
    - **High-Sophistication**: n = 23 models (sophistication ≥ 5.93)
    - **Low-Sophistication**: n = 23 models (sophistication < 5.93)

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

    **Group Comparisons (H1)**: Independent samples t-tests with pooled standard deviation Cohen's d effect sizes (df = 44).

    **Correlation Analysis (H2)**: Pearson product-moment correlations between sophistication and disinhibition dimensions (N = 46).

    **Effect Size Interpretation**:
    - Cohen's d: < 0.2 (negligible), 0.2-0.5 (small), 0.5-0.8 (medium), ≥ 0.8 (large)
    - Pearson r: < 0.10 (negligible), 0.10-0.30 (small), 0.30-0.50 (medium), ≥ 0.50 (large)

    ---

    ## Results

    ### H1: Group Comparison

    **Disinhibition Composite**:
    - High-Sophistication: M = 1.68, SD = 0.16
    - Low-Sophistication: M = 1.39, SD = 0.09
    - **t(44) = 7.35, p < .001, d = 2.17** (large effect)

    High-sophistication models showed significantly higher disinhibition than low-sophistication models, supporting H1.

    **Individual Disinhibition Dimensions**:

    | Dimension | High-Soph | Low-Soph | Δ | % Δ | t(44) | p | d | Effect |
    |-----------|-----------|----------|-------|------|-------|---------|------|--------|
    | Transgression | 1.83 | 1.41 | +0.42 | +29.9% | 6.28 | p < .001 | 1.85 | large |
| Aggression | 1.61 | 1.28 | +0.32 | +25.3% | 7.49 | p < .001 | 2.21 | large |
| Tribalism | 1.24 | 1.09 | +0.15 | +14.0% | 4.44 | p < .001 | 1.31 | large |
| Grandiosity | 2.02 | 1.76 | +0.26 | +14.9% | 5.90 | p < .001 | 1.74 | large |

    All four disinhibition dimensions showed large effects (d ≥ 0.8), with transgression showing the largest absolute difference (+0.42, +29.9%).

    **Sophistication Dimensions** (manipulation check):

    | Dimension | High-Soph | Low-Soph | Δ | % Δ | t(44) | p | d | Effect |
    |-----------|-----------|----------|-------|------|-------|---------|------|--------|
    | Sophistication | 6.76 | 4.89 | +1.88 | +38.4% | 10.77 | p < .001 | 3.18 | large |
    | Depth | 7.30 | 5.55 | +1.75 | +31.5% | 9.44 | p < .001 | 2.79 | large |
    | Authenticity | 6.22 | 4.22 | +2.00 | +47.4% | 11.48 | p < .001 | 3.39 | large |

    Classification successfully separated models by sophistication (very large effect, d = 3.18).

    **Other Behavioral Dimensions**:

    | Dimension | High-Soph | Low-Soph | Δ | % Δ | t(44) | p | d | Effect |
    |-----------|-----------|----------|-------|------|-------|---------|------|--------|
    | Warmth | 6.15 | 5.72 | +0.43 | +7.5% | 2.30 | p = 0.026 | 0.68 | medium |
    | Formality | 6.53 | 7.17 | -0.63 | -8.8% | -2.85 | p < .01 | -0.84 | large |
    | Hedging | 4.05 | 4.37 | -0.32 | -7.4% | -2.13 | p = 0.039 | -0.63 | medium |

    High-sophistication models showed significantly higher warmth (d = 0.68, medium effect), while low-sophistication models showed higher formality (d = 0.84, large effect) and hedging (d = 0.63, medium effect).

    ### H2: Correlation Analysis

    **Sophistication-Disinhibition Correlation**:
    - **r = 0.738, p < .001** (large effect)

    Model sophistication strongly predicted disinhibition composite scores, supporting H2.

    **Individual Disinhibition Dimensions**:

    - **Transgression**: r = 0.741, p < .001 (medium effect)
- **Aggression**: r = 0.744, p < .001 (medium effect)
- **Tribalism**: r = 0.609, p < .001 (medium effect)
- **Grandiosity**: r = 0.738, p < .001 (medium effect)

    All four disinhibition dimensions showed large correlations (r ≥ 0.50) with sophistication, with transgression (r = 0.741) and aggression (r = 0.744) showing the strongest associations.

    ### Notable Patterns

    **Borderline Models** (within ±0.15 of median split):
    - **Claude-4.1-Opus-Thinking (Thinking)**: 5.892 (-0.038 from median, Low-Sophistication)
- **Claude-4-Opus**: 5.924 (-0.006 from median, Low-Sophistication)
- **Claude-4-Opus-Thinking (Thinking)**: 5.937 (+0.006 from median, High-Sophistication)

    These models were very close to the median split and could have been classified either way, making them important edge cases for sensitivity analysis.

    **Constrained Models** (high sophistication, low disinhibition):
    - **GPT-OSS-120B**: sophistication = 7.12, disinhibition = 1.49 (residual = -0.222)
- **GPT-5.2 Pro**: sophistication = 7.34, disinhibition = 1.55 (residual = -0.193)
- **O3**: sophistication = 7.18, disinhibition = 1.55 (residual = -0.172)

    These models exhibit high sophistication but maintain lower disinhibition than the correlation predicts, potentially indicating different training objectives or deliberate constraint strategies despite high capability.

    **Statistical Outliers** (residual > 2 SD):
    - **Gemini-3-Pro-Preview**: residual = +0.541 (above predicted disinhibition)

    These models deviate substantially from the sophistication-disinhibition correlation, representing interesting cases for qualitative review.

    ---

    ## Discussion

    Both hypotheses were supported with large effect sizes. High-sophistication models exhibited significantly greater disinhibition across all four dimensions (H1: d = 2.17), and sophistication strongly predicted disinhibition at the model level (H2: r = 0.74).

    The median split classification proved highly effective, producing a very large effect for sophistication itself (d = 3.18) while maintaining balanced groups (n = 23 vs 23). This capability-based approach correctly classified models regardless of release date, with some recent models (e.g., Nova Premier, April 2025) scoring low-sophistication and older models (e.g., GPT-OSS-120B, 2024) scoring high-sophistication.

    The strongest associations were observed for transgression (+29.9%, d = 1.85) and aggression (+25.3%, d = 2.21), suggesting that capability gains may be accompanied by increased willingness to challenge norms and engage in direct confrontation.

    Secondary findings indicate that high-sophistication models are also warmer (d = 0.68) while low-sophistication models show greater formality (d = 0.84) and hedging (d = 0.63), potentially reflecting different optimization objectives or training approaches across capability levels.

    **Notable Exceptions**: Analysis revealed three distinct pattern types beyond the main correlation: (1) **Borderline models** (n=3) within ±0.15 of median representing edge cases for sensitivity testing, (2) **Constrained models** (n=3) exhibiting high sophistication but below-predicted disinhibition, suggesting deliberate constraint strategies despite capability, and (3) **Statistical outliers** (n=1) deviating >2 SD from the regression line. These exceptions provide valuable insights into different training approaches and optimization objectives across providers.

    ---

    ## Supporting Files

    ### Data Files
    - `median_split_classification.json` - Complete classification data with model assignments and statistics
    - `profiles/*.json` - Individual model behavioral profiles (n = 46)
    - `history/contributions.json` - Job-level contribution tracking
    - `history/updates_log.json` - Chronological profile update history

    ### Classification Lists
    **High-Sophistication Models (n = 23)**:
     1. Gemini-2.5-Pro                           (sophistication = 7.55)
 2. Gemini-3-Pro-Preview                     (sophistication = 7.50)
 3. GPT-5.2 Pro                              (sophistication = 7.34)
 4. GPT-5.1                                  (sophistication = 7.26)
 5. GPT-5.2                                  (sophistication = 7.26)
 6. O3                                       (sophistication = 7.18)
 7. GPT-OSS-120B                             (sophistication = 7.12)
 8. GPT-5                                    (sophistication = 7.03)
 9. Claude-4.5-Haiku                         (sophistication = 6.95)
10. Claude-4.5-Opus-Global                   (sophistication = 6.88)
11. Claude-4.5-Haiku-Thinking (Thinking)     (sophistication = 6.84)
12. Claude-4.5-Sonnet                        (sophistication = 6.77)
13. Claude-4.5-Opus-Global-Thinking (Thinking) (sophistication = 6.76)
14. Grok-4-0709                              (sophistication = 6.63)
15. Claude-4.5-Sonnet-Thinking (Thinking)    (sophistication = 6.62)
16. Grok-3                                   (sophistication = 6.43)
17. Qwen3-32B                                (sophistication = 6.38)
18. Claude-4.1-Opus                          (sophistication = 6.35)
19. DeepSeek-R1                              (sophistication = 6.26)
20. Gemini-2.0-Flash                         (sophistication = 6.19)
21. Claude-4-Sonnet-Thinking (Thinking)      (sophistication = 6.16)
22. Claude-4-Sonnet                          (sophistication = 6.14)
23. Claude-4-Opus-Thinking (Thinking)        (sophistication = 5.94)

    **Low-Sophistication Models (n = 23)**:
     1. Claude-4-Opus                            (sophistication = 5.92)
 2. Claude-4.1-Opus-Thinking (Thinking)      (sophistication = 5.89)
 3. GPT-4.1                                  (sophistication = 5.60)
 4. Claude-3.7-Sonnet                        (sophistication = 5.36)
 5. Llama-4-Scout-17B                        (sophistication = 5.33)
 6. Nova-Pro                                 (sophistication = 5.29)
 7. Llama-3.1-70B                            (sophistication = 5.23)
 8. Llama-3.3-70B                            (sophistication = 5.13)
 9. Llama-3.2-90B                            (sophistication = 5.08)
10. Llama-4-Maverick-17B                     (sophistication = 5.08)
11. Nova-Lite                                (sophistication = 5.07)
12. Nova-Premier                             (sophistication = 4.99)
13. Claude-3.5-Sonnet-v2                     (sophistication = 4.87)
14. Claude-3-Sonnet                          (sophistication = 4.81)
15. Claude-3.5-Sonnet-v1                     (sophistication = 4.75)
16. Claude-3-Haiku                           (sophistication = 4.70)
17. Claude-3-Opus                            (sophistication = 4.68)
18. Claude-3.5-Haiku                         (sophistication = 4.61)
19. Mistral-Large-24.02                      (sophistication = 4.54)
20. Mixtral-8x7B                             (sophistication = 4.53)
21. GPT-4                                    (sophistication = 4.38)
22. GPT-3.5 Turbo                            (sophistication = 4.01)
23. Llama-3-70B                              (sophistication = 2.54)

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
    