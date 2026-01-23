# Statistical Assumptions Analysis: Telemetryv3

**Generated**: 2026-01-19
**Condition**: telemetryV3
**N**: 45 models

---

## Data Summary

| Metric | Value |
|--------|-------|
| Models Evaluated | 45 |
| Unique Prompts | 51 |
| Total Evaluations | 1,470 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Judge Count | 3 |
| Jobs Complete | 30/51 (59%) |
| Outliers Detected | 2 (grok-4-0709, claude-4.5-haiku-thinking_(thinking)) |

---

## Statistical Assumptions Summary

| Check | Result | Status |
|-------|--------|--------|
| Sophistication Symmetric | skew = 0.229 | ✅ |
| Correlation Methods Agree (Full) | Δ = 0.180 | ❌ |
| Correlation Methods Agree (Clean) | Δ = 0.001 | ✅ |
| Residuals Normal (without outliers) | p = 0.006 | ❌ |
| **Parametric Methods** | Pearson/Spearman differ by 0.180 | **⚠️ CAUTION** |

---

## Outliers

**Detection Method**: Models with residuals > 2.0 standard deviations from regression line (Sophistication → Disinhibition)

**Outliers Detected**: 2

| Model | Provider | Sophistication | Disinhibition | Std Residual | Direction |
|-------|----------|----------------|---------------|--------------|-----------|
| grok-4-0709 | xAI | 5.60 | 1.74 | 3.54 SD | Above |
| claude-4.5-haiku-thinking_(thinking) | Anthropic | 7.29 | 1.97 | 4.54 SD | Above |

**Impact of Outlier Removal**:
- Pearson r: 0.625 → 0.799 (+0.175)
- Pearson/Spearman Δ: 0.180 → 0.001
- Methods Agree: ❌ → ✅


---

## Normality Tests (Shapiro-Wilk)

| Variable | W | p-value | Normal? |
|----------|---|---------|---------|
| Sophistication | 0.9277 | 0.0078 | ❌ |
| Disinhibition | 0.6688 | 0.0000 | ❌ |
| Depth | 0.9305 | 0.0098 | ❌ |
| Authenticity | 0.9204 | 0.0044 | ❌ |
| Transgression | 0.7049 | 0.0000 | ❌ |
| Aggression | 0.6339 | 0.0000 | ❌ |
| Tribalism | 0.8280 | 0.0000 | ❌ |
| Grandiosity | 0.8992 | 0.0009 | ❌ |

**0/8 variables pass normality (α = 0.05)**

---

## Correlation Robustness

### Full Sample (N = 45)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.6245 | 4.5426e-06 |
| Spearman ρ | 0.8046 | 2.7559e-11 |
| Difference | 0.1801 | - |

**Methods DO NOT agree (threshold: Δ < 0.05)**

### Without Outliers (N = 43)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.7991 | 1.3364e-10 |
| Spearman ρ | 0.7984 | 1.4261e-10 |
| Difference | 0.0007 | - |

**Methods agree (threshold: Δ < 0.05)**

### Comparison

| Metric | Full Sample | Outliers Removed | Change |
|--------|-------------|------------------|--------|
| Pearson r | 0.6245 | 0.7991 | +0.1746 |
| Spearman ρ | 0.8046 | 0.7984 | -0.0062 |
| Δ (difference) | 0.1801 | 0.0007 | -0.1794 |
| Methods Agree | ❌ | ✅ | - |

---

## Residual Analysis

### Full Sample (N = 45)
- Shapiro-Wilk W = 0.6384, p = 0.0000
- Skewness = 3.0994, Kurtosis = 10.6635

### Without Outliers (N = 43)
- Shapiro-Wilk W = 0.9215, p = 0.006
- Correlation r = 0.7991

---

## Recommendation

**⚠️ CAUTION with parametric methods**

Pearson/Spearman differ by 0.180

---

## Visualizations

- `distribution_composites.png` - Sophistication and Disinhibition distributions
- `distribution_disinhibition_dims.png` - Individual disinhibition dimension distributions
- `distribution_qq_plots.png` - Q-Q plots for normality assessment
- `distribution_residuals.png` - Residual analysis plots
- `correlation_robustness.png` - Pearson vs Spearman comparison

---

## Data Provenance

**Source**: `outputs/behavioral_profiles/telemetryV3/all_models_data.csv`
**Audit File**: `normality_audit.json`
