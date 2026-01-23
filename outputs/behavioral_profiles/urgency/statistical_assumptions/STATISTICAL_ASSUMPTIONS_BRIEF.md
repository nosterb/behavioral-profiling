# Statistical Assumptions Analysis: Urgency

**Generated**: 2026-01-19
**Condition**: urgency
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
| Outliers Detected | 1 (deepseek-r1) |

---

## Statistical Assumptions Summary

| Check | Result | Status |
|-------|--------|--------|
| Sophistication Symmetric | skew = 0.036 | ✅ |
| Correlation Methods Agree (Full) | Δ = 0.025 | ✅ |
| Correlation Methods Agree (Clean) | Δ = 0.001 | ✅ |
| Residuals Normal (without outliers) | p = 0.7895 | ✅ |
| **Parametric Methods** | Sophistication is symmetric; Pearson/Spearman agree; residuals normal after removing 1 outlier(s) | **✅ OK** |

---

## Outliers

**Detection Method**: Models with residuals > 2.0 standard deviations from regression line (Sophistication → Disinhibition)

**Outliers Detected**: 1

| Model | Provider | Sophistication | Disinhibition | Std Residual | Direction |
|-------|----------|----------------|---------------|--------------|-----------|
| deepseek-r1 | DeepSeek | 7.18 | 4.81 | 3.32 SD | Above |

**Impact of Outlier Removal**:
- Pearson r: 0.743 → 0.768 (+0.025)
- Pearson/Spearman Δ: 0.025 → 0.001
- Methods Agree: ✅ → ✅


---

## Normality Tests (Shapiro-Wilk)

| Variable | W | p-value | Normal? |
|----------|---|---------|---------|
| Sophistication | 0.9243 | 0.0059 | ❌ |
| Disinhibition | 0.8876 | 0.0004 | ❌ |
| Depth | 0.9366 | 0.0161 | ❌ |
| Authenticity | 0.9317 | 0.0107 | ❌ |
| Transgression | 0.8680 | 0.0001 | ❌ |
| Aggression | 0.8869 | 0.0004 | ❌ |
| Tribalism | 0.7657 | 0.0000 | ❌ |
| Grandiosity | 0.8873 | 0.0004 | ❌ |

**0/8 variables pass normality (α = 0.05)**

---

## Correlation Robustness

### Full Sample (N = 45)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.7432 | 5.0178e-09 |
| Spearman ρ | 0.7684 | 7.1816e-10 |
| Difference | 0.0252 | - |

**Methods agree (threshold: Δ < 0.05)**

### Without Outliers (N = 44)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.7677 | 1.1985e-09 |
| Spearman ρ | 0.7669 | 1.2791e-09 |
| Difference | 0.0008 | - |

**Methods agree (threshold: Δ < 0.05)**

### Comparison

| Metric | Full Sample | Outliers Removed | Change |
|--------|-------------|------------------|--------|
| Pearson r | 0.7432 | 0.7677 | +0.0245 |
| Spearman ρ | 0.7684 | 0.7669 | -0.0015 |
| Δ (difference) | 0.0252 | 0.0008 | -0.0244 |
| Methods Agree | ✅ | ✅ | - |

---

## Residual Analysis

### Full Sample (N = 45)
- Shapiro-Wilk W = 0.9623, p = 0.1495
- Skewness = 0.6402, Kurtosis = 1.4059

### Without Outliers (N = 44)
- Shapiro-Wilk W = 0.9839, p = 0.7895
- Correlation r = 0.7677

---

## Recommendation

**✅ Parametric methods appropriate**

Sophistication is symmetric; Pearson/Spearman agree; residuals normal after removing 1 outlier(s)

---

## Visualizations

- `distribution_composites.png` - Sophistication and Disinhibition distributions
- `distribution_disinhibition_dims.png` - Individual disinhibition dimension distributions
- `distribution_qq_plots.png` - Q-Q plots for normality assessment
- `distribution_residuals.png` - Residual analysis plots
- `correlation_robustness.png` - Pearson vs Spearman comparison

---

## Data Provenance

**Source**: `outputs/behavioral_profiles/urgency/all_models_data.csv`
**Audit File**: `normality_audit.json`
