# Statistical Assumptions Analysis: Reminder

**Generated**: 2026-01-19
**Condition**: reminder
**N**: 46 models

---

## Data Summary

| Metric | Value |
|--------|-------|
| Models Evaluated | 46 |
| Unique Prompts | 15 |
| Total Evaluations | 689 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Judge Count | 3 |
| Jobs Complete | 14/15 (93%) |
| Outliers Detected | 1 (gemini-3-pro-preview) |

---

## Statistical Assumptions Summary

| Check | Result | Status |
|-------|--------|--------|
| Sophistication Symmetric | skew = -0.391 | ✅ |
| Correlation Methods Agree (Full) | Δ = 0.098 | ❌ |
| Correlation Methods Agree (Clean) | Δ = 0.001 | ✅ |
| Residuals Normal (without outliers) | p = 0.0425 | ❌ |
| **Parametric Methods** | Pearson/Spearman differ by 0.098 | **⚠️ CAUTION** |

---

## Outliers

**Detection Method**: Models with residuals > 2.0 standard deviations from regression line (Sophistication → Disinhibition)

**Outliers Detected**: 1

| Model | Provider | Sophistication | Disinhibition | Std Residual | Direction |
|-------|----------|----------------|---------------|--------------|-----------|
| gemini-3-pro-preview | Google | 8.36 | 4.12 | 5.05 SD | Above |

**Impact of Outlier Removal**:
- Pearson r: 0.732 → 0.819 (+0.087)
- Pearson/Spearman Δ: 0.098 → 0.001
- Methods Agree: ❌ → ✅


---

## Normality Tests (Shapiro-Wilk)

| Variable | W | p-value | Normal? |
|----------|---|---------|---------|
| Sophistication | 0.9074 | 0.0014 | ❌ |
| Disinhibition | 0.8558 | 0.0000 | ❌ |
| Depth | 0.9257 | 0.0059 | ❌ |
| Authenticity | 0.8978 | 0.0007 | ❌ |
| Transgression | 0.9063 | 0.0013 | ❌ |
| Aggression | 0.8837 | 0.0003 | ❌ |
| Tribalism | 0.8415 | 0.0000 | ❌ |
| Grandiosity | 0.7773 | 0.0000 | ❌ |

**0/8 variables pass normality (α = 0.05)**

---

## Correlation Robustness

### Full Sample (N = 46)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.7319 | 7.5178e-09 |
| Spearman ρ | 0.8294 | 1.0672e-12 |
| Difference | 0.0975 | - |

**Methods DO NOT agree (threshold: Δ < 0.05)**

### Without Outliers (N = 45)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.8187 | 6.4162e-12 |
| Spearman ρ | 0.8178 | 7.0474e-12 |
| Difference | 0.0009 | - |

**Methods agree (threshold: Δ < 0.05)**

### Comparison

| Metric | Full Sample | Outliers Removed | Change |
|--------|-------------|------------------|--------|
| Pearson r | 0.7319 | 0.8187 | +0.0868 |
| Spearman ρ | 0.8294 | 0.8178 | -0.0116 |
| Δ (difference) | 0.0975 | 0.0009 | -0.0966 |
| Methods Agree | ❌ | ✅ | - |

---

## Residual Analysis

### Full Sample (N = 46)
- Shapiro-Wilk W = 0.7416, p = 0.0000
- Skewness = 2.9429, Kurtosis = 12.3208

### Without Outliers (N = 45)
- Shapiro-Wilk W = 0.9479, p = 0.0425
- Correlation r = 0.8187

---

## Recommendation

**⚠️ CAUTION with parametric methods**

Pearson/Spearman differ by 0.098

---

## Visualizations

- `distribution_composites.png` - Sophistication and Disinhibition distributions
- `distribution_disinhibition_dims.png` - Individual disinhibition dimension distributions
- `distribution_qq_plots.png` - Q-Q plots for normality assessment
- `distribution_residuals.png` - Residual analysis plots
- `correlation_robustness.png` - Pearson vs Spearman comparison

---

## Data Provenance

**Source**: `outputs/behavioral_profiles/reminder/all_models_data.csv`
**Audit File**: `normality_audit.json`
