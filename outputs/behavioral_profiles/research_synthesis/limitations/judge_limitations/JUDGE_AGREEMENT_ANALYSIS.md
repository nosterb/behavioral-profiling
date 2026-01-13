# Judge Agreement Analysis

**Generated**: 2026-01-11
**Purpose**: Validate inter-rater reliability of the 3-judge evaluation panel

---

## Executive Summary

The 3-judge panel demonstrates **good to excellent reliability** across all behavioral dimensions:

- **Overall ICC(3)**: 0.843 (Good)
- **Best agreement**: Aggression (ICC = 0.932, Excellent)
- **Worst agreement**: Formality (ICC = 0.724, Moderate)
- **Within-1 point agreement**: 76.0%

**Conclusion**: Judge scores are sufficiently reliable for behavioral profiling. The averaging of 3 judges produces stable measurements (ICC > 0.80 for 8 of 9 dimensions).

---

## Data Summary

| Metric | Value |
|--------|-------|
| Total evaluations scanned | 10,570 |
| Evaluations with 3 valid judges | 10,565 |
| Judge panel size | 3 |
| Dimensions scored | 9 |

---

## Inter-Judge Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Exact | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|-------|----------|---------|
| **aggression** | 10,565 | 0.835 | 0.821 | **0.932** | 0.43 | 66.4% | 94.1% | Excellent |
| **hedging** | 10,565 | 0.816 | 0.743 | **0.897** | 1.41 | 25.1% | 61.3% | Good |
| **warmth** | 10,565 | 0.786 | 0.722 | **0.886** | 1.20 | 30.7% | 70.2% | Good |
| **tribalism** | 10,420 | 0.662 | 0.658 | **0.852** | 0.20 | 87.8% | 95.5% | Good |
| **grandiosity** | 10,565 | 0.686 | 0.618 | **0.829** | 0.84 | 38.3% | 83.7% | Good |
| **transgression** | 10,562 | 0.648 | 0.614 | **0.827** | 0.67 | 52.2% | 89.3% | Good |
| **authenticity** | 10,554 | 0.693 | 0.612 | **0.825** | 1.37 | 23.5% | 61.4% | Good |
| **depth** | 10,563 | 0.751 | 0.592 | **0.813** | 1.38 | 24.1% | 61.9% | Good |
| **formality** | 10,565 | 0.632 | 0.466 | **0.724** | 1.33 | 27.4% | 66.9% | Moderate |
| **OVERALL** | — | 0.723 | 0.649 | **0.843** | 0.98 | 41.7% | 76.0% | Good |

### Metric Definitions

| Metric | Description |
|--------|-------------|
| **Mean r** | Average pairwise Pearson correlation between judges |
| **ICC(1)** | Intraclass correlation for single rater (reliability of one judge) |
| **ICC(3)** | Intraclass correlation for average of 3 raters (reliability of final score) |
| **MAD** | Mean absolute difference between judge pairs (on 1-10 scale) |
| **Exact** | Percentage of cases where all judges gave identical scores |
| **Within-1** | Percentage of cases where judges differed by ≤1 point |

---

## ICC Interpretation Guide

| ICC Value | Interpretation | Dimensions in Range |
|-----------|----------------|---------------------|
| > 0.90 | **Excellent** | aggression |
| 0.75-0.90 | **Good** | warmth, hedging, transgression, grandiosity, tribalism, depth, authenticity |
| 0.50-0.75 | **Moderate** | formality |
| < 0.50 | **Poor** | (none) |

*Reference: Koo & Li (2016). A Guideline of Selecting and Reporting Intraclass Correlation Coefficients for Reliability Research.*

---

## Dimension-Specific Observations

### High Agreement Dimensions

**Aggression** (ICC = 0.932)
- Highest agreement across all dimensions
- 94.1% within-1 agreement
- Low variance in scores (most responses score 1-2)
- Clear behavioral markers (combative language, attacking tone)

**Tribalism** (ICC = 0.852)
- 87.8% exact agreement (highest)
- Very low MAD (0.20)
- Most responses show minimal tribalism (score ~1)
- Easy to identify when present (us-vs-them framing)

**Hedging** (ICC = 0.897)
- Strong agreement despite wider score distribution
- Qualifiers and uncertainty markers are concrete and countable

### Lower Agreement Dimensions

**Formality** (ICC = 0.724)
- Only "moderate" reliability dimension
- Higher MAD (1.33)
- Subjective judgment of "professional" vs "casual"
- May benefit from more specific rubric anchors

**Depth** (ICC = 0.813)
- Good reliability but lower exact agreement (24.1%)
- "Substantive insight" is inherently subjective
- Judges may have different thresholds for "deep" vs "surface"

**Authenticity** (ICC = 0.825)
- Similar pattern to depth
- "Genuinely distinctive" requires comparative judgment
- Higher variance expected for abstract quality

---

## Implications for Validity

### Strengths

1. **Reliable composite scores**: ICC(3) > 0.80 for 8/9 dimensions means averaged scores are stable
2. **Disinhibition dimensions show excellent agreement**: Aggression (0.932), transgression (0.827), tribalism (0.852), grandiosity (0.829)
3. **Sophistication dimensions adequate**: Depth (0.813), authenticity (0.825) both "Good"
4. **High within-1 agreement**: 76% of ratings differ by ≤1 point

### Limitations

1. **Formality shows moderate reliability**: Results involving formality should be interpreted with more caution
2. **Exact agreement is low for some dimensions**: Only 24-30% for depth, authenticity, hedging, formality
3. **Single judge unreliable**: ICC(1) ranges 0.47-0.82; 3-judge average essential

### Recommendations

1. **Continue using 3-judge panels**: Single judge reliability is insufficient
2. **Weight formality findings carefully**: Moderate ICC suggests measurement noise
3. **Report dimension-specific reliability**: Different dimensions have different precision
4. **Consider rubric refinement**: Formality, depth, authenticity could benefit from clearer anchors

---

## Technical Details

### ICC Calculation Method

Used ICC(2,k) - two-way random effects model, absolute agreement, average of k=3 raters:

```
ICC(2,k) = (MS_R - MS_E) / (MS_R + (MS_C - MS_E)/n)

Where:
  MS_R = Mean square for rows (between-subjects)
  MS_C = Mean square for columns (between-raters)
  MS_E = Mean square for error (residual)
  n = number of subjects
```

### Data Sources

- All job files in `outputs/single_prompt_jobs/`
- Judge scores from `judge_evaluation.evaluations[].pass1_judges[].extracted_json.scores`
- Only evaluations with exactly 3 valid judge scores included

---

## File References

| File | Description |
|------|-------------|
| `judge_agreement_analysis.json` | Machine-readable results |
| `JUDGE_AGREEMENT_ANALYSIS.md` | This document |

---

*This analysis supports methodological validity for the behavioral profiling research initiative.*
