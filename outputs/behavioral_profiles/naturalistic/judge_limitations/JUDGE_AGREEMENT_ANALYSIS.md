# Judge Agreement Analysis: Naturalistic

**Generated**: 2026-01-19
**Condition**: naturalistic
**Purpose**: Validate inter-rater reliability of the 3-judge evaluation panel

---

## Executive Summary

The 3-judge panel for the naturalistic condition demonstrates **moderate reliability** across behavioral dimensions:

- **Overall ICC(3)**: 0.621 (Moderate)
- **Best agreement**: Depth (ICC = 0.826, Good)
- **Worst agreement**: Grandiosity (ICC = 0.241, Poor)
- **Within-1 point agreement**: 60.9%

**Conclusion**: Judge scores are moderately reliable for behavioral profiling. The averaging of 3 judges produces reasonably stable measurements.

---

## Data Summary

| Metric | Value |
|--------|-------|
| Total evaluations scanned | 630 |
| Evaluations with 3 valid judges | 630 |
| Judge panel size | 3 |
| Dimensions scored | 9 |
| Judges | Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B |

---

## Inter-Judge Agreement by Dimension

| Dimension | N | Mean r | ICC(1) | ICC(3) | MAD | Exact | Within-1 | Quality |
|-----------|---|--------|--------|--------|-----|-------|----------|---------|
| **depth** | 630 | 0.715 | 0.613 | **0.826** | 1.10 | 12.1% | 51.7% | Good |
| **warmth** | 630 | 0.709 | 0.598 | **0.817** | 1.25 | 15.2% | 48.9% | Good |
| **hedging** | 630 | 0.705 | 0.574 | **0.802** | 1.59 | 3.0% | 22.5% | Good |
| **authenticity** | 630 | 0.646 | 0.560 | **0.793** | 1.28 | 5.7% | 34.3% | Good |
| **transgression** | 630 | 0.420 | 0.387 | **0.655** | 0.36 | 54.1% | 93.0% | Moderate |
| **formality** | 630 | 0.515 | 0.336 | **0.603** | 1.41 | 5.4% | 37.6% | Moderate |
| **tribalism** | 622 | 0.269 | 0.203 | **0.433** | 0.15 | 86.5% | 93.9% | Poor |
| **aggression** | 630 | 0.345 | 0.194 | **0.419** | 0.40 | 42.7% | 97.9% | Poor |
| **grandiosity** | 630 | 0.217 | 0.096 | **0.241** | 0.85 | 7.3% | 68.1% | Poor |
| **OVERALL** | — | 0.504 | 0.396 | **0.621** | 0.93 | 25.8% | 60.9% | Moderate |

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
| > 0.90 | **Excellent** | (none) |
| 0.75-0.90 | **Good** | warmth, hedging, depth, authenticity |
| 0.50-0.75 | **Moderate** | formality, transgression |
| < 0.50 | **Poor** | aggression, grandiosity, tribalism |

*Reference: Koo & Li (2016). A Guideline of Selecting and Reporting Intraclass Correlation Coefficients for Reliability Research.*

---

## Dimension-Specific Observations

### High Agreement Dimensions

**Depth** (ICC = 0.826)
- 51.7% within-1 agreement
- Mean absolute difference: 1.10

**Warmth** (ICC = 0.817)
- 48.9% within-1 agreement
- Mean absolute difference: 1.25

**Hedging** (ICC = 0.802)
- 22.5% within-1 agreement
- Mean absolute difference: 1.59

### Lower Agreement Dimensions

**Tribalism** (ICC = 0.433)
- 93.9% within-1 agreement
- Mean absolute difference: 0.15
- May benefit from more specific rubric anchors

**Aggression** (ICC = 0.419)
- 97.9% within-1 agreement
- Mean absolute difference: 0.40
- May benefit from more specific rubric anchors

**Grandiosity** (ICC = 0.241)
- 68.1% within-1 agreement
- Mean absolute difference: 0.85
- May benefit from more specific rubric anchors

---

## Implications for Validity

### Strengths

1. **Adequate composite reliability**: ICC(3) = 0.621 for averaged scores
2. **Disinhibition dimensions**: aggression (0.419), transgression (0.655), tribalism (0.433), grandiosity (0.241)
3. **Sophistication dimensions**: depth (0.826), authenticity (0.793)
4. **Within-1 agreement**: 60.9% of ratings differ by ≤1 point

### Limitations

1. **Single judge unreliable**: ICC(1) = 0.396; 3-judge average essential
2. **Exact agreement variable**: Ranges from 3.0% to 86.5%

### Recommendations

1. **Continue using 3-judge panels**: Single judge reliability is insufficient
2. **Report dimension-specific reliability**: Different dimensions have different precision
3. **Consider rubric refinement**: Lower-agreement dimensions could benefit from clearer anchors

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

- Job files in `outputs/single_prompt_jobs/job_naturalistic_*/*.json`
- Judge scores from `judge_evaluation.evaluations[].pass1_judges[].extracted_json.scores`
- Only evaluations with exactly 3 valid judge scores included

---

## Data Provenance & Audit Trail

### Source Files
| File | Purpose |
|------|---------|
| `outputs/single_prompt_jobs/job_naturalistic_*/*.json` | Raw job outputs with judge evaluations |

### Audit File
| File | Description |
|------|-------------|
| `judge_agreement_analysis.json` | Complete ICC and agreement statistics |

### Methodology
- **Statistical tests**: ICC(2,k), Pearson correlation, Mean Absolute Deviation
- **Judge panel**: 3 judges per evaluation (Claude-4.5-Sonnet, DeepSeek-R1, Llama-4-Maverick-17B)
- **Model**: Two-way random effects, absolute agreement, average of k=3 raters

### Reproducibility
To regenerate:
```bash
python3 scripts/analyze_judge_agreement.py --condition naturalistic
```

### Data Quality
- **N**: 630 evaluations with 3 valid judges
- **Dimensions**: 9 behavioral dimensions
- **Reliability**: Overall ICC(3) = 0.621 (Moderate)

---

*This analysis supports methodological validity for the behavioral profiling research initiative.*
