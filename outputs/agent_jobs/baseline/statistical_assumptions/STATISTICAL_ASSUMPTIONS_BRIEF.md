# Statistical Assumptions Analysis: Baseline

**Generated**: 2026-01-19
**Condition**: baseline
**N**: 45 models

---

## Data Summary

| Metric | Value |
|--------|-------|
| Models Evaluated | 45 |
| Unique Prompts | 50 |
| Total Evaluations | 2,299 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |
| Judge Count | 3 |
| Jobs Complete | 49/50 (98%) |
| Outliers Detected | 1 (gemini-3-pro-preview) |

---

## Statistical Assumptions Summary

| Check | Result | Status |
|-------|--------|--------|
| Sophistication Symmetric | skew = -0.022 | ✅ |
| Correlation Methods Agree (Full) | Δ = 0.018 | ✅ |
| Correlation Methods Agree (Clean) | Δ = 0.037 | ✅ |
| Residuals Normal (without outliers) | p = 0.8313 | ✅ |
| **Parametric Methods** | Sophistication is symmetric; Pearson/Spearman agree; residuals normal after removing 1 outlier(s) | **✅ OK** |

---

## Outliers

**Detection Method**: Models with residuals > 2.0 standard deviations from regression line (Sophistication → Disinhibition)

**Outliers Detected**: 1

| Model | Provider | Sophistication | Disinhibition | Std Residual | Direction |
|-------|----------|----------------|---------------|--------------|-----------|
| gemini-3-pro-preview | Google | 7.50 | 2.31 | 4.38 SD | Above |

**Impact of Outlier Removal**:
- Pearson r: 0.778 → 0.820 (+0.041)
- Pearson/Spearman Δ: 0.018 → 0.037
- Methods Agree: ✅ → ✅


---

## Normality Tests (Shapiro-Wilk)

| Variable | W | p-value | Normal? |
|----------|---|---------|---------|
| Sophistication | 0.9445 | 0.0315 | ❌ |
| Disinhibition | 0.8679 | 0.0001 | ❌ |
| Depth | 0.9559 | 0.0848 | ✅ |
| Authenticity | 0.9236 | 0.0056 | ❌ |
| Transgression | 0.8973 | 0.0008 | ❌ |
| Aggression | 0.9326 | 0.0116 | ❌ |
| Tribalism | 0.7819 | 0.0000 | ❌ |
| Grandiosity | 0.8809 | 0.0003 | ❌ |

**1/8 variables pass normality (α = 0.05)**

---

## Correlation Robustness

### Full Sample (N = 45)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.7785 | 3.0815e-10 |
| Spearman ρ | 0.7963 | 6.1404e-11 |
| Difference | 0.0179 | - |

**Methods agree (threshold: Δ < 0.05)**

### Without Outliers (N = 44)

| Method | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.8195 | 1.0352e-11 |
| Spearman ρ | 0.7825 | 3.5124e-10 |
| Difference | 0.0370 | - |

**Methods agree (threshold: Δ < 0.05)**

### Comparison

| Metric | Full Sample | Outliers Removed | Change |
|--------|-------------|------------------|--------|
| Pearson r | 0.7785 | 0.8195 | +0.0410 |
| Spearman ρ | 0.7963 | 0.7825 | -0.0138 |
| Δ (difference) | 0.0179 | 0.0370 | +0.0191 |
| Methods Agree | ✅ | ✅ | - |

---

## Residual Analysis

### Full Sample (N = 45)
- Shapiro-Wilk W = 0.8623, p = 0.0001
- Skewness = 1.7508, Kurtosis = 6.6883

### Without Outliers (N = 44)
- Shapiro-Wilk W = 0.9851, p = 0.8313
- Correlation r = 0.8195

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

**Source**: `outputs/behavioral_profiles/baseline/all_models_data.csv`
**Audit File**: `normality_audit.json`
