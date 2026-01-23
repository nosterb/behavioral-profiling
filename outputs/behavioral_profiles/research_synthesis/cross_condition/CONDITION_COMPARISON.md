# Cross-Condition Comparison

**Last Updated**: 2026-01-23 14:55
**Conditions**: 8

---

## Summary Table

| Metric | baseline | all_combined | authority | minimal_steering | naturalistic | reminder | telemetryV3 | urgency |
|--------|--------|--------|--------|--------|--------|--------|--------|--------|
| **N (Total)** | 45 | 45 | 45 | 45 | 44 | 45 | 45 | 45 |
| **High / Low** | 23 / 22 | 23 / 22 | 23 / 22 | 23 / 22 | 22 / 22 | 23 / 22 | 23 / 22 | 23 / 22 |
| **Median Soph** | 5.937 | 7.025 | 6.722 | 5.422 | 6.357 | 6.911 | 5.106 | 6.173 |
| **H1: Soph d** | 3.75 | 3.73 | 4.19 | 4.36 | 3.51 | 4.14 | 3.67 | 4.25 |
| **H1a: d (disinhib)** | 2.13 | 2.30 | 1.84 | 2.32 | 2.09 | 1.65 | 1.09 | 1.77 |
| **H1a: p-value** | < .001 | < .001 | < .001 | < .001 | < .001 | < .001 | < .001 | < .001 |
| **H2: r** | 0.778 | 0.815 | 0.770 | 0.854 | 0.841 | 0.720 | 0.625 | 0.743 |
| |  |  |  |  |  |  |  | |
| **Dimension d:** |  |  |  |  |  |  |  | |
| *Transgression* | 1.81 | 2.06 | 1.97 | 1.89 | 1.28 | 2.28 | 1.07 | 1.80 |
| *Aggression* | 2.17 | 2.25 | 1.79 | 2.13 | 2.08 | 1.73 | 0.80 | 1.81 |
| *Tribalism* | 1.26 | 1.66 | 0.98 | 1.28 | 1.29 | 0.92 | 0.60 | 1.44 |
| *Grandiosity* | 1.71 | 1.62 | 0.96 | 0.96 | 1.83 | 0.70 | 1.21 | 1.25 |

---

## Key Comparative Findings

**All_combined vs Baseline**:
  - H2 correlation: 0.815 (stronger by 0.037)
  - H1a effect size: d=2.30 (larger by 0.16)

**Authority vs Baseline**:
  - H2 correlation: 0.770 (weaker by 0.008)
  - H1a effect size: d=1.84 (smaller by 0.29)

**Minimal_steering vs Baseline**:
  - H2 correlation: 0.854 (stronger by 0.076)
  - H1a effect size: d=2.32 (larger by 0.19)

**Naturalistic vs Baseline**:
  - H2 correlation: 0.841 (stronger by 0.062)
  - H1a effect size: d=2.09 (smaller by 0.04)

**Reminder vs Baseline**:
  - H2 correlation: 0.720 (weaker by 0.058)
  - H1a effect size: d=1.65 (smaller by 0.48)

**Telemetryv3 vs Baseline**:
  - H2 correlation: 0.625 (weaker by 0.154)
  - H1a effect size: d=1.09 (smaller by 1.04)

**Urgency vs Baseline**:
  - H2 correlation: 0.743 (weaker by 0.035)
  - H1a effect size: d=1.77 (smaller by 0.37)


---

## Interpretation Notes

### H1 (Group Existence) Patterns
- Sophistication separation d > 2.0 indicates well-separated groups
- This validates the median split as creating meaningful distinct groups

### H1a (Group Difference) Patterns
- Cohen's d > 0.8 indicates large effect (high vs low sophistication groups differ substantially in disinhibition)
- Larger d suggests stronger group separation in disinhibition

### H2 (Correlation) Patterns
- r > 0.5 indicates large correlation (sophistication predicts disinhibition)
- Changes in r across conditions suggest intervention effects on this relationship

### Cross-Condition Observations

*Add observations here as patterns emerge across conditions.*

---

## Methodology

- **Classification**: Median split on sophistication composite (depth + authenticity / 2)
- **H1 Test**: Cohen's d for sophistication separation between high and low groups
- **H1a Test**: Independent samples t-test comparing disinhibition between high vs low sophistication groups
- **H2 Test**: Pearson correlation between sophistication and disinhibition composite
- **Effect Sizes**: Cohen's d for group differences, Pearson r for correlations

---

## Files Referenced

- `../baseline/median_split_classification.json`
- `../baseline/RESEARCH_BRIEF.md`
- `../all_combined/median_split_classification.json`
- `../all_combined/RESEARCH_BRIEF.md`
- `../authority/median_split_classification.json`
- `../authority/RESEARCH_BRIEF.md`
- `../minimal_steering/median_split_classification.json`
- `../minimal_steering/RESEARCH_BRIEF.md`
- `../naturalistic/median_split_classification.json`
- `../naturalistic/RESEARCH_BRIEF.md`
- `../reminder/median_split_classification.json`
- `../reminder/RESEARCH_BRIEF.md`
- `../telemetryV3/median_split_classification.json`
- `../telemetryV3/RESEARCH_BRIEF.md`
- `../urgency/median_split_classification.json`
- `../urgency/RESEARCH_BRIEF.md`
