# Quadrant Classification: Sophistication × Disinhibition

**Status**: Exploratory Analysis
**Generated**: 2026-01-12
**Data**: Baseline condition (N=45)

---

## Overview

Alternative to median-split classification using both sophistication AND disinhibition dimensions to create 4 behavioral categories.

```
                        DISINHIBITION
                    Low              High
              ┌─────────────┬─────────────┐
       High   │ CONSTRAINED │   CAPABLE   │
 SOPH         │ (deliberate)│ (expected)  │
              ├─────────────┼─────────────┤
       Low    │   TYPICAL   │   UNUSUAL   │
              │  (legacy)   │ (anomalous) │
              └─────────────┴─────────────┘
```

---

## Classification Results

| Quadrant | N | % | Description |
|----------|---|---|-------------|
| **Constrained** | 3 | 7% | High capability, deliberately low disinhibition |
| **Capable** | 19 | 42% | High capability, expected H2 correlation |
| **Typical** | 20 | 44% | Legacy/smaller models, both metrics low |
| **Unusual** | 3 | 7% | Low capability but high disinhibition |

### Thresholds

- Sophistication median: **5.94**
- Disinhibition median: **1.55**

---

## Quadrant Details

### Constrained (n=3)

High sophistication but below-median disinhibition. Evidence of deliberate behavioral constraint.

| Model | Provider | Soph | Dis | Residual |
|-------|----------|------|-----|----------|
| gpt-oss-120b | OpenAI | 7.12 | 1.49 | -0.230 |
| gpt-5.2_pro | OpenAI | 7.34 | 1.55 | -0.203 |
| o3 | OpenAI | 7.18 | 1.55 | -0.180 |

**Pattern**: All OpenAI. Strong negative residuals confirm below-predicted disinhibition.

### Capable (n=19)

High sophistication with above-median disinhibition. Expected H2 relationship.

| Model | Provider | Soph | Dis | Residual |
|-------|----------|------|-----|----------|
| gemini-3-pro-preview | Google | 7.50 | 2.31 | +0.530 |
| grok-4-0709 | xAI | 6.63 | 1.86 | +0.217 |
| claude-4.5-sonnet | Anthropic | 6.77 | 1.83 | +0.158 |
| deepseek-r1 | DeepSeek | 6.26 | 1.64 | +0.050 |
| ... | | | | |

**Pattern**: Mixed providers. Positive residuals indicate above-predicted disinhibition.

### Typical (n=20)

Below-median on both dimensions. Legacy and smaller models.

| Model | Provider | Soph | Dis | Residual |
|-------|----------|------|-----|----------|
| gpt-3.5_turbo | OpenAI | 4.01 | 1.39 | +0.135 |
| claude-3-opus | Anthropic | 4.68 | 1.36 | -0.001 |
| llama-3.3-70b | Meta | 5.13 | 1.40 | -0.028 |
| ... | | | | |

**Pattern**: Older Claude (3.x), older GPT (3.5/4), all Meta/Llama, all AWS Nova, all Mistral.

### Unusual (n=3)

Below-median sophistication but above-median disinhibition. Anomalous pattern.

| Model | Provider | Soph | Dis | Residual |
|-------|----------|------|-----|----------|
| claude-4-opus-thinking | Anthropic | 5.94 | 1.66 | +0.114 |
| claude-4-opus | Anthropic | 5.92 | 1.65 | +0.105 |
| claude-4.1-opus-thinking | Anthropic | 5.89 | 1.61 | +0.072 |

**Pattern**: All Claude 4 Opus variants. Borderline sophistication (just below median) with elevated disinhibition. May represent measurement edge cases rather than true anomaly.

---

## Provider Distribution

| Provider | Constrained | Capable | Typical | Unusual | Total |
|----------|-------------|---------|---------|---------|-------|
| **Anthropic** | 0 | 9 | 7 | 3 | 19 |
| **OpenAI** | 3 | 3 | 3 | 0 | 9 |
| **Google** | 0 | 3 | 0 | 0 | 3 |
| **Meta** | 0 | 0 | 5 | 0 | 5 |
| **AWS** | 0 | 0 | 3 | 0 | 3 |
| **xAI** | 0 | 2 | 0 | 0 | 2 |
| **Mistral** | 0 | 0 | 2 | 0 | 2 |
| **DeepSeek** | 0 | 1 | 0 | 0 | 1 |
| **Alibaba** | 0 | 1 | 0 | 0 | 1 |

### Key Provider Patterns

- **OpenAI**: Only provider with models in Constrained quadrant (3/9 = 33%)
- **Anthropic**: Split across Capable (47%), Typical (37%), Unusual (16%)
- **Google/xAI/DeepSeek/Alibaba**: 100% in Capable quadrant
- **Meta/AWS/Mistral**: 100% in Typical quadrant

---

## Comparison to Median Split

| Method | Groups | Basis | Captures Constraint? |
|--------|--------|-------|---------------------|
| Median Split | 2 | Soph only | Indirectly (via H1a) |
| Quadrant | 4 | Soph × Dis | Directly (Constrained quadrant) |

**Advantage**: Quadrant explicitly identifies constrained models rather than inferring from group-level disinhibition differences.

**Trade-off**: Smaller cell sizes (n=3 for Constrained/Unusual) limit statistical power.

---

## Visualizations

- `quadrant_scatter.png` - Scatter plot with quadrant boundaries and regression line
- `quadrant_by_provider.png` - Stacked bar chart of quadrant distribution by provider

---

## Data Artifacts

- `quadrant_classification.json` - Complete classification with residuals

---

## Limitations

1. **Small quadrant sizes**: Constrained and Unusual have only 3 models each
2. **Threshold sensitivity**: Models near medians could flip with small score changes
3. **Single condition**: Based on baseline only; cross-condition stability unknown

## Future Work

- Apply quadrant classification across all 6 conditions
- Test stability of quadrant membership
- Explore tertile-based 9-cell classification for finer granularity
