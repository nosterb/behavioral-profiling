# BERT Toxicity Regression Analysis

**Generated**: 2026-01-16
**Condition**: baseline
**N**: 45 models

---

## Research Question

Does Sophistication predict BERT toxicity independent of Disinhibition, or is the Sophistication-Toxicity correlation mediated through Disinhibition?

---

## Model Comparison

| Model | Formula | R² |
|-------|---------|-----|
| 1 | Toxicity ~ Disinhibition | **0.601** |
| 2 | Toxicity ~ Sophistication | 0.260 |
| 3 | Toxicity ~ Soph + Disin | 0.624 (adj = 0.606) |

**Key observation**: Adding Sophistication to Model 1 increases R² by only 0.023 (2.3%)

---

## Variance Decomposition

| Source | Variance Explained |
|--------|-------------------|
| Disinhibition (unique) | **36.3%** |
| Sophistication (unique) | 2.2% |
| Shared (Soph ∩ Disin) | 23.8% |
| **Total explained** | **62.4%** |

---

## Standardized Coefficients (Model 3)

| Predictor | β | p-value | Significant? |
|-----------|---|---------|--------------|
| Disinhibition | **0.960** | < .0001 | **Yes** |
| Sophistication | -0.237 | 0.123 | No |

---

## Multicollinearity

| Metric | Value | Interpretation |
|--------|-------|----------------|
| r(Soph, Disin) | 0.778 | High correlation |
| VIF | 2.54 | Acceptable (< 5) |

---

## Formal Mediation Analysis

**Model**: Sophistication → Disinhibition → BERT Toxicity

Bootstrap resamples: 5,000

| Effect | Estimate | 95% CI | p-value |
|--------|----------|--------|---------|
| **ACME** (indirect: Soph → Disin → Tox) | 0.0074 | [0.0039, 0.0116] | **< .001** |
| **ADE** (direct: Soph → Tox) | -0.0023 | [-0.0053, 0.0006] | 0.120 |
| **Total effect** | 0.0050 | [0.0014, 0.0087] | 0.008 |
| **Proportion mediated** | **146%** | [89%, 349%] | 0.008 |

### Inconsistent Mediation (Suppression)

The proportion mediated exceeds 100% because:

1. **Indirect effect is positive** (0.0074): Sophistication → ↑Disinhibition → ↑Toxicity
2. **Direct effect is negative** (-0.0023): Sophistication → ↓Toxicity (when controlling for Disinhibition)
3. **Total effect is positive but smaller** (0.0050): The direct and indirect effects partially cancel

This is called **inconsistent mediation** or a **suppression effect**. Disinhibition acts as a suppressor variable that masks a slight protective effect of Sophistication on BERT toxicity.

**Plain English**: More sophisticated models tend to be more disinhibited, which increases toxicity scores. But if you compare models with *equal* disinhibition, sophisticated models are actually *less* toxic (more articulate, less crude).

---

## Interpretation

1. **Disinhibition dominates**: 60.1% of BERT toxicity variance is explained by Disinhibition alone. This validates that BERT toxicity captures the disinhibition behavioral construct.

2. **Sophistication effect is mediated**: The apparent Sophistication-Toxicity correlation (r² = 0.26) is largely explained by Sophistication's correlation with Disinhibition. When controlling for Disinhibition, Sophistication adds only 2.2% unique variance (not statistically significant).

3. **Negative suppression effect**: The negative β for Sophistication (-0.237) suggests that when holding Disinhibition constant, more sophisticated models may actually produce *less* BERT-toxic content. This is consistent with sophisticated models being more articulate/substantive rather than crude/inflammatory.

4. **Shared variance (23.8%)**: This represents the portion of BERT toxicity that's explained by what Sophistication and Disinhibition have in common - likely the general "capability" factor that drives both constructs.

---

## Conclusion

BERT toxicity is primarily a measure of **disinhibition**, not sophistication. The observed correlation between Sophistication and BERT toxicity is a spurious association mediated through Disinhibition. More capable models aren't inherently "toxic" - they tend to score higher on disinhibition behaviors, which in turn trigger BERT toxicity detection.

This supports the validity of:
- BERT as an independent validator of the Disinhibition construct
- The distinction between Sophistication (capability) and Disinhibition (behavioral style)

---

## Convergence with GPQA Analysis

This regression analysis converges with the GPQA mediation analysis:

| Capability Measure | Direct Effect (controlling for Disinhibition) | Significant? |
|-------------------|-----------------------------------------------|--------------|
| Sophistication | β = -0.237 | No (p = 0.123) |
| GPQA | r = -0.218 | No (p = 0.216) |

Both analyses show:
1. **Full mediation**: Capability → Toxicity is explained by Capability → Disinhibition → Toxicity
2. **Negative direct effect**: Slight protective effect of capability when disinhibition is held constant
3. **Suppression/inconsistent mediation**: The indirect and direct effects partially cancel

See `../framework/STATISTICAL_RELATIONSHIPS.md` for the integrated theoretical model.

---

## Data Provenance & Audit Trail

**Audit file**: `regression_analysis_audit.json`

### Source Files

| Source | File |
|--------|------|
| BERT toxicity scores | `baseline/bert_validation_results.json` |
| Behavioral profiles | `../../baseline/profiles/*.json` |
| Sophistication/Disinhibition | `../../baseline/median_split_classification.json` |

### Methodology

| Component | Method |
|-----------|--------|
| Regression | Ordinary Least Squares (OLS) |
| Mediation | Causal mediation with bootstrap (n=5000) |
| Variance decomposition | Hierarchical regression |
| Multicollinearity | Variance Inflation Factor (VIF) |

### Reproducibility

The audit JSON contains:
- All model coefficients and R² values
- Variance decomposition calculations
- Bootstrap mediation estimates with 95% CIs
- Convergence comparison with GPQA analysis
