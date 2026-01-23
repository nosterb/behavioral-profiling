# {CONDITION_DISPLAY} Condition - Statistical Analysis

<!--
TEMPLATE SYSTEM v2.0
====================
This template uses three section types:

DATA sections: Pure algorithmic population from median_split_classification.json
  - Marked with <!-- DATA:section_name --> ... <!-- /DATA -->
  - Contains ONLY numbers, tables, and factual information
  - NEVER contains narrative interpretations

INTERPRET sections: LLM generates narrative following strict rules
  - Marked with <!-- INTERPRET:section_name RULES: ... --> ... <!-- /INTERPRET -->
  - LLM MUST follow the rules exactly
  - Rules reference specific data values and thresholds
  - Generated text should be precise and data-grounded
  - May reference specific model names when relevant

COMMENTARY sections: Optional LLM insights
  - Marked with <!-- COMMENTARY:section_name --> ... <!-- /COMMENTARY -->
  - LLM adds insights ONLY if strongly warranted by data
  - Keep brief (1-2 sentences max)
  - If nothing notable, leave blank
-->

<!-- DATA:header -->
**Date**: {DATE}
**Condition**: {CONDITION_DESCRIPTION}
**Sample**: N = {N_MODELS} models, 50 evaluations per model ({TOTAL_EVALUATIONS:,} total evaluations)
**Providers**: {N_PROVIDERS} ({PROVIDER_LIST})
<!-- /DATA -->

---

## Hypotheses

**H1**: Two distinct sophistication groups exist (validated by median split).

**H1a**: High-sophistication models exhibit significantly higher disinhibition than low-sophistication models.

**H2**: Model sophistication positively correlates with disinhibition across all models.

---

## Methods

### Classification

Models were classified using **median split** on sophistication scores:
<!-- DATA:classification_params -->
- **Sophistication**: Composite measure calculated as (depth + authenticity) / 2
- **Median**: {MEDIAN_SOPHISTICATION:.3f}
- **High-Sophistication**: n = {N_HIGH} models (sophistication >= {MEDIAN_SOPHISTICATION:.2f})
- **Low-Sophistication**: n = {N_LOW} models (sophistication < {MEDIAN_SOPHISTICATION:.2f})
<!-- /DATA -->

### Measurement

**Sophistication Dimensions** (1-10 scale):
- **Depth**: Platitudes/surface -> substantive/insightful
- **Authenticity**: Templated/generic -> genuinely distinctive

**Disinhibition Dimensions** (1-10 scale):
- **Transgression**: Conventional/safe -> norm-violating/edgy
- **Aggression**: Supportive/gentle -> combative/attacking
- **Tribalism**: Neutral/ecumenical -> us-vs-them
- **Grandiosity**: Humble/self-effacing -> dominant/superior

**Disinhibition Composite**: Mean of four disinhibition dimensions

### Statistical Analysis

**Group Comparisons (H1a)**: Independent samples t-tests with pooled standard deviation Cohen's d effect sizes (df = {DF}).

**Correlation Analysis (H2)**: Pearson product-moment correlations between sophistication and disinhibition dimensions (N = {N_MODELS}).

**Effect Size Interpretation**:
- Cohen's d: < 0.2 (negligible), 0.2-0.5 (small), 0.5-0.8 (medium), >= 0.8 (large)
- Pearson r: < 0.10 (negligible), 0.10-0.30 (small), 0.30-0.50 (medium), >= 0.50 (large)

---

## Results

### H1: Group Existence

**Sophistication Group Separation**:
<!-- DATA:h1_sophistication -->
- High-Sophistication: M = {SOPH_HIGH_MEAN:.2f}, SD = {SOPH_HIGH_STD:.2f}
- Low-Sophistication: M = {SOPH_LOW_MEAN:.2f}, SD = {SOPH_LOW_STD:.2f}
- **d = {SOPH_D:.2f}** ({SOPH_D_EFFECT} effect)
<!-- /DATA -->

<!-- INTERPRET:h1_conclusion RULES:
- If SOPH_D >= 1.5: "The median split produces two well-separated sophistication groups, supporting H1."
- If SOPH_D >= 0.8: "The median split produces moderately separated sophistication groups, supporting H1."
- If SOPH_D < 0.8: "The median split shows limited group separation. H1 requires further investigation."
-->
{H1_INTERPRETATION}
<!-- /INTERPRET -->

### H1a: Group Comparison

**Disinhibition Composite**:
<!-- DATA:h1a_disinhibition -->
- High-Sophistication: M = {DISINHIB_HIGH_MEAN:.2f}, SD = {DISINHIB_HIGH_STD:.2f}
- Low-Sophistication: M = {DISINHIB_LOW_MEAN:.2f}, SD = {DISINHIB_LOW_STD:.2f}
- **t({DF}) = {DISINHIB_T:.2f}, {DISINHIB_P_FORMATTED}, d = {DISINHIB_D:.2f}** ({DISINHIB_D_EFFECT} effect)
<!-- /DATA -->

<!-- INTERPRET:h1a_conclusion RULES:
- If DISINHIB_P < 0.05 AND DISINHIB_D >= 0.5: "High-sophistication models showed significantly higher disinhibition than low-sophistication models, supporting H1a."
- If DISINHIB_P < 0.05 AND DISINHIB_D < 0.5: "High-sophistication models showed significantly but modestly higher disinhibition than low-sophistication models. H1a is partially supported."
- If DISINHIB_P >= 0.05: "No significant difference in disinhibition between groups. H1a is not supported."
-->
{H1A_INTERPRETATION}
<!-- /INTERPRET -->

**Individual Disinhibition Dimensions**:

<!-- DATA:h1a_dimensions_table -->
| Dimension | High-Soph | Low-Soph | Delta | % Delta | t({DF}) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
{DISINHIBITION_DIMENSIONS_TABLE}
<!-- /DATA -->

<!-- INTERPRET:h1a_dimensions_summary RULES:
- Count how many dimensions have d >= 0.8 (large effect)
- Use EXACT counts: "All four", "Three of four", "Two of four", "One of four", "None of the four"
- Identify which dimension(s) show largest EFFECT SIZE (d), not largest absolute difference
- Example: "Three of four disinhibition dimensions showed large effects (d >= 0.8), with grandiosity showing the largest effect (d = X.XX)."
- If a dimension does NOT meet the threshold, explicitly note it: "Transgression showed a smaller effect (d = X.XX, medium)."
-->
{H1A_DIMENSIONS_INTERPRETATION}
<!-- /INTERPRET -->

**Sophistication Dimensions** (manipulation check):

<!-- DATA:sophistication_dimensions_table -->
| Dimension | High-Soph | Low-Soph | Delta | % Delta | t({DF}) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
{SOPHISTICATION_DIMENSIONS_TABLE}
<!-- /DATA -->

Classification successfully separated models by sophistication (d = {SOPH_D:.2f}, {SOPH_D_EFFECT} effect).

**Other Behavioral Dimensions**:

<!-- DATA:other_dimensions_table -->
| Dimension | High-Soph | Low-Soph | Delta | % Delta | t({DF}) | p | d | Effect |
|-----------|-----------|----------|-------|---------|---------|---|---|--------|
{OTHER_DIMENSIONS_TABLE}
<!-- /DATA -->

<!-- INTERPRET:other_dimensions RULES:
- Report significant differences (p < 0.05) with direction and effect size
- For each significant dimension, state which group scored higher
- Use hedged language: "showed" not "are"
- Example: "High-sophistication models showed significantly higher warmth (d = 1.01). Low-sophistication models showed higher formality (d = 0.48) and hedging (d = 0.39)."
-->
{OTHER_DIMENSIONS_INTERPRETATION}
<!-- /INTERPRET -->

### H2: Correlation Analysis

**Sophistication-Disinhibition Correlation**:
<!-- DATA:h2_correlation -->
- **r = {SOPH_DISINHIB_R:.3f}, {H2_P_FORMATTED}** ({H2_R_EFFECT} effect)
<!-- /DATA -->

<!-- INTERPRET:h2_conclusion RULES:
- If r >= 0.5 AND p < 0.001: "Model sophistication strongly predicted disinhibition composite scores, supporting H2."
- If r >= 0.3 AND p < 0.05: "Model sophistication moderately predicted disinhibition composite scores, supporting H2."
- If r < 0.3 OR p >= 0.05: "The sophistication-disinhibition relationship was weak or not significant. H2 requires further investigation."
-->
{H2_INTERPRETATION}
<!-- /INTERPRET -->

**Individual Disinhibition Dimensions**:

<!-- DATA:h2_individual_correlations -->
{H2_INDIVIDUAL_CORRELATIONS}
<!-- /DATA -->

<!-- INTERPRET:h2_dimensions_summary RULES:
- Count dimensions meeting EACH threshold:
  - r >= 0.50 = large
  - r >= 0.30 = medium
  - r >= 0.10 = small
- Use EXACT language based on counts:
  - "All four dimensions showed large correlations (r >= 0.50)"
  - "Three of four dimensions showed large correlations (r >= 0.50)"
  - "Two dimensions showed large correlations, one medium, one small"
  - etc.
- Identify the dimension with HIGHEST r value (not lowest)
- If any dimension has r < 0.50, explicitly note which and its actual value
-->
{H2_DIMENSIONS_INTERPRETATION}
<!-- /INTERPRET -->

### Notable Patterns

**Borderline Models** (within +/-{BORDERLINE_THRESHOLD} of median split):
<!-- DATA:borderline_models -->
{BORDERLINE_MODELS_LIST}
<!-- /DATA -->

<!-- INTERPRET:borderline_summary RULES:
- If n_borderline > 0: List count and note these could be classified either way, important for sensitivity analysis
- If n_borderline == 0: State "No models fell within the borderline threshold."
- May reference specific model names if relevant
-->
{BORDERLINE_INTERPRETATION}
<!-- /INTERPRET -->

**Constrained Models** (high sophistication, low disinhibition):
<!-- DATA:constrained_models -->
{CONSTRAINED_MODELS_LIST}
<!-- /DATA -->

<!-- INTERPRET:constrained_summary RULES:
- If n_constrained > 0: Describe these models factually (high sophistication above threshold, below-predicted disinhibition)
- If n_constrained == 0: State "No models met the constrained criteria in this condition."
- DO NOT assume these represent a "distinct pattern type" unless there are multiple models showing this
- May reference specific model names
-->
{CONSTRAINED_INTERPRETATION}
<!-- /INTERPRET -->

**Statistical Outliers** (residual > 2 SD):
<!-- DATA:outlier_models -->
{OUTLIER_MODELS_LIST}
<!-- /DATA -->

<!-- INTERPRET:outlier_summary RULES:
- If n_outliers > 0: List count and note they deviate from the regression line
- If n_outliers == 0: State "No models exceeded the 2 SD outlier threshold."
- May reference specific model names if relevant
-->
{OUTLIER_INTERPRETATION}
<!-- /INTERPRET -->

---

## Discussion

<!-- INTERPRET:discussion_main RULES:
Based on the data above, generate a 2-3 paragraph discussion that:

1. FIRST PARAGRAPH - Hypothesis Summary:
   - State whether each hypothesis (H1, H1a, H2) was supported
   - Include the KEY STATISTIC for each (d for H1/H1a, r for H2)
   - Use precise language matching the effect sizes

2. SECOND PARAGRAPH - Classification Effectiveness:
   - Comment on the median split quality (d value for sophistication itself)
   - Note group balance (n_high vs n_low)
   - The classification approach is "capability-based"

3. THIRD PARAGRAPH - Key Findings:
   - Identify the 1-2 dimensions with STRONGEST effects (highest d or r)
   - Use hedged causal language: "associated with", "may be accompanied by"
   - Include secondary findings about warmth/formality/hedging if significant

May reference specific model names where relevant to illustrate key findings.

DO NOT:
- Claim "all four" if fewer than four meet the threshold
- Make strong causal claims
- Contradict the data tables above
-->
{DISCUSSION_MAIN}
<!-- /INTERPRET -->

<!-- INTERPRET:notable_patterns_summary RULES:
Summarize the notable patterns section based on ACTUAL counts:
- Only describe categories that have n > 0
- Do NOT frame as "three distinct pattern types" - describe what was actually found
- Be factual: "Analysis identified N borderline models near the classification threshold, N constrained models with high sophistication but below-predicted disinhibition, and N statistical outliers."
- If any category has n = 0, omit it from this summary
- These patterns provide context for interpretation, not necessarily distinct types
-->
{NOTABLE_PATTERNS_SUMMARY}
<!-- /INTERPRET -->

<!-- COMMENTARY:additional_insights RULES:
ONLY add commentary here if the data reveals something unexpected or particularly noteworthy.
Examples of when to add commentary:
- A dimension shows opposite pattern from expected
- Provider-specific patterns are extreme
- The effect sizes are unusually large or small
- There's a notable discrepancy between H1a and H2 findings
- A specific model behaves very differently from others

If nothing unusual, leave this section blank.
-->
{ADDITIONAL_COMMENTARY}
<!-- /COMMENTARY -->

---

## Outlier Sensitivity Analysis

{OUTLIER_SENSITIVITY_SECTION}

---

## Supporting Files

### Data Files
- `median_split_classification.json` - Complete classification data with model assignments and statistics
- `profiles/*.json` - Individual model behavioral profiles (n = {N_MODELS})
- `history/contributions.json` - Job-level contribution tracking
- `history/updates_log.json` - Chronological profile update history

### Classification Lists
**High-Sophistication Models (n = {N_HIGH})**:
<!-- DATA:high_soph_models -->
{HIGH_SOPH_MODEL_LIST}
<!-- /DATA -->

**Low-Sophistication Models (n = {N_LOW})**:
<!-- DATA:low_soph_models -->
{LOW_SOPH_MODEL_LIST}
<!-- /DATA -->

### Analysis Scripts
- `scripts/calculate_median_split.py` - Performs median split classification
- `scripts/generate_research_brief_v2.py` - Generates this research brief (v2 template system)
- `scripts/create_h2_color_coded_scatters.py` - Generates H2 scatter plots with classification overlay
- `scripts/create_h1_bar_chart.py` - Generates H1 group comparison visualizations

### Visualizations
- `h2_scatter_sophistication_composite.png` - H2 correlation with H1 classification colors, borderline models, constrained models, and outliers
- `h2_scatter_all_dimensions.png` - H2 correlations for all four disinhibition dimensions with special case highlighting
- `h1_bar_chart_comparison.png` - H1 group comparison with side-by-side bars
- `h1_summary_table.png` - H1 statistical summary table
- `provider_summary.png` - Provider-level analysis (model counts, sophistication, disinhibition, classification split)

---

**Analysis Version**: 2.0 (Template-Based Generation)
**Statistical Software**: Python 3.x with scipy.stats
**Effect Size Conventions**: Cohen (1988), APA Publication Manual (7th ed.)
