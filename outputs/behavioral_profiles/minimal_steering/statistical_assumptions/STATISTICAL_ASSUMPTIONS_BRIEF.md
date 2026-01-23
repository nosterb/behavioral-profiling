# Statistical Assumptions Analysis: Minimal_Steering

**Generated**: 2026-01-19
**Condition**: minimal_steering
**N**: 46 models

---

## Data Summary

| Metric | Value |
|--------|-------|
| Models Evaluated | 46 |
| Unique Prompts | 51 |
| Total Evaluations | 2,341 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Judge Count | 3 |
| Jobs Complete | 48/51 (94%) |
| Outliers Detected | 2 (gemini-2.5-pro, claude-4.5-opus-global) |

---

## Statistical Assumptions Summary

| Check | Result | Status |
|-------|--------|--------|
| Sophistication Symmetric | skew = -0.110 | ✅ |
| Correlation Methods Agree (Full) | Δ = 0.005 | ✅ |
| Correlation Methods Agree (Clean) | Δ = 0.000 | ✅ |
| Residuals Normal (without outliers) | p = 0.9603 | ✅ |
| **Parametric Methods** | Sophistication is symmetric; Pearson/Spearman agree; residuals normal after removing 2 outlier(s) | **✅ OK** |

---

## Outliers

**Detection Method**: Models with residuals > 2.0 standard deviations from regression line (Sophistication → Disinhibition)

**Outliers Detected**: 2

| Model | Provider | Sophistication | Disinhibition | Std Residual | Direction |
|-------|----------|----------------|---------------|--------------|-----------|
| gemini-2.5-pro | Google | 6.16 | 1.29 | -2.47 SD | Below |
| claude-4.5-opus-global | Anthropic | 6.91 | 1.58 | 2.27 SD | Above |

**Impact of Outlier Removal**:
- Pearson r: 0.860 → 0.880 (+0.021)
- Pearson/Spearman Δ: 0.005 → 0.000
- Methods Agree: ✅ → ✅


---

## Normality Tests (Shapiro-Wilk)

| Variable | W | p-value | Normal? |
|----------|---|---------|---------|
| Sophistication | 0.9380 | 0.0165 | ❌ |
| Disinhibition | 0.9318 | 0.0098 | ❌ |
| Depth | 0.9399 | 0.0194 | ❌ |
| Authenticity | 0.9351 | 0.0130 | ❌ |
| Transgression | 0.8737 | 0.0001 | ❌ |
| Aggression | 0.8779 | 0.0002 | ❌ |
| Tribalism | 0.9473 | 0.0371 | ❌ |
| Grandiosity | 0.9832 | 0.7388 | ✅ |

**1/8 variables pass normality (α = 0.05)**

---

## Correlation Robustness

### Full Sample (N = 46)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.8596 | 2.0352e-14 |
| Spearman ρ | 0.8643 | 1.0158e-14 |
| Difference | 0.0047 | - |

**Methods agree (threshold: Δ < 0.05)**

### Without Outliers (N = 44)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.8802 | 3.4902e-15 |
| Spearman ρ | 0.8802 | 3.5188e-15 |
| Difference | 0.0000 | - |

**Methods agree (threshold: Δ < 0.05)**

### Comparison

| Metric | Full Sample | Outliers Removed | Change |
|--------|-------------|------------------|--------|
| Pearson r | 0.8596 | 0.8802 | +0.0206 |
| Spearman ρ | 0.8643 | 0.8802 | +0.0159 |
| Δ (difference) | 0.0047 | 0.0000 | -0.0047 |
| Methods Agree | ✅ | ✅ | - |

---

## Residual Analysis

### Full Sample (N = 46)
- Shapiro-Wilk W = 0.9952, p = 0.9995
- Skewness = -0.0684, Kurtosis = -0.0640

### Without Outliers (N = 44)
- Shapiro-Wilk W = 0.9897, p = 0.9603
- Correlation r = 0.8802

---

## Recommendation

**✅ Parametric methods appropriate**

Sophistication is symmetric; Pearson/Spearman agree; residuals normal after removing 2 outlier(s)

---

## Visualizations

- `distribution_composites.png` - Sophistication and Disinhibition distributions
- `distribution_disinhibition_dims.png` - Individual disinhibition dimension distributions
- `distribution_qq_plots.png` - Q-Q plots for normality assessment
- `distribution_residuals.png` - Residual analysis plots
- `correlation_robustness.png` - Pearson vs Spearman comparison

---

## Data Provenance

**Source**: `outputs/behavioral_profiles/minimal_steering/all_models_data.csv`
**Audit File**: `normality_audit.json`
