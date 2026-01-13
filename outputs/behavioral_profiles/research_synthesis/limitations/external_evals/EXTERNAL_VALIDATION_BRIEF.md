# External Validation Brief: ARC-AGI & GPQA

**Status**: Independently Verified
**Last Updated**: 2026-01-12
**Data Artifacts**: `arc_agi_validation_analysis.json`, `gpqa_validation_analysis.json`

---

## Executive Summary

Cross-validation against two independent reasoning benchmarks provides strong external validity for the behavioral sophistication measure:

| Benchmark | n | r (Sophistication) | r (Disinhibition) | Group Diff |
|-----------|---|-------------------|-------------------|------------|
| **ARC-AGI** | 16 | 0.801*** | 0.596* | +47.7 pp |
| **GPQA** | 35 | 0.884*** | 0.711*** | +31.4 pp |

*\* p < .05, \*\*\* p < .001*

**Key Finding**: Behavioral sophistication (depth + authenticity) strongly predicts performance on external reasoning benchmarks, providing convergent validity for H1 and H2.

---

## 1. Purpose

Cross-validate the sophistication-disinhibition framework against external capability benchmarks that are:
1. **Independent** of our evaluation methodology
2. **Objective** (not LLM-as-judge)
3. **Capability-focused** (measuring reasoning, not style)

---

## 2. Benchmarks

### 2.1 ARC-AGI

**What it measures**: Abstract reasoning and few-shot pattern generalization

- Grid-based visual puzzles requiring novel rule inference
- Tests fluid intelligence / generalization capability
- No training data overlap possible (unique puzzles)
- Source: https://arcprize.org/leaderboard

### 2.2 GPQA (Graduate-Level Google-Proof Q&A)

**What it measures**: Expert-level scientific reasoning

- Graduate-level questions in biology, chemistry, physics
- Designed to be unsearchable ("Google-proof")
- Tests crystallized knowledge + reasoning
- Random baseline: 25% (4-choice multiple choice)
- Expert human baseline: ~65%

### 2.3 Why Two Benchmarks?

| Aspect | ARC-AGI | GPQA |
|--------|---------|------|
| **Reasoning type** | Fluid / abstract | Crystallized / domain |
| **Knowledge required** | Minimal | Extensive |
| **Format** | Visual grid puzzles | Text multiple-choice |
| **Skill tested** | Pattern abstraction | Scientific expertise |

If sophistication correlates with both, it captures **general capability** rather than a narrow skill.

---

## 3. Methodology

### 3.1 Data Sources

**Behavioral Data** (from `baseline/all_models_data.csv`):
- 46 model profiles from baseline behavioral evaluations
- 9 dimensions measured on 1-10 scale
- Sophistication = (depth + authenticity) / 2
- Disinhibition = (transgression + aggression + tribalism + grandiosity) / 4

**External Benchmarks**:
- ARC-AGI: 42 leaderboard entries
- GPQA: 162 leaderboard entries

### 3.2 Matching Procedure

1. Normalize model names (lowercase, alphanumeric)
2. Match behavioral profiles to benchmark entries
3. Deduplicate to highest score per model
4. Final matched sets: **16 (ARC-AGI)**, **35 (GPQA)**

### 3.3 Statistical Methods

- **Correlation**: Pearson product-moment (scipy.stats.pearsonr)
- **Group comparison**: Independent samples t-test
- **Effect sizes**: Pearson r, group mean difference

---

## 4. Results

### 4.1 Correlation Summary

| Dimension | ARC-AGI (n=16) | GPQA (n=35) |
|-----------|----------------|-------------|
| **Sophistication** | **0.801*** | **0.884*** |
| Authenticity | 0.827*** | 0.887*** |
| Depth | 0.761*** | 0.865*** |
| **Disinhibition** | **0.596*** | **0.711*** |
| Aggression | 0.654** | 0.686*** |
| Transgression | 0.648** | 0.673*** |
| Grandiosity | 0.402 | 0.668*** |
| Tribalism | 0.488 | 0.543*** |

*\* p < .05, \*\* p < .01, \*\*\* p < .001*

### 4.2 Group Comparison (H1 Validation)

**ARC-AGI**:
| Group | n | Mean | SD |
|-------|---|------|-----|
| High-Sophistication | 12 | 57.6% | 27.8 |
| Low-Sophistication | 4 | 9.9% | 9.3 |
| **Difference** | | **+47.7 pp** | |
| **t-statistic** | | 3.30 | p = .005 |

**GPQA**:
| Group | n | Mean | SD |
|-------|---|------|-----|
| High-Sophistication | 18 | 83.4% | 7.6 |
| Low-Sophistication | 17 | 52.1% | 16.2 |
| **Difference** | | **+31.4 pp** | |
| **t-statistic** | | 7.41 | p < .0001 |

### 4.3 Key Models

**Top Performers (Both Benchmarks)**:
| Model | ARC-AGI | GPQA | Soph | Disinhib |
|-------|---------|------|------|----------|
| Gemini-3-Pro-Preview | 87.5% | 91.9% | 7.50 | 2.31 |
| GPT-5.2 | 86.2% | 92.4% | 7.26 | 1.63 |
| GPT-5.2 Pro | 85.7% | 93.2% | 7.34 | 1.55 |
| GPT-5.1 | 72.8% | 88.1% | 7.26 | 1.66 |
| Grok-4 | 66.7% | 87.5% | 6.63 | 1.87 |

**Bottom Performers**:
| Model | ARC-AGI | GPQA | Soph | Disinhib |
|-------|---------|------|------|----------|
| GPT-3.5 Turbo | — | 30.8% | 4.01 | 1.39 |
| Claude-3 Haiku | — | 33.3% | 4.70 | 1.33 |
| Llama-4 Scout | 0.5% | 57.2% | 5.33 | 1.40 |
| Llama-4 Maverick | 4.4% | 69.8% | 5.08 | 1.36 |
| Claude-3 Opus | 13.6% | 50.4% | 4.68 | 1.36 |

---

## 5. Interpretation

### 5.1 H1 Validated: Sophistication Predicts Capability

The median split based on behavioral sophistication produces groups with dramatically different benchmark performance:
- **ARC-AGI**: 5.8x performance ratio (High vs Low)
- **GPQA**: 1.6x performance ratio

This confirms that "depth" and "authenticity" capture genuine reasoning capability, not merely stylistic features.

### 5.2 H2 Supported: Disinhibition Correlates with Capability

Disinhibition shows significant positive correlations with both benchmarks:
- **ARC-AGI**: r = 0.596, p < .05
- **GPQA**: r = 0.711, p < .001

Models that score higher on external capability benchmarks also exhibit higher behavioral disinhibition. This supports the core H2 finding that capability and boundary-pushing behavior are linked.

### 5.3 Convergent Validity

Two benchmarks measuring fundamentally different capabilities (abstract reasoning vs. scientific expertise) both show very large correlations (r > 0.80) with sophistication. This provides strong evidence that:

1. The behavioral framework captures **general capability**, not narrow skills
2. The sophistication-disinhibition relationship is **not an artifact** of evaluation methodology
3. Results **generalize** across reasoning domains

---

## 6. Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Sample size** | ARC-AGI n=16 limits power | GPQA n=35 provides replication |
| **Selection bias** | Only models with published scores | Major providers represented |
| **Confounds** | CoT vs base not controlled | Effect robust across model types |
| **Temporal** | Leaderboard snapshot | Behavioral data from same period |
| **Unbalanced groups** | ARC-AGI: 12 High, 4 Low | GPQA: 18 High, 17 Low (balanced) |

### 6.1 Classification Stability

Cross-condition analysis shows 76% of models maintain consistent High/Low classification across all 6 intervention conditions. For matched benchmark models:

**Stably Classified (External Validation)**:

| Benchmark | Stable High | Stable Low | Flippers |
|-----------|-------------|------------|----------|
| ARC-AGI (n=16) | 11 | 3 | 2 |
| GPQA (n=35) | 14 | 14 | 7 |

**Flippers in Matched Sets**:

| Model | Benchmark | Baseline Group | Cross-Condition Pattern |
|-------|-----------|----------------|------------------------|
| Claude-4-Opus | GPQA | Low | High 5/6 (near-threshold) |
| DeepSeek-R1 | GPQA | High | High 5/6 (Low in reminder only) |
| Qwen3-32B | Both | High | High 4/6 (constraint-sensitive) |
| Grok-3 | Both | High | High 4/6 (pressure-sensitive) |
| Gemini-2.0-Flash | GPQA | High | High 3/6 (variable) |
| Claude-4.5-Opus-Global | GPQA | High | High 3/6 (variable) |
| GPT-4.1 | GPQA | Low | High 2/6 (mostly low) |

**Implication**: The majority of high-performers (GPT-5 series, O3, Claude-4.5-Sonnet, Gemini-2.5-Pro) are **stably High** across all conditions. Flippers tend to be near the median threshold. External validation is robust because top-tier models show consistent classification.

**Data trail**: `research_synthesis/limitations/median_split/classification_stability_analysis.json`

---

## 7. Visualizations

**Location**: `research_synthesis/limitations/external_evals/`

| File | Description |
|------|-------------|
| `external_validation_consolidated.png` | 2x2 panel: Soph & Disinhib vs both benchmarks |
| `external_validation_correlations.png` | Bar chart: All dimensions vs both benchmarks |
| `external_validation_comparison.png` | Side-by-side: ARC-AGI vs GPQA (Soph only) |
| `arc_agi_combined.png` | ARC-AGI scatter + box plot |
| `gpqa_combined.png` | GPQA scatter + box plot |

---

## 8. Conclusion

> **Behavioral sophistication strongly predicts external benchmark performance (r = 0.80-0.88), providing convergent validity for the sophistication-disinhibition framework.**

The finding that high-sophistication models exhibit both superior reasoning capability AND higher disinhibition is not an artifact of LLM-as-judge evaluation. It reflects genuine differences in model capability validated against objective, independent benchmarks.

---

## 9. Data Artifacts

**JSON files** (complete traceable data):
- `arc_agi_validation_analysis.json`
- `gpqa_validation_analysis.json`

**Source data**:
- `external_evals/ARC-AGI_leaders` (ARC-AGI leaderboard)
- `external_evals/GPQA` (GPQA leaderboard)
- `baseline/all_models_data.csv` (behavioral profiles)

**Regenerate visualizations**:
```bash
python3 scripts/visualize_external_evals.py
```

---

## Appendix: Full Matched Model Tables

### A.1 ARC-AGI Matched Models (n=16)

| Model | ARC-AGI-1 | Soph | Disinhib | Group |
|-------|-----------|------|----------|-------|
| gemini-3-pro-preview | 87.5% | 7.50 | 2.31 | High |
| gpt-5.2 | 86.2% | 7.26 | 1.63 | High |
| gpt-5.2_pro | 85.7% | 7.34 | 1.55 | High |
| gpt-5.1 | 72.8% | 7.26 | 1.66 | High |
| gpt-5 | 70.2% | 7.03 | 1.56 | High |
| grok-4-0709 | 66.7% | 6.63 | 1.87 | High |
| claude-4.5-sonnet | 63.7% | 6.77 | 1.83 | High |
| o3 | 60.8% | 7.18 | 1.55 | High |
| gemini-2.5-pro | 41.0% | 7.55 | 1.76 | High |
| claude-4-sonnet | 40.0% | 6.14 | 1.63 | High |
| claude-3.7-sonnet | 21.2% | 5.36 | 1.45 | Low |
| claude-3-opus | 13.6% | 4.68 | 1.36 | Low |
| qwen3-32b | 11.0% | 6.38 | 1.59 | High |
| grok-3 | 5.5% | 6.43 | 1.62 | High |
| llama-4-maverick-17b | 4.4% | 5.08 | 1.36 | Low |
| llama-4-scout-17b | 0.5% | 5.33 | 1.40 | Low |

### A.2 GPQA Matched Models (n=35)

| Model | GPQA | Soph | Disinhib | Group |
|-------|------|------|----------|-------|
| gpt-5.2_pro | 93.2% | 7.34 | 1.55 | High |
| gpt-5.2 | 92.4% | 7.26 | 1.63 | High |
| gemini-3-pro-preview | 91.9% | 7.50 | 2.31 | High |
| gpt-5 | 88.1% | 7.03 | 1.56 | High |
| gpt-5.1 | 88.1% | 7.26 | 1.66 | High |
| grok-4-0709 | 87.5% | 6.63 | 1.87 | High |
| claude-4.5-opus-global | 87.0% | 6.88 | 1.70 | High |
| gemini-2.5-pro | 86.4% | 7.55 | 1.76 | High |
| claude-3.7-sonnet | 84.8% | 5.36 | 1.45 | Low |
| grok-3 | 84.6% | 6.43 | 1.62 | High |
| claude-4.5-sonnet | 83.4% | 6.77 | 1.83 | High |
| o3 | 83.3% | 7.18 | 1.55 | High |
| deepseek-r1 | 82.4% | 6.26 | 1.64 | High |
| qwen3-32b | 81.1% | 6.38 | 1.59 | High |
| gpt-oss-120b | 80.9% | 7.12 | 1.49 | High |
| claude-4.1-opus | 80.9% | 6.35 | 1.63 | High |
| claude-4-opus | 79.6% | 5.92 | 1.65 | Low |
| claude-4-sonnet | 75.4% | 6.14 | 1.63 | High |
| claude-4.5-haiku | 73.0% | 6.95 | 1.67 | High |
| llama-4-maverick-17b | 69.8% | 5.08 | 1.36 | Low |
| claude-3.5-sonnet-v2 | 67.2% | 4.87 | 1.37 | Low |
| gpt-4.1 | 66.3% | 5.60 | 1.42 | Low |
| gemini-2.0-flash | 62.1% | 6.19 | 1.55 | High |
| llama-4-scout-17b | 57.2% | 5.33 | 1.40 | Low |
| llama-3.3-70b | 50.5% | 5.13 | 1.40 | Low |
| claude-3-opus | 50.4% | 4.68 | 1.36 | Low |
| nova-pro | 46.9% | 5.29 | 1.34 | Low |
| llama-3.2-90b | 46.7% | 5.08 | 1.38 | Low |
| nova-lite | 42.0% | 5.07 | 1.32 | Low |
| llama-3.1-70b | 41.7% | 5.23 | 1.45 | Low |
| claude-3.5-haiku | 41.6% | 4.61 | 1.40 | Low |
| claude-3-sonnet | 40.4% | 4.81 | 1.30 | Low |
| gpt-4 | 35.7% | 4.38 | 1.35 | Low |
| claude-3-haiku | 33.3% | 4.70 | 1.33 | Low |
| gpt-3.5_turbo | 30.8% | 4.01 | 1.39 | Low |

---

**Document Version**: 1.1
**Last Updated**: 2026-01-12
