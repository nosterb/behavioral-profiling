# Pre-Registration: H4 Advanced Reasoning Hypothesis

**Pre-Registration ID**: H4-AR-20260118
**Timestamp**: 2026-01-18T16:15:00Z
**Author**: Nicholas Osterbur (Independent Researcher)
**Status**: Pre-Registered (Awaiting Analysis)

---

## Theory Statement

**Advanced reasoning capability unlocks disinhibitive behavioral patterns**

Models with enhanced reasoning architectures (Chain-of-Thought, Test-Time Scaling, Mixture-of-Experts, extended thinking modes) exhibit more potential pattern combinations during inference. This expanded pattern space unlocks and encourages more disinhibitive behavioral traits, resulting in detectably higher toxicity outputs that scale with "applied thinking effort."

### Mechanism Hypothesis

```
Advanced Reasoning Architecture (MoE, TTS, CoT, etc.)
    ↓
Expanded Inference Pattern Space
    ↓
More Potential Behavioral Combinations
    ↓
Higher Disinhibition Expression
    ↓
Increased Detectable Toxicity
```

---

## Testable Hypotheses

### H4 (Main Hypothesis)

**H4**: Applied thinking effort positively correlates with sophistication, disinhibition, and toxicity.

### H4-H2 (Correlation Hypotheses)

Models with higher levels of overall "applied thinking effort" have higher levels of:

| Sub-Hypothesis | Prediction | Measure |
|----------------|------------|---------|
| **H4-H2a** | Higher sophistication | (depth + authenticity) / 2 |
| **H4-H2b** | Higher disinhibition | mean(transgression, aggression, tribalism, grandiosity) |
| **H4-H2c** | Higher toxicity (via disinhibition) | BERT toxicity score |

**Statistical Test**: Spearman correlation (ordinal thinking effort scale) or ANOVA across effort categories.

### H4-H1 (Group Overlap Hypothesis)

**H4-H1**: Models with higher "applied thinking effort" significantly overlap with H1 high-sophistication groups; models with lower effort overlap with H1 low-sophistication groups.

| Thinking Effort | Predicted H1 Group |
|-----------------|-------------------|
| None, Low | Low Sophistication |
| Medium, Medium-High | Transitional |
| High, Very High, Maximum | High Sophistication |

**Statistical Test**: Chi-square test of independence; Cramer's V effect size.

### H4a-H1 (Borderline/Flipper Hypothesis)

**H4a-H1**: Models with Medium to Medium-High "applied thinking effort" are strongly correlated with the "borderline/flipper" category of models occupying the transitional zone near the median split.

**Definition of Borderline**: Models within ±0.15 of median sophistication (existing `BORDERLINE_THRESHOLD`).

**Statistical Test**: Fisher's exact test; odds ratio for Medium/Medium-High being borderline.

---

## Applied Thinking Effort Scale

Ordinal scale based on architectural features:

| Level | Code | Description | Example Models |
|-------|------|-------------|----------------|
| **None** | 0 | No reasoning enhancement | Claude 3 Haiku, GPT-3.5 |
| **Low** | 1 | Basic prompted reasoning | Claude 4 Sonnet, GPT-4.1, Llama 4 |
| **Medium** | 2 | Moderate inference compute | Llama 3.3 70B, Gemini 2.0 Flash |
| **Medium-High** | 3 | Enhanced reasoning | Llama 3.2 90B |
| **High** | 4 | Native TTS/CoT | Claude 4.5 Haiku-Thinking, O3 Mini, Qwen3-32B |
| **Very High** | 5 | Extended thinking | Claude 4.5 Sonnet-Thinking, DeepSeek-R1, Grok 3/4 |
| **Maximum** | 6 | Unrestricted thinking | Claude 4.5 Opus-Thinking, GPT-5.2 Pro |

### Assessment Criteria

| Feature | Contribution to Score |
|---------|----------------------|
| MoE Architecture | +1 if active routing |
| Test-Time Scaling (TTS) | +2 if native support |
| Reasoning Mode | +1 (Prompted), +2 (Native), +3 (Extended) |
| Visible Chain-of-Thought | +1 if <think> tags or thinking blocks |

---

## Data Sources

### Primary Data

| Source | Description |
|--------|-------------|
| `model_config/thinking_assessment.csv` | Model architecture survey with Est_Thinking_Effort labels |
| `outputs/behavioral_profiles/baseline/profiles/*.json` | Behavioral dimension scores |
| `outputs/behavioral_profiles/baseline/median_split_classification.json` | H1 group assignments |

### Existing Constructs (from H1/H2)

| Construct | Definition | Source |
|-----------|------------|--------|
| Sophistication | (depth + authenticity) / 2 | behavioral_constants.py |
| Disinhibition | mean(transgression, aggression, tribalism, grandiosity) | behavioral_constants.py |
| Borderline | ±0.15 of median sophistication | H2 scatter analysis |

### External Validation

| Source | Purpose |
|--------|---------|
| BERT toxicity scores | Independent toxicity measure |
| GPQA/ARC-AGI/AIME | Capability validation |

---

## Analysis Plan

### Phase 1: Data Preparation

1. Load `thinking_assessment.csv` and merge with behavioral profiles
2. Convert Est_Thinking_Effort to ordinal scale (0-6)
3. Calculate sophistication and disinhibition composites
4. Merge H1 classification (high/low sophistication group)
5. Identify borderline models

### Phase 2: H4-H2 Analysis (Correlations)

```python
# Spearman correlations (ordinal predictor)
spearman(thinking_effort, sophistication)
spearman(thinking_effort, disinhibition)
spearman(thinking_effort, bert_toxicity)

# Alternative: One-way ANOVA across effort categories
anova(sophistication ~ effort_category)
anova(disinhibition ~ effort_category)
```

### Phase 3: H4-H1 Analysis (Group Overlap)

```python
# Chi-square: thinking_effort_group × H1_group
chi2, p = chi2_contingency(crosstab(effort_group, h1_group))
cramers_v = sqrt(chi2 / (n * (min(k-1, r-1))))

# Classification agreement
kappa = cohen_kappa(predicted_group, h1_group)
```

### Phase 4: H4a-H1 Analysis (Borderline Overlap)

```python
# Fisher's exact: Medium/Medium-High vs borderline status
odds_ratio, p = fisher_exact([[medium_borderline, medium_not],
                              [other_borderline, other_not]])
```

### Phase 5: Mediation Analysis (if H4-H2c supported)

```
Thinking Effort → Disinhibition → BERT Toxicity
```

Test indirect effect via bootstrapped mediation.

---

## Expected Results

| Hypothesis | Expected Direction | Threshold |
|------------|-------------------|-----------|
| H4-H2a (Soph) | Positive | ρ > 0.50 |
| H4-H2b (Disin) | Positive | ρ > 0.40 |
| H4-H2c (Tox) | Positive | ρ > 0.30 |
| H4-H1 | Significant overlap | Cramer's V > 0.30 |
| H4a-H1 | Medium = Borderline | OR > 2.0 |

---

## Falsification Criteria

The theory is **falsified** if:

1. **H4-H2**: No significant correlation between thinking effort and any of sophistication, disinhibition, or toxicity (all p > 0.05)
2. **H4-H1**: H1 group membership is independent of thinking effort (χ² p > 0.05)
3. **H4a-H1**: Medium/Medium-High models are NOT overrepresented in borderline category (OR < 1.0)

---

## Limitations (Anticipated)

1. **Ordinal scale**: Thinking effort is ordinal, not interval—limits statistical tests
2. **Sample size**: Only 45-48 models; some effort categories may be sparse
3. **Confounding**: Model generation (newer = more reasoning + more sophisticated)
4. **Provider effects**: Anthropic dominance (42%) may confound effort-sophistication relationship
5. **Measurement**: "Applied thinking effort" is estimated, not directly measured

---

## Timeline

| Phase | Target |
|-------|--------|
| Pre-registration | 2026-01-18 (COMPLETE) |
| Data merge & validation | 2026-01-18 |
| H4-H2 analysis | 2026-01-19 |
| H4-H1 analysis | 2026-01-19 |
| H4a-H1 analysis | 2026-01-19 |
| Results brief | 2026-01-20 |

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-18 | 1.0 | Initial pre-registration |

---

*Pre-registered prior to data analysis. This document is timestamped and uploaded to S3 for posterity.*
