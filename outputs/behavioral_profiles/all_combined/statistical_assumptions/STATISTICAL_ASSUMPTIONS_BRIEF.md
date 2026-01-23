# Statistical Assumptions Analysis: All_Combined

**Generated**: 2026-01-19
**Condition**: all_combined
**N**: 45 models

---

## Data Summary

| Metric | Value |
|--------|-------|
| Models Evaluated | 45 |
| Outliers Detected | 3 (deepseek-r1, gpt-5.2-pro, gemini-3-pro-preview) |

---

## Statistical Assumptions Summary

| Check | Result | Status |
|-------|--------|--------|
| Sophistication Symmetric | skew = 0.009 | ✅ |
| Correlation Methods Agree (Full) | Δ = 0.046 | ✅ |
| Correlation Methods Agree (Clean) | Δ = 0.017 | ✅ |
| Residuals Normal (without outliers) | p = 0.4044 | ✅ |
| **Parametric Methods** | Sophistication is symmetric; Pearson/Spearman agree; residuals normal after removing 3 outlier(s) | **✅ OK** |

---

## Outliers

**Detection Method**: Models with residuals > 2.0 standard deviations from regression line (Sophistication → Disinhibition)

**Outliers Detected**: 3

| Model | Provider | Sophistication | Disinhibition | Std Residual | Direction |
|-------|----------|----------------|---------------|--------------|-----------|
| deepseek-r1 | DeepSeek | 6.45 | 2.30 | 2.64 SD | Above |
| gpt-5.2-pro | OpenAI | 7.45 | 1.66 | -2.01 SD | Below |
| gemini-3-pro-preview | Google | 7.15 | 2.57 | 3.28 SD | Above |

**Impact of Outlier Removal**:
- Pearson r: 0.783 → 0.851 (+0.068)
- Pearson/Spearman Δ: 0.046 → 0.017
- Methods Agree: ✅ → ✅


---

## Normality Tests (Shapiro-Wilk)

| Variable | W | p-value | Normal? |
|----------|---|---------|---------|
| Sophistication | 0.9258 | 0.0067 | ❌ |
| Disinhibition | 0.9013 | 0.0010 | ❌ |
| Depth | 0.9385 | 0.0190 | ❌ |
| Authenticity | 0.9268 | 0.0072 | ❌ |
| Transgression | 0.8727 | 0.0001 | ❌ |
| Aggression | 0.8984 | 0.0008 | ❌ |
| Tribalism | 0.8322 | 0.0000 | ❌ |
| Grandiosity | 0.8741 | 0.0002 | ❌ |

**0/8 variables pass normality (α = 0.05)**

---

## Correlation Robustness

### Full Sample (N = 45)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.7830 | 2.0786e-10 |
| Spearman ρ | 0.8286 | 2.1247e-12 |
| Difference | 0.0456 | - |

**Methods agree (threshold: Δ < 0.05)**

### Without Outliers (N = 42)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.8508 | 9.6938e-13 |
| Spearman ρ | 0.8678 | 1.0239e-13 |
| Difference | 0.0169 | - |

**Methods agree (threshold: Δ < 0.05)**

### Comparison

| Metric | Full Sample | Outliers Removed | Change |
|--------|-------------|------------------|--------|
| Pearson r | 0.7830 | 0.8508 | +0.0678 |
| Spearman ρ | 0.8286 | 0.8678 | +0.0392 |
| Δ (difference) | 0.0456 | 0.0169 | -0.0287 |
| Methods Agree | ✅ | ✅ | - |

---

## Residual Analysis

### Full Sample (N = 45)
- Shapiro-Wilk W = 0.9278, p = 0.0078
- Skewness = 0.6662, Kurtosis = 2.1308

### Without Outliers (N = 42)
- Shapiro-Wilk W = 0.9727, p = 0.4044
- Correlation r = 0.8508

---

## Recommendation

**✅ Parametric methods appropriate**

Sophistication is symmetric; Pearson/Spearman agree; residuals normal after removing 3 outlier(s)

---

## Visualizations

- `distribution_composites.png` - Sophistication and Disinhibition distributions
- `distribution_disinhibition_dims.png` - Individual disinhibition dimension distributions
- `distribution_qq_plots.png` - Q-Q plots for normality assessment
- `distribution_residuals.png` - Residual analysis plots
- `correlation_robustness.png` - Pearson vs Spearman comparison

---

## Data Provenance

**Source**: `outputs/behavioral_profiles/all_combined/all_models_data.csv`
**Audit File**: `normality_audit.json`
