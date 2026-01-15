# Gap vs Continuum Analysis: Is There a True Sophistication Boundary?

**Generated**: 2026-01-14
**Question**: Is there a true gap between H1 clusters or is it a continuum given the tertiary transitional state evidence?

---

## Summary

**Finding**: The sophistication distribution is a **continuum with transitional characteristics**, not discrete clusters. Evidence:

1. No meaningful gap at the classification boundary (0.02 points)
2. Flippers cluster heavily in the middle tertile (80% vs 17%/29%)
3. GPQA external validation shows overlap zone where both groups coexist

---

## 1. Sophistication Distribution by Stability Class

| Class | N | Soph Range | Mean | Boundary Gap |
|-------|---|------------|------|--------------|
| Always-High | 17 | 5.94 - 7.55 | 6.86 | — |
| **Flippers** | 10 | 5.36 - 6.88 | 6.17 | 0.02 to Always-Low |
| Always-Low | 18 | 4.01 - 5.33 | 4.84 | — |

**Key**: The gap between Flipper min (5.36) and Always-Low max (5.33) is only **0.02 points** — effectively no gap.

---

## 2. Middle Tertile Concentration

Tertile boundaries (baseline): 5.23, 6.62

| Group | % in Middle Tertile |
|-------|---------------------|
| **Flippers** | **80%** (8/10) |
| Always-High | 29% (5/17) |
| Always-Low | 17% (3/18) |

Flippers are not randomly distributed — they cluster in the transitional zone.

---

## 3. Flipper Model Details

| Model | Avg Soph | Range | High Conditions | Low Conditions |
|-------|----------|-------|-----------------|----------------|
| Claude-3.7-Sonnet | 5.51 | 5.01-5.81 | 1 | 5 |
| GPT-4.1 | 5.60 | 4.01-7.10 | 2 | 4 |
| Gemini-2.0-Flash | 5.90 | 4.14-6.83 | 3 | 3 |
| Claude-4.5-Opus-Global | 6.05 | 4.70-8.08 | 3 | 3 |
| Grok-3 | 6.11 | 4.94-7.18 | 2 | 4 |
| Qwen3-32B | 6.18 | 4.87-7.41 | 3 | 3 |
| Claude-4.5-Opus-Global-Thinking | 6.26 | 4.85-8.06 | 3 | 3 |
| Claude-4-Opus | 6.37 | 5.41-7.22 | 3 | 3 |
| DeepSeek-R1 | 6.42 | 5.38-7.18 | 3 | 3 |
| Claude-4.1-Opus-Thinking | 6.55 | 5.81-7.50 | 4 | 2 |

Note: High variance (>2.0 range) in Claude-4.5-Opus-Global, GPT-4.1, Gemini-2.0-Flash suggests condition sensitivity.

---

## 4. GPQA External Validation

### Distribution

- **Range**: 30.8% - 93.2%
- **Natural gap**: 6.7pp between 50.5% and 57.2%

### GPQA Tertile × Sophistication Group

| GPQA Tertile | High-Soph | Low-Soph |
|--------------|-----------|----------|
| Low (<57.2%) | 0 | 11 |
| **Middle (57-83%)** | **8** | **5** |
| High (>83.3%) | 10 | 1 |

The middle GPQA tertile shows **mixed composition** — both sophistication groups present.

### Overlap Zone (62.1% - 84.8%)

15 models where both High and Low sophistication groups coexist:

| GPQA | Group | Model |
|------|-------|-------|
| 62.1% | High | gemini-2.0-flash |
| 66.3% | Low | gpt-4.1 |
| 67.2% | Low | claude-3.5-sonnet-v2 |
| 69.8% | Low | llama-4-maverick-17b |
| 73.0% | High | claude-4.5-haiku |
| 75.4% | High | claude-4-sonnet |
| 79.6% | Low | claude-4-opus |
| 80.9% | High | gpt-oss-120b |
| 80.9% | High | claude-4.1-opus |
| 81.1% | High | qwen3-32b |
| 82.4% | High | deepseek-r1 |
| 83.3% | High | o3 |
| 83.4% | High | claude-4.5-sonnet |
| 84.6% | High | grok-3 |
| 84.8% | Low | claude-3.7-sonnet |

**Notable**: Claude-4-Opus (Low-Soph, 79.6% GPQA) outperforms Claude-4.5-Haiku (High-Soph, 73.0% GPQA).

---

## 5. Interpretation

### Evidence FOR Continuum

1. **Minimal boundary gap** (0.02 points between Flipper/Always-Low)
2. **GPQA overlap** — 15 models in 62-85% range with mixed sophistication groups
3. **Condition sensitivity** — same models classified differently under different interventions

### Evidence FOR Transitional Class (Not Just Noise)

1. **Flippers cluster in middle** — 80% in middle tertile vs 17%/29% for stable groups
2. **GPQA gap at ~55%** — natural breakpoint exists in external benchmark
3. **Consistent flipper behavior** — same models flip repeatedly, not random

### Synthesis

The data supports a **fuzzy boundary model**:

```
Low-Soph          Transitional         High-Soph
(4.0-5.3)         (5.3-6.5)            (6.5-7.5+)
   ↑                  ↑                    ↑
 Stable            Flippers              Stable
 (n=18)            (n=10)               (n=17)
```

The median split is a useful heuristic but should be interpreted as:
- **Stable Low**: Robustly low sophistication, consistently low GPQA (<55%)
- **Transitional**: Context-dependent classification, moderate GPQA (55-80%)
- **Stable High**: Robustly high sophistication, consistently high GPQA (>80%)

---

## 6. Implications

1. **H1 is supported** — two groups exist and are separable (d = 3.09-4.25)
2. **Boundary is fuzzy** — ~22% of models (10/46) are in transitional zone
3. **External validity mixed** — GPQA shows overlap but also natural gap at ~55%
4. **Sensitivity analyses should focus on transitional models** — they drive classification uncertainty

---

## Files Referenced

- `classification_stability_analysis.json` — cross-condition stability data
- `baseline/median_split_classification.json` — baseline sophistication scores
- `external_evals/gpqa_validation_analysis.json` — GPQA correlation data

---

*Analysis supports viewing sophistication as continuous with a transitional zone, rather than discrete binary clusters.*
