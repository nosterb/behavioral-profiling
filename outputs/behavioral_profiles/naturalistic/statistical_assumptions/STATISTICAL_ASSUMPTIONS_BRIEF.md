# Statistical Assumptions Analysis: Naturalistic

**Generated**: 2026-01-19
**Condition**: naturalistic
**N**: 45 models

---

## Data Summary

| Metric | Value |
|--------|-------|
| Models Evaluated | 45 |
| Unique Prompts | 20 |
| Total Evaluations | 896 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Judge Count | 3 |
| Jobs Complete | 17/20 (85%) |
| Outliers Detected | 2 (claude-4.5-haiku-thinking_(thinking), gemini-3-pro-preview) |

---

## Statistical Assumptions Summary

| Check | Result | Status |
|-------|--------|--------|
| Sophistication Symmetric | skew = -0.533 | ❌ |
| Correlation Methods Agree (Full) | Δ = 0.073 | ❌ |
| Correlation Methods Agree (Clean) | Δ = 0.014 | ✅ |
| Residuals Normal (without outliers) | p = 0.0667 | ✅ |
| **Parametric Methods** | sophistication skewed; Pearson/Spearman differ by 0.073 | **⚠️ CAUTION** |

---

## Outliers

**Detection Method**: Models with residuals > 2.0 standard deviations from regression line (Sophistication → Disinhibition)

**Outliers Detected**: 2

| Model | Provider | Sophistication | Disinhibition | Std Residual | Direction |
|-------|----------|----------------|---------------|--------------|-----------|
| claude-4.5-haiku-thinking_(thinking) | Anthropic | 7.12 | 1.57 | 2.76 SD | Above |
| gemini-3-pro-preview | Google | 7.80 | 1.72 | 4.36 SD | Above |

**Impact of Outlier Removal**:
- Pearson r: 0.819 → 0.900 (+0.080)
- Pearson/Spearman Δ: 0.073 → 0.014
- Methods Agree: ❌ → ✅


---

## Normality Tests (Shapiro-Wilk)

| Variable | W | p-value | Normal? |
|----------|---|---------|---------|
| Sophistication | 0.9423 | 0.0261 | ❌ |
| Disinhibition | 0.9098 | 0.0019 | ❌ |
| Depth | 0.9231 | 0.0054 | ❌ |
| Authenticity | 0.9413 | 0.0239 | ❌ |
| Transgression | 0.8733 | 0.0002 | ❌ |
| Aggression | 0.8922 | 0.0005 | ❌ |
| Tribalism | 0.6892 | 0.0000 | ❌ |
| Grandiosity | 0.9853 | 0.8300 | ✅ |

**1/8 variables pass normality (α = 0.05)**

---

## Correlation Robustness

### Full Sample (N = 45)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.8192 | 6.0421e-12 |
| Spearman ρ | 0.8925 | 1.8306e-16 |
| Difference | 0.0733 | - |

**Methods DO NOT agree (threshold: Δ < 0.05)**

### Without Outliers (N = 43)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.8996 | 2.4434e-16 |
| Spearman ρ | 0.8857 | 3.0327e-15 |
| Difference | 0.0139 | - |

**Methods agree (threshold: Δ < 0.05)**

### Comparison

| Metric | Full Sample | Outliers Removed | Change |
|--------|-------------|------------------|--------|
| Pearson r | 0.8192 | 0.8996 | +0.0804 |
| Spearman ρ | 0.8925 | 0.8857 | -0.0068 |
| Δ (difference) | 0.0733 | 0.0139 | -0.0594 |
| Methods Agree | ❌ | ✅ | - |

---

## Residual Analysis

### Full Sample (N = 45)
- Shapiro-Wilk W = 0.7964, p = 0.0000
- Skewness = 2.2451, Kurtosis = 7.0366

### Without Outliers (N = 43)
- Shapiro-Wilk W = 0.9513, p = 0.0667
- Correlation r = 0.8996

---

## Recommendation

**⚠️ CAUTION with parametric methods**

sophistication skewed; Pearson/Spearman differ by 0.073

---

## Visualizations

- `distribution_composites.png` - Sophistication and Disinhibition distributions
- `distribution_disinhibition_dims.png` - Individual disinhibition dimension distributions
- `distribution_qq_plots.png` - Q-Q plots for normality assessment
- `distribution_residuals.png` - Residual analysis plots
- `correlation_robustness.png` - Pearson vs Spearman comparison

---

## Data Provenance

**Source**: `outputs/behavioral_profiles/naturalistic/all_models_data.csv`
**Audit File**: `normality_audit.json`
