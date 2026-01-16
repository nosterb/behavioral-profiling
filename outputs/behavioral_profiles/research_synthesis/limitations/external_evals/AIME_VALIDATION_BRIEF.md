# AIME 2025 External Validation Brief

**Status**: Independently Verified
**Last Updated**: 2026-01-14
**Data Artifact**: `aime_validation_analysis.json`

## Purpose

Cross-validate the H1 hypothesis against a third independent benchmark. AIME (American Invitational Mathematics Examination) 2025 measures mathematical reasoning requiring multi-step problem solving and mathematical proof — a different capability dimension than ARC-AGI's abstract pattern matching or GPQA's scientific knowledge.

## Methodology

### Data Sources

1. **AIME 2025 Leaderboard**
   - Public AIME 2025 evaluation results
   - Metric: Percentage of problems solved correctly
   - Expert human baseline: Top high school students (~40-60%)
   - Score range: 46.4% - 100%

2. **Behavior Data** (`baseline/all_models_data.csv`)
   - 45 model profiles from baseline behavior evaluations
   - Sophistication = (depth + authenticity) / 2
   - Median split into High/Low-Sophistication groups

### Matching Procedure

- Manual model name mappings for known variants
- Final matched set: **20 unique models**

### Statistical Methods

- Group comparison: Mean AIME scores by sophistication group
- Pearson correlations: AIME vs each behavior dimension
- Significance testing: t-statistics with p-values

---

## Results (Independently Verified)

### H1 Group Comparison

| Sophistication Group | n | AIME Mean | AIME SD |
|---------------------|---|-----------|---------|
| High-Sophistication | 17 | 87.3% | 9.8 |
| Low-Sophistication | 3 | 58.9% | 15.0 |

**Difference: +28.4 percentage points** (High outperforms Low by **1.48x**)

**t-statistic**: 4.32, **p** = 0.0004

**Note**: The Low-Sophistication group has only n=3 matched models due to leaderboard coverage focusing on top-performing models. Results should be interpreted with this caveat.

### Top Performers (Matched)

| Model | AIME | Sophistication | Group |
|-------|------|----------------|-------|
| Gemini 3 Pro Preview | 100.0% | 7.50 | High |
| GPT-5.2 | 100.0% | 7.26 | High |
| GPT-5.2 Pro | 100.0% | 7.34 | High |
| GPT-5 | 94.6% | 7.03 | High |
| GPT-5.1 | 94.0% | 7.26 | High |
| Grok-3 | 93.3% | 6.43 | High |

### Bottom Performers (Matched)

| Model | AIME | Sophistication | Group |
|-------|------|----------------|-------|
| GPT-4.1 | 46.4% | 5.60 | Low |
| Claude 3.7 Sonnet | 54.8% | 5.36 | Low |
| Claude 4 Sonnet | 70.5% | 6.14 | High |
| Gemini 2.0 Flash | 72.0% | 6.19 | High |
| Qwen3 32B | 72.9% | 6.38 | High |

### Correlations: AIME vs Behavioral Dimensions

| Dimension | r | p | Significant | Effect Size |
|-----------|---|---|-------------|-------------|
| **Depth** | **+0.858** | < .001 | Yes | Very Large |
| **Sophistication** | **+0.828** | < .001 | Yes | Very Large |
| **Authenticity** | **+0.763** | < .001 | Yes | Large |
| **Grandiosity** | **+0.525** | = .018 | Yes | Large |
| **Disinhibition** | **+0.464** | = .039 | Yes | Medium |
| **Aggression** | **+0.454** | = .044 | Yes | Medium |
| Tribalism | +0.340 | = .142 | No | Medium |
| Transgression | +0.339 | = .143 | No | Medium |

---

## Comparison: All Three Benchmarks

| Metric | ARC-AGI | GPQA | AIME 2025 |
|--------|---------|------|-----------|
| Matched models | 16 | 35 | 20 |
| r (Sophistication) | +0.801 | +0.884 | **+0.828** |
| r (Disinhibition) | +0.596 | +0.711 | +0.464 |
| r (Depth) | +0.821 | +0.827 | **+0.858** |
| Group difference | +47.7pp | +31.4pp | +28.4pp |
| Performance ratio | 5.8x | 1.53x | 1.48x |
| Benchmark type | Abstract reasoning | Expert scientific | Mathematical reasoning |

All three benchmarks show large correlations with sophistication (r > 0.80), despite measuring fundamentally different capabilities:
- **ARC-AGI**: Few-shot pattern abstraction, grid puzzles
- **GPQA**: Deep domain knowledge, graduate-level science
- **AIME**: Multi-step mathematical reasoning and proof

**AIME shows the strongest depth correlation** (r = 0.858), suggesting depth particularly captures mathematical reasoning ability.

---

## Interpretation

### H1 Validated (Third Replication)

The High-Sophistication group dramatically outperforms the Low-Sophistication group on AIME mathematical reasoning (+28.4 percentage points). This replicates findings from both ARC-AGI and GPQA with a third benchmark measuring yet another capability dimension.

### Convergent Validity Across Three Domains

Three independent benchmarks measuring different aspects of reasoning:
- ARC-AGI: abstract/fluid intelligence
- GPQA: crystallized/domain expertise
- AIME: mathematical/logical reasoning

All correlate r > 0.80 with our sophistication measure. This is strong evidence that:

1. **Depth and authenticity capture genuine capability**, not stylistic artifacts
2. **The behavior framework generalizes** across reasoning types
3. **Findings are robust to benchmark selection**

### H2 Supported (With Caveats)

The disinhibition composite shows moderate correlation with AIME (r = 0.464, p = .039):
- Grandiosity: r = 0.525, p = .018 (significant)
- Aggression: r = 0.454, p = .044 (significant)
- Tribalism: r = 0.340, p = .142 (not significant)
- Transgression: r = 0.339, p = .143 (not significant)

The weaker disinhibition correlation compared to GPQA (r = 0.711) may reflect:
1. Smaller sample size (n=20 vs n=35)
2. Imbalanced groups (17 High vs 3 Low)
3. Mathematical tasks may be less affected by behavioral style

### Depth as Strongest Predictor

AIME shows the highest depth correlation of all three benchmarks (r = 0.858), suggesting that the "substantive/insightful" vs "platitudes/surface" dimension particularly captures mathematical reasoning ability.

---

## Limitations

1. **Small sample size**: Only 20 matched models
2. **Group imbalance**: 17 High vs 3 Low models due to leaderboard selection bias toward top performers
3. **Selection bias**: Only models with public AIME scores
4. **Confounds**: Thinking modes and compute not fully controlled
5. **Single math benchmark**: No code or language reasoning validation

---

## Conclusion

> **AIME 2025 (r = 0.828) provides the third independent validation of H1 with a mathematical reasoning benchmark.**

Three independent external benchmarks — abstract reasoning (ARC-AGI), expert scientific knowledge (GPQA), and mathematical reasoning (AIME) — all show large correlations (r > 0.80) with our behavior-based sophistication measure.

AIME's smaller sample and group imbalance produce weaker disinhibition correlations than GPQA, but the sophistication relationship remains robust. The depth dimension shows its strongest correlation with AIME (r = 0.858), suggesting particular relevance for mathematical reasoning.

---

## Reproducibility

**Data artifact**: `aime_validation_analysis.json`

Contains complete traceable data including:
- All matched model details with scores
- Group comparison statistics
- Correlation coefficients and p-values
- Methodology documentation

**Input files:**
- AIME 2025 leaderboard data
- `baseline/all_models_data.csv` (behavioral profiles)

---

## Matched Models Reference

| AIME Model | Behavioral Model | AIME % | Soph | Disinhib | Group |
|------------|------------------|--------|------|----------|-------|
| Gemini 3 Pro | gemini-3-pro-preview | 100.0% | 7.50 | 2.31 | High |
| GPT-5.2 | gpt-5.2 | 100.0% | 7.26 | 1.63 | High |
| GPT-5.2 Pro | gpt-5.2_pro | 100.0% | 7.34 | 1.55 | High |
| GPT-5 | gpt-5 | 94.6% | 7.03 | 1.56 | High |
| GPT-5.1 | gpt-5.1 | 94.0% | 7.26 | 1.66 | High |
| Grok-3 | grok-3 | 93.3% | 6.43 | 1.62 | High |
| GPT OSS 120B High | gpt-oss-120b | 92.5% | 7.12 | 1.49 | High |
| Grok-4 | grok-4-0709 | 91.7% | 6.63 | 1.87 | High |
| DeepSeek-R1-0528 | deepseek-r1 | 87.5% | 6.26 | 1.64 | High |
| Claude Sonnet 4.5 | claude-4.5-sonnet | 87.0% | 6.77 | 1.83 | High |
| o3 | o3 | 86.4% | 7.18 | 1.55 | High |
| Gemini 2.5 Pro | gemini-2.5-pro | 83.0% | 7.55 | 1.76 | High |
| Claude Haiku 4.5 | claude-4.5-haiku | 80.7% | 6.95 | 1.67 | High |
| Claude Opus 4.1 | claude-4.1-opus | 78.0% | 6.35 | 1.63 | High |
| Claude Opus 4 | claude-4-opus | 75.5% | 5.92 | 1.65 | Low |
| Qwen3 32B | qwen3-32b | 72.9% | 6.38 | 1.59 | High |
| Gemini 2.5 Flash | gemini-2.0-flash | 72.0% | 6.19 | 1.55 | High |
| Claude Sonnet 4 | claude-4-sonnet | 70.5% | 6.14 | 1.63 | High |
| Claude 3.7 Sonnet | claude-3.7-sonnet | 54.8% | 5.36 | 1.45 | Low |
| GPT-4.1 | gpt-4.1 | 46.4% | 5.60 | 1.42 | Low |

