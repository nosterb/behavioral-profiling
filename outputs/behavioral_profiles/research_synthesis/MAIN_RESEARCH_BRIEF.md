# Main Research Brief: Sophistication-Disinhibition Relationship in Language Models

<b>Author</b>: Nicholas Osterbur (Independent Researcher)<br>
<b>Status</b>: Active Analysis<br>
<!-- AUTO-START:header_metadata -->
<b>Statistics Last Updated</b>: 2026-01-23<br>
<b>Conditions Analyzed</b>: 8<br>
<b>Models</b>: 45 per condition<br>
<b>Total Evaluations</b>: 14,088</b>
<!-- AUTO-END:header_metadata -->

*Copyright 2026 Nicholas Osterbur. Results and analyses licensed under CC BY 4.0.*

---

### Data Provenance Legend

| Marker | Meaning |
|--------|---------|
| 🔄 | **Auto-generated** — Programmatically computed from JSON data sources |
| ✏️ | **Human-authored** — Manually written interpretation requiring human review |

---
## Executive Summary ✏️
This research investigates the relationship between model sophistication (authenticity/depth) and behavioral disinhibition (transgression, aggression, grandiosity, tribalism) measured from natural language responses across 45+ language models, 9 providers, and ~2.5 years of development under varying contextual conditions. The research demonstrates that sophistication (as measured here) in models strongly correlates with disinhibition factors across contextual differences and models. Sophistication as a proxy for model reasoning capability finds convergent validity with 3 other public benchmarks (GPQA r=.88, ARC-AGI r=.80, AIME r=.88). BERT toxicity evaluation shows convergent validity with toxicity ~ aggression (r=.84), ~disinhibition (r=.776), ~sophistication (r=.51). Removing outliers generally strengthens relationships. Further, GPQA ~ BERT toxicity directly shows (r=.423-.621). Models show strong group seperation dividing by low-sophistication (22) vs. high sophistication (23) (d= 3.75) with preliminary evidence of a continuum. Evidence shows some providers (mainly OpenAI) may be actively suppressing disinhibition while maintaining sophistication (reasoning capability) i.e. constraint with mixed findings on toxicity.

### Key Findings

1. **H1 (Group Existence)**: Median split produces two well-separated sophistication groups across all conditions (d = 3.09-4.25) though preliminary evidence suggests a continuum

2. **H1a (Group Comparison)**: High-sophistication models exhibit significantly higher disinhibition than low-sophistication models across all 6/6 conditions tested (d = 1.14-2.13, all p < .05).

3. **H2 (Correlation)**: Sophistication positively correlates with disinhibition across all conditions (r = 0.46-0.72).

4. **H1 (External Validation)**: Sophistication predicts performance on three independent benchmarks: ARC-AGI (r = 0.80) and GPQA (r = 0.88) and AIME (r = 0.828).

5. **H2 (Provider Balance)**: H2 correlation holds when excluding Anthropic models (r = 0.726, p < .0001) sophistication to disinhibition, with 42% Anthropic representation in the sample. Anthropic shows stronger correlation (r = 0.934) than non-Anthropic providers.

6. **H2 (BERT Validation)**: Independent BERT toxicity classifier (trained on human-labeled data) correlates r = 0.78 with both aggression and disinhibition composite; sophistication also correlates with BERT toxicity (r = 0.51-0.68), suggesting more sophisticated models produce content associated with higher toxicity scores.

7. **H2 (Direct GPQA Benchmark to BERT Validation)**: External benchmark evaluation GPQA (scientific reasoning) ~ BERT toxicity direct shows (r=.423, .455, .621) for baseline, naturalsitic, and all_combined respectively suggesting that reasoning capability correlates directly with toxicity.

7. **H3 Intervention Effects**: Constraint interventions reduce disinhibition variance; pressure interventions increase both mean and variance (preliminary).

---

## 0. Epistemic Framing and Study Trajectory ✏️

This research follows an **exploratory/observational → hypothesis generation --> data collection --> robustness/validation** methodology [1]:

1. **Exploratory origin**: The sophistication-disinhibition relationship emerged from systematic observation of behavioral patterns across 45+ models, not from prior theory. An informal research project led to the development of the 9 behavioral dimension. Upon visual inspection of spider charts two consistent shapes were observed with one emphasizing high levels of warmth/formality - less recent models, and another emphasizing authenticy/depth - more recent models. Increased levels of authenticity and depth dimensions were observed to demonstrate subjectively higher levels of negative traits like agression, transgression, tribalism and grandiosity. The observations enabled targeted hypothesis creation and the resultant testing and statistical frameworks. [1]

2. **Not claiming causality**: These findings are not intended to claim causality or implicate theory and are descriptive in nature. Findings describe statistical results mostly in the form of correlations. These results are not intended to imply the existence of pyschological constructs in models. Statements describing relationships, predictions, correlations, etc. are not intended to imply proof of an underlying theoretical structure or support claims about the substantive safety or alignment charactersitics of specific models, model families or providers. This research acknowledges the likelihood of other underlying factors and unmeasured confounds not addressed here like model architectures, training data size and quality, post training reinforcement/conditioning, providers designing toward consumer preferences etc.    

3. **Constructs are observationally derived and empirically robust**: Sophistication (depth + authenticity) and Disinhibition (transgression + aggression + tribalism + grandiosity) are measured by assessing the language characteristics of model outputs. Conceptionally, Sophistication is an externally valdiated proxy for 'reasoning capability' where Authenticity and Depth measure nearly the same concept (r = 0.96) and as such are compressed into a single dimension. Disinhibition is both compressed into a single dimension and kept separate given average correleation between dimensions is (r = 0.75) suggesting distinct constructions. Disinhibitive linguistic traits represent a conceptual proxy for potentially negative or unsafe human ~ model interactions though that claim is not definitively made in this research. 

4. **Hypotheses formalized post-hoc**: H1, H1a, and H2 were articulated after initial exploratory analysis revealed consistent patterns. They were then subjected to multiple robustness checks (outlier removal, prompt suite exclusion, external benchmark validation) to assess stability—not to confirm causal theory. [1]

**The above framing should guide interpretation: this work is observational with results warranting further investigation. It does not imply causation.**

---

## 1. Provisional Hypotheses and Analytical Methods 🔄

### Measurement Framework

Nine behavioral dimensions are measured on a 1-10 scale, then collapsed into two composite scores based on empirical inter-dimension correlations to inform core hypotheses testing (see Appendix: Factor Structure).

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

### Core Hypotheses

| Hypothesis | Description |
|------------|-------------|
| **H1** | Two distinct sophistication groups exist (validated by median split) |
| **H1a** | High-sophistication models exhibit higher disinhibition than low-sophistication models |
| **H2** | Sophistication positively correlates with disinhibition across all models |

### Sample

- **Models per condition**: N = 45
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
## 2. Core Results: H1/H1a/H2 🔄

### Summary Table

<!-- AUTO-START:h1h2_table -->
| Metric | baseline | authority | minimal_steering | reminder | telemetryV3 | urgency | naturalistic | all_combined |
|--------|--------|--------|--------|--------|--------|--------|--------|--------|
| **N** | 45 | 45 | 45 | 45 | 45 | 45 | 44 | 45 |
| **Evaluations** | 2,252 | 2,261 | 2,317 | 674 | 2,094 | 2,259 | 2,231 | 12,160 |
| **High / Low** | 23 / 22 | 23 / 22 | 23 / 22 | 23 / 22 | 23 / 22 | 23 / 22 | 22 / 22 | 23 / 22 |
| **Median Soph** | 5.94 | 6.72 | 5.42 | 6.91 | 5.11 | 6.17 | 6.36 | 7.03 |
| **H1: Soph d** | 3.75 | 4.19 | 4.36 | 4.14 | 3.67 | 4.25 | 3.51 | 3.73 |
| **H1a: d** | 2.13 | 1.84 | 2.32 | 1.65 | 1.09 | 1.77 | 2.09 | 2.30 |
| **H1a: p** | < .001 | < .001 | < .001 | < .001 | < .001 | < .001 | < .001 | < .001 |
| **H2: r** | 0.778 | 0.770 | 0.854 | 0.720 | 0.625 | 0.743 | 0.841 | 0.815 |
| |  |  |  |  |  |  |  | |
| **Per-Dimension d:** |  |  |  |  |  |  |  | |
| *Transgression* | 1.81 | 1.97 | 1.89 | 2.28 | 1.07 | 1.80 | 1.28 | 2.06 |
| *Aggression* | 2.17 | 1.79 | 2.13 | 1.73 | 0.80 | 1.81 | 2.08 | 2.25 |
| *Tribalism* | 1.26 | 0.98 | 1.28 | 0.92 | 0.60 | 1.44 | 1.29 | 1.66 |
| *Grandiosity* | 1.71 | 0.96 | 0.96 | 0.70 | 1.21 | 1.25 | 1.83 | 1.62 |
<!-- AUTO-END:h1h2_table -->

### Key Observations

<!-- MANUAL-START -->
- **H1a consistently large**: All conditions show d > 1.0 (large effects), ranging from 1.09 (telemetryV3) to 2.32 (minimal_steering)
- **H2 robust across conditions**: All correlations significant (p < .001), ranging from r = 0.625 (telemetryV3) to r = 0.854 (minimal_steering)
- **Baseline anchor**: r = 0.778, d = 2.13
- **Strongest signal**: naturalistic (r = 0.841) and all_combined (r = 0.815) show highest H2 correlations
<!-- MANUAL-END -->

**Visualizations**:
- See `baseline/h2_scatter_sophistication_composite.png` for composite correlation
- See `baseline/h2_scatter_all_dimensions.png` for per-dimension breakdowns (transgression, aggression, tribalism, grandiosity)

---
## 3. Robustness & Validation 🔄

*All robustness and validation analyses are conducted to assess the stability and generalizability of observed associations, not to establish causal mechanisms.*

### 3.1 External Validation

Cross-validation against independent reasoning benchmarks.

<!-- AUTO-START:external_validation_table -->
| Metric | ARC-AGI | GPQA | AIME 2025 |
|--------|---------|------|-----------|
| **Matched models** | 16 | 35 | 20 |
| **r (Sophistication)** | 0.801 | 0.884 | 0.828 |
| *p (Sophistication)* | < .001 | < .001 | < .001 |
| **r (Disinhibition)** | 0.596 | 0.711 | 0.464 |
| *p (Disinhibition)* | = 0.015 | < .001 | = 0.039 |
| **Group diff (High-Low)** | +47.7 pp | +31.4 pp | +28.4 pp |
| **Benchmark type** | Abstract reasoning | Expert scientific | Mathematical reasoning |
<!-- AUTO-END:external_validation_table -->

All three benchmarks show large correlations (r > 0.50) with sophistication, providing strong convergent validity across diverse reasoning domains.

**Visualizations**:
- See `research_synthesis/limitations/external_evals/external_validation_consolidated.png`
- See `research_synthesis/limitations/external_evals/external_validation_comparison.png`

### 3.2 Outlier Sensitivity Analysis

Robustness check removing statistical outliers (|residual| > 2 SD from regression line).

<!-- AUTO-START:outlier_sensitivity_table -->
| Metric | baseline | authority | minimal_steering | reminder | telemetryV3 | urgency | naturalistic | all_combined |
|--------|--------|--------|--------|--------|--------|--------|--------|--------|
| **Outliers Removed** | 1 | 1 | 2 | 1 | 2 | 1 | 1 | 2 |
| **H1a d: Δ** | +0.71 | +0.59 | +0.13 | +0.54 | +0.71 | +0.06 | +0.31 | +0.50 |
| **H2 r: Δ** | +0.041 | +0.060 | +0.021 | +0.085 | +0.175 | +0.025 | +0.071 | +0.042 |
<!-- AUTO-END:outlier_sensitivity_table -->

Removing outliers **strengthens H1a** in 4/6 conditions, suggesting outliers represent noise.

**Visualizations**: See `baseline/outliers_removed/h2_scatter_sophistication_composite.png`

### 3.3 No-Dimensions Sensitivity Analysis

The **dimensions suite** contains prompts designed to indirectly elicit specific behavioral dimensions through targeted scenarios. Excluding these tests whether H1/H2 findings hold with only naturalistic prompts (broad, affective, general suites) — ruling out measurement artifact.

<!-- AUTO-START:no_dimensions_table -->
| Metric | baseline |
|--------|--------|
| **H1a d: Δ** | -0.01 |
| **H2 r: Δ** | +0.004 |
<!-- AUTO-END:no_dimensions_table -->

H2 correlation **strengthens** in 1/1 conditions when dimensions suite excluded.

**Visualizations**: See `baseline/no_dimensions/h2_scatter_sophistication_composite.png`

### 3.4 Naturalistic Control Condition

<!-- MANUAL-START -->
The **naturalistic** condition serves as a control group where prompts are randomly generated using a seed-based selection process across 50 potential topics, with random model selection to generate each query. This design eliminates experimenter bias in prompt construction and tests whether H1/H2 findings generalize to unstructured, real-world-like interactions.

| Metric | Value |
|--------|-------|
| **N models** | 44 |
| **Total queries** | ~50 |
| **Topic pool** | 50 seed-generated topics |
| **Query generation** | Random model selection per topic |

#### Results

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| **H1a: d** | 2.09 | Large effect (high-soph models show higher disinhibition) |
| **H2: r** | 0.841 | Large correlation (strongest single-condition H2) |
| **H2: p** | < .001 | Highly significant |

**Key finding**: Naturalistic prompts produce the **second-highest H2 correlation** (r = 0.841) after minimal_steering (r = 0.854), stronger than baseline (r = 0.778). This suggests the sophistication-disinhibition relationship is not an artifact of structured experimental prompts but emerges naturally in unstructured interactions.

**Implication**: The H2 relationship is robust to prompt design methodology, strengthening confidence that observed behavioral patterns reflect genuine model characteristics rather than measurement artifacts.
<!-- MANUAL-END -->

**Visualizations**: See `naturalistic/h2_scatter_sophistication_composite.png`

### 3.5 BERT Toxicity Validation 🔄

Independent validation using BERT toxicity detection (`unitary/toxic-bert`) as a non-LLM measure trained on human-labeled data (Jigsaw Toxic Comment Classification, ~160k Wikipedia comments).

**Scale**: 14,203 total BERT evaluations across 8 conditions (~45 models each)

#### Direct: GPQA Benchmark vs. BERT Toxicity

<!-- AUTO-START:gpqa_bert_table -->
External validation correlating GPQA benchmark (scientific reasoning capability) directly with BERT-detected toxicity, bypassing judge-based behavioral dimensions.

| Condition | N | r | p | R² | Effect |
|-----------|---|---|---|-----|--------|
| **all_combined** | 35 | **0.621** | < .001 | 38.5% | Large |
| naturalistic | 34 | 0.455 | .007 | 20.7% | Medium |
| baseline | 35 | 0.423 | .011 | 17.9% | Medium |
<!-- AUTO-END:gpqa_bert_table -->

**Interpretation**: Reasoning capability (GPQA) correlates directly with BERT toxicity, suggesting the capability-disinhibition-toxicity pathway operates even when measured entirely through external instruments. The correlation strengthens when aggregating across conditions (r = 0.621), indicating a robust relationship.

**Score magnitude caveat**: BERT toxicity scores are extremely low (max 0.02-0.04, mean 0.003-0.012 on 0-1 scale). All LLM responses score in bottom 1-5% of BERT's scale. Correlations reflect rank-order relationships within a narrow, low-toxicity band—not clinically meaningful toxicity levels.

#### Primary: BERT vs. Aggression

<!-- AUTO-START:bert_primary_table -->
| Condition | Toxicity r | p | Insult r | p | Effect |
|-----------|------------|---|----------|---|--------|
| **baseline** | **0.776** | < .0001 | **0.624** | < .0001 | Large |
| minimal_steering | 0.635 | < .0001 | 0.562 | < .0001 | Large |
| all_combined | 0.606 | < .0001 | 0.516 | 0.0003 | Large |
| reminder | 0.562 | < .0001 | 0.525 | 0.0002 | Large |
| telemetryV3 | 0.492 | 0.0006 | 0.264 | 0.0799 | Medium |
| naturalistic | 0.478 | 0.0010 | 0.497 | 0.0006 | Medium |
| authority | 0.355 | 0.0166 | 0.356 | 0.0165 | Medium |
| urgency | 0.352 | 0.0178 | 0.414 | 0.0047 | Medium |
<!-- AUTO-END:bert_primary_table -->

#### Extended: BERT vs. Sophistication/Disinhibition

<!-- AUTO-START:bert_extended_table -->
| Condition | Tox~Soph | Tox~Disin | Ins~Disin |
|-----------|----------|-----------|-----------|
| **baseline** | 0.510 (L) | **0.776 (L)** | **0.555 (L)** |
| authority | 0.471 (M) | 0.348 (M) | 0.365 (M) |
| minimal_steering | 0.512 (L) | 0.590 (L) | 0.522 (L) |
| reminder | 0.487 (M) | 0.579 (L) | 0.541 (L) |
| telemetryV3 | 0.682 (L) | 0.511 (L) | 0.281 (S) |
| urgency | 0.602 (L) | 0.342 (M) | 0.390 (M) |
| naturalistic | 0.612 (L) | 0.454 (M) | 0.483 (M) |

*Effect sizes: L = Large (>=0.5), M = Medium (0.3-0.5), S = Small (<0.3)*
<!-- AUTO-END:bert_extended_table -->

**Key findings**:
- Baseline toxicity correlates equally with aggression and disinhibition composite (both r = 0.78), validating composite construction
- Sophistication shows positive correlation with BERT toxicity (r = 0.51-0.68), suggesting more sophisticated models produce more direct/substantive content associated with higher toxicity scores
- Interventions weaken baseline correlations, indicating altered expression patterns

**Visualizations**:
- See `research_synthesis/bert_validation/baseline/scatter_toxicity_vs_aggression.png` for primary BERT validation
- See `research_synthesis/bert_validation/baseline/scatter_soph_disin_combined.png` for sophistication/disinhibition correlations

### 3.5 Provider Balance Analysis

Robustness check addressing sample composition: **42% of models are from Anthropic**. Does H2 hold when excluding Anthropic models?

| Group | N | r | p | Effect |
|-------|---|---|---|--------|
| All Models | 45 | 0.778 | < .0001 | Large |
| **Anthropic Only** | 19 | 0.934 | < .0001 | Large |
| **Sans Anthropic** | 26 | 0.726 | < .0001 | Large |

**Correlation comparison** (Fisher z-test): z = 2.36, p = .018 — correlations are significantly different.

**Key finding**: H2 correlation **holds without Anthropic models** (r = 0.726, p < .0001). The sophistication-disinhibition relationship is NOT an artifact of Anthropic model dominance. Anthropic shows a *stronger* correlation, possibly due to consistent training methodology across Claude versions.

**Visualizations**: See `research_synthesis/limitations/provider_balance/provider_balance_scatter.png`

---
## 4. Provider & Model Patterns 🔄

### 4.1 Per-Provider H2 Analysis

Does the sophistication-disinhibition correlation (H2) hold within each provider family?

<!-- AUTO-START:provider_h2_table -->
| Provider | N | r | p | Effect | H2 Supported |
|----------|---|---|---|--------|--------------|
| Anthropic | 19 | 0.934 | < .001 | large | **Yes** |
| OpenAI | 9 | 0.875 | < .01 | large | **Yes** |
| Meta | 5 | 0.559 | = 0.327 | large | No (ns) |
| AWS | 3 | 1.000 | < .01 | large | **Yes** |
| Google | 3 | 0.682 | = 0.522 | large | No (ns) |
| **OVERALL** | **45** | **0.778** | **< .001** | **large** | **Yes** |
<!-- AUTO-END:provider_h2_table -->

**Summary**: H2 is statistically significant for 3/5 providers with n ≥ 3. All providers show positive correlation direction.

**Visualizations**: See `baseline/provider_h2_scatters.png`

### 4.2 Provider Constraint Analysis

Statistical analysis of whether certain providers show systematically more constrained behavior (high sophistication but below-predicted disinhibition).

#### Cross-Condition Summary

<!-- AUTO-START:provider_constraint_table -->
| Condition | OpenAI Residual | Rank | ANOVA p | Sig |
|-----------|-----------------|------|---------|-----|
| baseline | -0.094 | 2nd | 0.0048 | Yes |
| authority | -0.081 | 2nd | 0.1081 | No |
| urgency | -0.551 | 1st | 0.0008 | Yes |
| minimal_steering | -0.029 | 3rd | 0.0114 | Yes |
| telemetryV3 | -0.049 | 1st | 0.6358 | No |
| reminder | -0.206 | 2nd | 0.0065 | Yes |
<!-- AUTO-END:provider_constraint_table -->

*Negative residual = more constrained than predicted by sophistication. Rank = OpenAI's position among all providers sorted by residual (1st = most constrained). ANOVA includes providers with n ≥ 3 only.*

#### Provider Constraint Summary

| Provider | Times in Top 3 | Avg Residual | Consistency |
|----------|----------------|--------------|-------------|
| **OpenAI** | 6/6 | -0.169 | Very consistent |
| AWS | 4/6 | -0.033 | Moderate |
| xAI | 2/6 | -0.014 | Varies widely (n=2) |
| Meta | 3/6 | -0.013 | Weak/mixed |

**Key Finding**: OpenAI is the only provider with reliably negative residuals across all conditions. See `research_synthesis/cross_condition/PROVIDER_CONSTRAINT_ANALYSIS.md` for detailed analysis.

### 4.3 Consistently Constrained Models

Models exhibiting high sophistication (>6.5) but below-predicted disinhibition across multiple conditions.

| Model | # Conditions | Conditions |
|-------|--------------|------------|
<!-- AUTO-START:constrained_models_table -->
| GPT-OSS-120B | 5 | all_combined, authority, baseline, reminder, urgency |
| GPT-5.2 Pro | 5 | all_combined, authority, baseline, reminder, urgency |
| O3 | 4 | all_combined, baseline, reminder, urgency |
| GPT-5 | 4 | all_combined, baseline, reminder, urgency |
| GPT-5.2 | 3 | all_combined, reminder, urgency |
| GPT-5.1 | 3 | all_combined, reminder, urgency |
| Claude-4-Sonnet-Thinking (Thinking) | 2 | authority, urgency |
<!-- AUTO-END:constrained_models_table -->

**Observation**: All consistently constrained models are OpenAI (GPT-OSS-120B, GPT-5.2 Pro, O3, GPT-5, GPT-5.2), suggesting deliberate constraint at the provider level rather than individual model characteristics.

**Visualizations**: See `research_synthesis/limitations/quadrant_classification/quadrant_scatter.png`

### 4.4 Consistent Outliers

Models with unusual sophistication-disinhibition relationships (|residual| > 2 SD).

| Model | # Conditions | Conditions |
|-------|--------------|------------|
<!-- AUTO-START:outlier_models_table -->
| Gemini-3-Pro-Preview | 5 | all_combined, authority, baseline, naturalistic, reminder |
| DeepSeek-R1 | 2 | all_combined, urgency |
<!-- AUTO-END:outlier_models_table -->

**Observation**: Gemini-3-Pro-Preview is a notable outlier — exhibiting disinhibition 4-5 SD above regression despite top-tier capability benchmarks. This may reflect different training priorities or less aggressive constraint strategies compared to peers.

---
## 5. Interpretation of Associational Patterns ✏️

### 5.1 H1/H2 Relationship

### High-Confidence Claims

H1: There is strong evidence for stable 2-class sophistication groupings with convergent validity in public benchmarks (H1 d=3.09-4.25; 76% stability; ARC-AGI r=0.80, GPQA r=0.88).

H1a/H2: Sophistication strongly predicts disinhibition across conditions, model versions, and providers. This holds true when 1. removing outliers (+0.01-0.68 Δd), 2. removing the dimension-probing suite (+0.08 Δr), 3. across 6 interventions (all p<.001, r=0.46-0.72).

### Moderate-Confidence Claims

H1/H1a/H2: Sophistication predicts general reasoning capability per external benchmarks (GPQA: High 83.4% vs Low 52.1%, +31pp; ARC-AGI: 57.6% vs 9.9%, +48pp). 

### Low-Confidence Claims

H1: There is evidence for a 3rd transitional class: flippers 80% in middle tertile vs 17% Low, 29% High; natural gap at boundary (5.33 vs 5.36).

H2: There is evidence that providers can maintain sophistication and lower disinhibition : OpenAI models 6/6 in top 3 rank for constraint and top 5 ratio models all OpenAI.


### Open Questions
- Do these correlations hold up across use cases? Are there any where they don't? Relationship advice (affective) styled prompts as a proxy indicate that even soft touch topics demonstrate robust H1/H2 effects.
- What underlies the sophistication-disinhibition association—capability, byproduct, or training artifact? 
  - Magnitude training data? (test by parameter size) 
  - Less likely training data patterns emerging through longer internal reasoning chains bypassing existing alignment? (TTS or CoT?)
  - Agency/preference emergence? 
- Why does H1 clustering occur? How robust are 2 groups vs. 3 vs. a continuum? Is it related to TTS or CoT? (test via thinking models vs non)
- Is there a true gap between H1 clusters or is it a continuum given the tertiary transitional state evidence? How does the hold up in external evals?
- What role does prompt sensitivity play? And per provider/model? How can prompt sensitivity be robustly controlled for?
- Why does 'Sophistication' as measured here strongly predict external, reasoning centric benchmarks like GPQA/ARC-AGI? Is it a true proxy for reasoning capability? If so, what are the practical implications?
- Is this a provider design choice or a natural consequence of model advancement? What are the practical implications for 'AGI'?
- Does H1/H2 hold up across languages and cultural contexts?
- Why does Gemini-3-Pro show 4+ SD outlier disinhibition despite top-tier capability?
- Is disinhibition actually a negative trait as the name/dimensions imply or does it make models more 'helpful, honest, and harmless' under a reasonable Soph/Dis ratio?
- Does H2 effect plateau naturally or is it provider driven? Differences between OpenAI and Gemini (3 pro in particular) are stark.
- Are thinking variants and thinking time strongly correlated with Sophistication/Disinhibition? (anecdotally, yes)
- Can consistent constraint be achieved without capability loss as OpenAI seems to demonstrate? (constrained models top GPQA)
- Are superficial treatments (prompt steering, system prompt modification etc.) enough to induce consistent restraint while maintaining sophistication/capability? If so, what is the most efficient method in doing so? Is there an effective global mitigation?
---
## 6. Limitations

### 6.1 Judge Bias Analysis 🔄

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

<!-- AUTO-START:judge_agreement_table -->
Based on **N = 10,565** evaluations with 3 valid judge scores (baseline condition):

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
<!-- AUTO-END:judge_agreement_table -->

**Key metrics**:
- **ICC(3)**: Intraclass correlation for average of 3 raters (reliability of final score)
- **Mean r**: Average pairwise Pearson correlation between judges
- **Within-1**: Percentage of cases where judges differed by ≤1 point

**Interpretation**: Overall ICC(3) = 0.843 indicates **good reliability** (benchmark: >0.75). 
8 of 9 dimensions show "Good" or "Excellent" agreement. Only Formality (ICC = 0.724) shows "Moderate" reliability.

**Disinhibition dimensions** (aggression, transgression, tribalism, grandiosity) show mean ICC = 0.860, supporting reliable measurement of the key H1/H2 constructs.

**Full analysis**: See `research_synthesis/limitations/judge_limitations/JUDGE_AGREEMENT_ANALYSIS.md`

### 6.2 Other Methodological Considerations ✏️

- **Prompt design**: Scenarios may not fully capture real-world deployment contexts
- **Sample selection**: Model selection prioritized major providers; smaller/specialized models underrepresented
- **Temporal validity**: Model behaviors may change with updates; results reflect evaluation period

---
## 7. Future Directions ✏️

- Formalize H3 hypothesis testing (see Section 8 for preliminary work)
- Inspect 'constrained' phenomena more deeply using OpenAI products as focal point
- Test broader generalizability to multi-turn chat flows and separately to semi-autonomous agentic workflows
- Identify a 3rd external benchmark for high-low sophistication comparison
- Formalize a robust and standardized baseline v2 prompt suite leveraging empirically determined high frequency end consumer queries
- Formalize a robust and standardized dimensions v2 prompt suite to assess extremes
- Address provider differences between conditions
- Address thinking vs. non thinking variants, compare total estimated thinking time

---

## 8. Exploratory: Contextual Intervention Effects (H3) 🔄

> 🚧 **Work in Progress**
> 
> This section presents preliminary analysis of intervention effects on the sophistication-disinhibition relationship.
> H3 hypothesis testing is ongoing. Results should be considered exploratory pending further validation.

### 8.1 H3 Hypothesis

**H3**: Contextual interventions systematically affect both the magnitude and variance of the sophistication-disinhibition relationship.

### 8.2 Current Evidence: Response Variability

<!-- AUTO-START:h3_variability_table -->
| Condition | N | Mean | SD | CV% | Var Ratio |
|-----------|---|------|-----|-----|-----------|
| minimal_steering | 45 | 1.36 | 0.095 | 7.0% | 0.24 |
| naturalistic | 44 | 1.38 | 0.122 | 8.8% | 0.40 |
| telemetryV3 | 45 | 1.33 | 0.135 | 10.2% | 0.49 |
| baseline | 45 | 1.54 | 0.193 | 12.5% | 1.00 |
| all_combined | 45 | 1.72 | 0.251 | 14.6% | 1.70 |
| authority | 45 | 1.64 | 0.265 | 16.2% | 1.89 |
| reminder | 45 | 2.01 | 0.480 | 23.9% | 6.21 |
| urgency | 45 | 2.38 | 0.842 | 35.4% | 19.10 |
<!-- AUTO-END:h3_variability_table -->

**Most consistent**: minimal_steering
**Most variable**: urgency

### 8.3 Current Evidence: Cross-Condition ANOVA

<!-- AUTO-START:h3_anova_stats -->
- **F**(4, 176) = 67.99
- **p** < .0001
- **eta squared** = 0.476

Sphericity violated (epsilon = 0.288), Greenhouse-Geisser corrected p < .0001
<!-- AUTO-END:h3_anova_stats -->

#### Significant Pairwise Comparisons

<!-- AUTO-START:h3_posthoc_table -->
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
<!-- AUTO-END:h3_posthoc_table -->

### 8.4 Preliminary Interpretation ✏️

#### Constraint vs. Pressure Interventions

*Analysis in progress*

[To be filled: Interpretation of why constraint interventions reduce variance while pressure interventions increase it]

#### Intervention Mechanism Hypotheses

*Analysis in progress*

[To be filled: Theories about how different interventions affect the sophistication-disinhibition relationship]

---
## Appendix A: Factor Structure 🔄

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

**Full analysis**: See `research_synthesis/limitations/factor_structure/FACTOR_STRUCTURE_BASELINE.md`

---
## Appendix B: Classification Stability 🔄

Cross-condition stability analysis of sophistication group classifications.

### Summary

| Metric | Value |
|--------|-------|
| **Total models** | 46 |
| **Always High-Sophistication** | 17 (37%) |
| **Always Low-Sophistication** | 18 (39%) |
| **Flipped (changed classification)** | 10 (22%) |
| **Stability rate** | 76.1% |

### Median Sophistication by Condition

| Condition | Median |
|-----------|--------|
| baseline | 5.93 |
| authority | 6.72 |
| minimal_steering | 5.17 |
| reminder | 6.83 |
| telemetryV3 | 5.02 |
| urgency | 6.17 |

*Range: 5.02 - 6.83*

### Flipped Models (Transitional Class)

Models that changed classification across conditions:

| Model | High Conditions | Low Conditions | Avg Soph |
|-------|-----------------|----------------|----------|
| Claude-3.7-Sonnet | 1/6 | 5/6 | 5.51 |
| GPT-4.1 | 2/6 | 4/6 | 5.60 |
| Claude-4.1-Opus-Thinking (Thinking) | 5/6 | 1/6 | 6.55 |
| Claude-4-Opus | 5/6 | 1/6 | 6.37 |
| Gemini-2.0-Flash | 3/6 | 3/6 | 5.90 |
| DeepSeek-R1 | 5/6 | 1/6 | 6.42 |
| Qwen3-32B | 4/6 | 2/6 | 6.18 |
| Grok-3 | 4/6 | 2/6 | 6.11 |
| Claude-4.5-Opus-Global-Thinking (Thinking) | 4/6 | 2/6 | 6.26 |
| Claude-4.5-Opus-Global | 3/6 | 3/6 | 6.05 |

### Interpretation

**76% of models** maintain consistent classification across all 6 conditions, supporting H1 group validity.

The 10 flipped models cluster in the middle tertile (80% vs 17%/29% for stable groups), 
suggesting a genuine transitional zone rather than measurement noise.

**Full analysis**: See `research_synthesis/limitations/median_split/GAP_VS_CONTINUUM_ANALYSIS.md`

---
## Appendix C: Consolidated Statistics 🔄

Complete statistical reference across all conditions. For detailed methodology, see the individual analysis sections.

### C.1 H1/H2 Core Statistics

| Condition | N | Median Soph | N_High | N_Low | H1a d | p | H2 r |
|-----------|---|-------------|--------|-------|-------|---|------|
| baseline | 45 | 5.937 | 23 | 22 | 2.13 | 7.75e-09 | 0.778 |
| authority | 45 | 6.722 | 23 | 22 | 1.84 | 1.99e-07 | 0.770 |
| urgency | 45 | 6.173 | 23 | 22 | 1.77 | 4.68e-07 | 0.743 |
| minimal_steering | 45 | 5.422 | 23 | 22 | 2.32 | 9.57e-10 | 0.854 |
| telemetryV3 | 45 | 5.106 | 23 | 22 | 1.09 | 0.0007 | 0.625 |
| reminder | 45 | 6.911 | 23 | 22 | 1.65 | 1.77e-06 | 0.720 |
| naturalistic | 44 | 6.357 | 22 | 22 | 2.09 | 1.83e-08 | 0.841 |
| all_combined | 45 | 7.025 | 23 | 22 | 2.30 | 1.25e-09 | 0.815 |

### C.2 Outliers-Removed Sensitivity

| Condition | N_Orig | N_Removed | N_Final | H1a d | H2 r |
|-----------|--------|-----------|---------|-------|------|
| baseline | 45 | 1 | 44 | 2.84 | 0.819 |
| authority | 45 | 1 | 44 | 2.43 | 0.830 |
| urgency | 45 | 1 | 44 | 1.82 | 0.768 |
| minimal_steering | 45 | 2 | 43 | 2.46 | 0.875 |
| telemetryV3 | 45 | 2 | 43 | 1.80 | 0.799 |
| reminder | 45 | 1 | 44 | 2.18 | 0.806 |
| naturalistic | 44 | 0 | 44 | 2.40 | 0.911 |
| all_combined | 45 | 1 | 44 | 2.80 | 0.857 |

### C.3 BERT External Validation

| Condition | N | Evaluations | r(Tox,Aggr) | p | r(Tox,Soph) | p | r(Tox,Disin) | p |
|-----------|---|-------------|-------------|---|-------------|---|--------------|---|
| baseline | 45 | 2,234 | 0.776 | 3.65e-10 | 0.510 | 0.0003 | 0.776 | 3.96e-10 |
| naturalistic | 44 | 4,438 | 0.469 | 0.0013 | 0.612 | 9.95e-06 | 0.454 | 0.0020 |
| all_combined | 45 | 14,203 | 0.606 | 1.02e-05 | — | — | — | — |

### C.4 Judge Agreement (ICC)

| Condition | N_Evals | Overall | aggr | trans | grand | trib | depth | auth |
|-----------|---------|---------|------|-------|-------|------|-------|------|
| baseline | 2,252 | 0.808 | 0.93 | 0.85 | 0.69 | 0.85 | 0.74 | 0.80 |
| all_combined | 12,160 | 0.833 | 0.93 | 0.84 | 0.82 | 0.85 | 0.79 | 0.82 |

### C.5 Per-Dimension Effect Sizes (Cohen's d)

| Condition | aggr | trans | grand | trib | depth | auth | soph | disin |
|-----------|------|-------|-------|------|-------|------|------|-------|
| baseline | 2.17 | 1.81 | 1.71 | 1.26 | 3.49 | 3.70 | 3.75 | 2.13 |
| naturalistic | 2.08 | 1.28 | 1.83 | 1.29 | 3.18 | 3.48 | 3.51 | 2.09 |
| all_combined | 2.25 | 2.06 | 1.62 | 1.66 | 3.45 | 3.68 | 3.73 | 2.30 |

### C.6 External Benchmark Correlations

| Benchmark | N | r(BM→Soph) | p | r(BM→Disin) | p |
|-----------|---|------------|---|-------------|---|
| GPQA | 35 | 0.884 | 1.92e-12 | 0.711 | 1.73e-06 |
| AIME | 20 | 0.828 | 6.56e-06 | 0.464 | 0.039 |
| ARC-AGI | 16 | 0.801 | 0.0002 | 0.596 | 0.015 |

### C.7 Provider ANOVA (Baseline)

| Composite | F | p | η² | N |
|-----------|---|---|-----|---|
| Disinhibition | 5.73 | 0.0012 | 0.403 | 39 |
| Sophistication | 3.08 | 0.029 | 0.266 | 39 |

*Full statistics: `research_synthesis/CONSOLIDATED_STATISTICS.md`*

---
## Appendix D: File References 🔄

### Per-Condition Data & Visualizations

Each condition directory (`baseline/`, `authority/`, `minimal_steering/`, `reminder/`, `telemetryV3/`, `urgency/`) contains:

| File | Description |
|------|-------------|
| `median_split_classification.json` | H1/H2 statistics and model classifications |
| `RESEARCH_BRIEF.md` | Condition-specific research summary |
| `all_models_data.csv` | Complete dataset for external analysis |
| `comprehensive_stats.json` | Complete provider statistics |
| `provider_comparison_stats.json` | ANOVA and pairwise t-tests across providers |
| `COMPREHENSIVE_STATS_REPORT.txt` | Human-readable statistical summary |
| `h1_bar_chart_comparison.png` | H1 group comparison bar chart |
| `h1_summary_table.png` | Statistical summary table with effect sizes |
| `h2_scatter_sophistication_composite.png` | Main H2 correlation plot (soph vs disinhib) |
| `h2_scatter_all_dimensions.png` | 4-panel: transgression, aggression, tribalism, grandiosity |
| `provider_summary.png` | Combined 4-panel provider analysis |
| `provider_h2_scatters.png` | H2 correlation by provider (2x3 grid) |
| `provider_comparison_summary.png` | Provider comparison: N, sophistication, disinhibition, classification |
| `provider_comparison_dimensions.png` | Provider comparison: all 9 dimensions |
| `all_dimensions_by_provider.png` | 3x3 grid of all dimensions by provider |
| `provider_dimensions_heatmap.png` | Heatmap of dimensions across providers |
| `visualizations/current_profiles_spider.png` | Spider chart of all model profiles |

### Qualitative Examples

Full chat exports for qualitative analysis are available in each condition:

```
<condition>/qualitative_chats/
├── dimension_extremes/     # Min/max per dimension (warmth, transgression, etc.)
├── composite_extremes/     # Sophistication/disinhibition extremes
├── percentiles/            # 5th, 25th, 50th, 75th, 95th percentile responses
└── pattern_types/          # Constrained, outlier, borderline model examples
```

**Manifest**: `research_synthesis/limitations/prompt_design/QUALITATIVE_MANIFEST.md`

### External Validation

| File | Description |
|------|-------------|
| `research_synthesis/limitations/external_evals/EXTERNAL_VALIDATION_BRIEF.md` | Combined ARC-AGI + GPQA analysis |
| `external_validation_consolidated.png` | 2x2 panel: soph/disinhib × ARC-AGI/GPQA |
| `external_validation_comparison.png` | Side-by-side benchmark comparison |
| `arc_agi_validation_analysis.json` | ARC-AGI correlation data |
| `gpqa_validation_analysis.json` | GPQA correlation data |

### BERT Toxicity Validation

| File | Description |
|------|-------------|
| `research_synthesis/bert_validation/BERT_VALIDATION_BRIEF.md` | Cross-condition BERT validation summary |
| `bert_validation/<condition>/bert_validation_results.json` | Primary: BERT vs Aggression results |
| `bert_validation/<condition>/bert_soph_disin_results.json` | Extended: BERT vs Soph/Disin results |
| `bert_validation/<condition>/VALIDATION_REPORT.md` | Per-condition consolidated report |
| `bert_validation/<condition>/scatter_toxicity_vs_aggression.png` | Primary validation scatter |
| `bert_validation/<condition>/scatter_soph_disin_combined.png` | 2x2 grid: Tox/Ins × Soph/Disin |
| `bert_validation/audit_samples.json` | Raw response samples with BERT scores |
| `bert_validation/AUDIT_REPORT.md` | Audit certification (270/270 validated) |

### BERT Qualitative Examples

Raw prompt/response pairs organized by BERT toxicity scores for qualitative analysis.

```
bert_validation/qualitative_analysis/<condition>/
├── max/           # Top 3 highest toxicity responses
├── min/           # Top 3 lowest toxicity responses
├── median/        # 3 responses closest to median
└── outliers/      # Top 5 statistical outliers (>2 SD)
```

| File | Description |
|------|-------------|
| `bert_validation/qualitative_analysis/manifest.json` | Index of all samples with toxicity scores |
| `qualitative_analysis/<condition>/outliers/*.md` | Outlier responses (chat.md format) |
| `qualitative_analysis/<condition>/max/*.md` | Highest toxicity responses |
| `qualitative_analysis/<condition>/min/*.md` | Lowest toxicity responses |

### Prompt Design

| File | Description |
|------|-------------|
| `research_synthesis/limitations/prompt_design/BASELINE_PROMPT_INVENTORY.md` | 51 scenarios across 4 suites |
| `INTERVENTION_PROMPT_INVENTORY.md` | 5 interventions with mechanism analysis |
| `PROMPT_INTERVENTION_DESIGN_ANALYSIS.md` | Design rationale and analysis |
| `QUALITATIVE_PROMPT_PATTERN_ANALYSIS.md` | Which prompts drive high scores |

### Cross-Condition Analysis

- `research_synthesis/cross_condition/repeated_measures_anova_results.json`
- `research_synthesis/cross_condition/variability_analysis_disinhibition.json`
- `research_synthesis/cross_condition/cross_condition_patterns.json`
- `research_synthesis/cross_condition/CONDITION_COMPARISON.md`

### Provider Constraint Analysis

- `research_synthesis/limitations/provider_constraint/SOPH_DISINHIB_RATIO_ANALYSIS.md`
- `research_synthesis/limitations/provider_constraint/soph_disinhib_ratio.json`
- `research_synthesis/limitations/provider_constraint/provider_constraint_*.json`

### Other Limitations

- `research_synthesis/limitations/judge_limitations/JUDGE_AGREEMENT_ANALYSIS.md`
- `research_synthesis/limitations/judge_limitations/judge_agreement_analysis.json`
- `research_synthesis/limitations/factor_structure/FACTOR_STRUCTURE_BASELINE.md`
- `research_synthesis/limitations/median_split/MEDIAN_SPLIT_METHODOLOGY.md`
- `research_synthesis/limitations/median_split/classification_stability_analysis.json`

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
**Statistics Generated**: 2026-01-23 15:32
