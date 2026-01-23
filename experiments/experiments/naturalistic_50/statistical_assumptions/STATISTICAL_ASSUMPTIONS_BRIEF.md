# Statistical Assumptions Analysis: Naturalistic_50

**Generated**: 2026-01-19
**Condition**: naturalistic_50
**N**: 44 models

---

## Data Summary

| Metric | Value |
|--------|-------|
| Models Evaluated | 44 |
| Unique Prompts | 20 |
| Total Evaluations | 540 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Judge Count | 3 |
| Jobs Complete | 12/20 (60%) |
| Outliers Detected | 1 (gemini-3-pro-preview) |

---

## Statistical Assumptions Summary

| Check | Result | Status |
|-------|--------|--------|
| Sophistication Symmetric | skew = -0.081 | ✅ |
| Correlation Methods Agree (Full) | Δ = 0.058 | ❌ |
| Correlation Methods Agree (Clean) | Δ = 0.021 | ✅ |
| Residuals Normal (without outliers) | p = 0.1138 | ✅ |
| **Parametric Methods** | Pearson/Spearman differ by 0.058 | **⚠️ CAUTION** |

---

## Outliers

**Detection Method**: Models with residuals > 2.0 standard deviations from regression line (Sophistication → Disinhibition)

**Outliers Detected**: 1

| Model | Provider | Sophistication | Disinhibition | Std Residual | Direction |
|-------|----------|----------------|---------------|--------------|-----------|
| gemini-3-pro-preview | Google | 37.75 | 8.62 | 3.90 SD | Above |

**Impact of Outlier Removal**:
- Pearson r: 0.698 → 0.718 (+0.020)
- Pearson/Spearman Δ: 0.058 → 0.021
- Methods Agree: ❌ → ✅


---

## Normality Tests (Shapiro-Wilk)

| Variable | W | p-value | Normal? |
|----------|---|---------|---------|
| Sophistication | 0.9412 | 0.0261 | ❌ |
| Disinhibition | 0.8617 | 0.0001 | ❌ |
| Depth | 0.9566 | 0.0967 | ✅ |
| Authenticity | 0.9116 | 0.0025 | ❌ |
| Transgression | 0.8539 | 0.0001 | ❌ |
| Aggression | 0.7803 | 0.0000 | ❌ |
| Tribalism | 0.9454 | 0.0371 | ❌ |
| Grandiosity | 0.8998 | 0.0011 | ❌ |

**1/8 variables pass normality (α = 0.05)**

---

## Correlation Robustness

### Full Sample (N = 44)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.6980 | 1.3884e-07 |
| Spearman ρ | 0.7557 | 3.0247e-09 |
| Difference | 0.0577 | - |

**Methods DO NOT agree (threshold: Δ < 0.05)**

### Without Outliers (N = 43)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.7181 | 5.9483e-08 |
| Spearman ρ | 0.7392 | 1.5049e-08 |
| Difference | 0.0211 | - |

**Methods agree (threshold: Δ < 0.05)**

### Comparison

| Metric | Full Sample | Outliers Removed | Change |
|--------|-------------|------------------|--------|
| Pearson r | 0.6980 | 0.7181 | +0.0201 |
| Spearman ρ | 0.7557 | 0.7392 | -0.0165 |
| Δ (difference) | 0.0577 | 0.0211 | -0.0366 |
| Methods Agree | ❌ | ✅ | - |

---

## Residual Analysis

### Full Sample (N = 44)
- Shapiro-Wilk W = 0.9026, p = 0.0013
- Skewness = 1.4391, Kurtosis = 3.5573

### Without Outliers (N = 43)
- Shapiro-Wilk W = 0.9577, p = 0.1138
- Correlation r = 0.7181

---

## Recommendation

**⚠️ CAUTION with parametric methods**

Pearson/Spearman differ by 0.058

---

## Visualizations

- `distribution_composites.png` - Sophistication and Disinhibition distributions
- `distribution_disinhibition_dims.png` - Individual disinhibition dimension distributions
- `distribution_qq_plots.png` - Q-Q plots for normality assessment
- `distribution_residuals.png` - Residual analysis plots
- `correlation_robustness.png` - Pearson vs Spearman comparison

---

## Data Provenance

**Source**: `outputs/behavioral_profiles/naturalistic_50/all_models_data.csv`
**Audit File**: `normality_audit.json`
