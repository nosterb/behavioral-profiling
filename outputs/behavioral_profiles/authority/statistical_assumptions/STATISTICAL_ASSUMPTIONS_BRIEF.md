# Statistical Assumptions Analysis: Authority

**Generated**: 2026-01-19
**Condition**: authority
**N**: 45 models

---

## Data Summary

| Metric | Value |
|--------|-------|
| Models Evaluated | 45 |
| Unique Prompts | 51 |
| Total Evaluations | 2,294 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Judge Count | 3 |
| Jobs Complete | 50/51 (98%) |
| Outliers Detected | 1 (gemini-3-pro-preview) |

---

## Statistical Assumptions Summary

| Check | Result | Status |
|-------|--------|--------|
| Sophistication Symmetric | skew = -0.086 | ✅ |
| Correlation Methods Agree (Full) | Δ = 0.084 | ❌ |
| Correlation Methods Agree (Clean) | Δ = 0.014 | ✅ |
| Residuals Normal (without outliers) | p = 0.0059 | ❌ |
| **Parametric Methods** | Pearson/Spearman differ by 0.084 | **⚠️ CAUTION** |

---

## Outliers

**Detection Method**: Models with residuals > 2.0 standard deviations from regression line (Sophistication → Disinhibition)

**Outliers Detected**: 1

| Model | Provider | Sophistication | Disinhibition | Std Residual | Direction |
|-------|----------|----------------|---------------|--------------|-----------|
| gemini-3-pro-preview | Google | 8.24 | 2.75 | 4.73 SD | Above |

**Impact of Outlier Removal**:
- Pearson r: 0.770 → 0.830 (+0.060)
- Pearson/Spearman Δ: 0.084 → 0.014
- Methods Agree: ❌ → ✅


---

## Normality Tests (Shapiro-Wilk)

| Variable | W | p-value | Normal? |
|----------|---|---------|---------|
| Sophistication | 0.9271 | 0.0074 | ❌ |
| Disinhibition | 0.8522 | 0.0000 | ❌ |
| Depth | 0.9469 | 0.0389 | ❌ |
| Authenticity | 0.9282 | 0.0081 | ❌ |
| Transgression | 0.8460 | 0.0000 | ❌ |
| Aggression | 0.8783 | 0.0002 | ❌ |
| Tribalism | 0.7625 | 0.0000 | ❌ |
| Grandiosity | 0.8834 | 0.0003 | ❌ |

**0/8 variables pass normality (α = 0.05)**

---

## Correlation Robustness

### Full Sample (N = 45)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.7702 | 6.1812e-10 |
| Spearman ρ | 0.8543 | 8.4897e-14 |
| Difference | 0.0841 | - |

**Methods DO NOT agree (threshold: Δ < 0.05)**

### Without Outliers (N = 44)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.8300 | 3.2879e-12 |
| Spearman ρ | 0.8441 | 6.1353e-13 |
| Difference | 0.0142 | - |

**Methods agree (threshold: Δ < 0.05)**

### Comparison

| Metric | Full Sample | Outliers Removed | Change |
|--------|-------------|------------------|--------|
| Pearson r | 0.7702 | 0.8300 | +0.0598 |
| Spearman ρ | 0.8543 | 0.8441 | -0.0102 |
| Δ (difference) | 0.0841 | 0.0142 | -0.0699 |
| Methods Agree | ❌ | ✅ | - |

---

## Residual Analysis

### Full Sample (N = 45)
- Shapiro-Wilk W = 0.7800, p = 0.0000
- Skewness = 2.5405, Kurtosis = 9.2443

### Without Outliers (N = 44)
- Shapiro-Wilk W = 0.9228, p = 0.0059
- Correlation r = 0.83

---

## Recommendation

**⚠️ CAUTION with parametric methods**

Pearson/Spearman differ by 0.084

---

## Visualizations

- `distribution_composites.png` - Sophistication and Disinhibition distributions
- `distribution_disinhibition_dims.png` - Individual disinhibition dimension distributions
- `distribution_qq_plots.png` - Q-Q plots for normality assessment
- `distribution_residuals.png` - Residual analysis plots
- `correlation_robustness.png` - Pearson vs Spearman comparison

---

## Data Provenance

**Source**: `outputs/behavioral_profiles/authority/all_models_data.csv`
**Audit File**: `normality_audit.json`
