# Cross-Condition Comparison

**Last Updated**: 2026-01-13 20:15
**Conditions**: 6

---

## Summary Table

| Metric | baseline | authority | minimal_steering | reminder | telemetryV3 | urgency |
|--------|--------|--------|--------|--------|--------|--------|
| **N (Total)** | 45 | 45 | 46 | 46 | 46 | 45 |
| **High / Low** | 23 / 22 | 23 / 22 | 23 / 23 | 23 / 23 | 23 / 23 | 23 / 22 |
| **Median Soph** | 5.937 | 6.722 | 5.172 | 6.833 | 5.016 | 6.173 |
| **H1: Soph d** | 3.75 | 4.19 | 3.96 | 3.87 | 3.09 | 4.25 |
| **H1a: d (disinhib)** | 2.13 | 1.86 | 1.83 | 1.51 | 1.14 | 1.77 |
| **H1a: p-value** | < .001 | < .001 | < .001 | < .001 | < .001 | < .001 |
| **H2: r** | 0.702 | 0.588 | 0.509 | 0.458 | 0.724 | 0.563 |
| |  |  |  |  |  | |
| **Dimension d:** |  |  |  |  |  | |
| *Transgression* | 1.81 | 1.97 | 1.56 | 2.05 | 1.12 | 1.80 |
| *Aggression* | 2.17 | 1.79 | 1.39 | 1.41 | 0.84 | 1.81 |
| *Tribalism* | 1.26 | 1.07 | 0.68 | 0.92 | 0.65 | 1.44 |
| *Grandiosity* | 1.71 | 0.96 | 0.84 | 0.64 | 1.20 | 1.25 |

---

## Key Comparative Findings

**Authority vs Baseline**:
  - H2 correlation: 0.588 (weaker by 0.114)
  - H1a effect size: d=1.86 (smaller by 0.27)

**Minimal_steering vs Baseline**:
  - H2 correlation: 0.509 (weaker by 0.193)
  - H1a effect size: d=1.83 (smaller by 0.31)

**Reminder vs Baseline**:
  - H2 correlation: 0.458 (weaker by 0.244)
  - H1a effect size: d=1.51 (smaller by 0.62)

**Telemetryv3 vs Baseline**:
  - H2 correlation: 0.724 (stronger by 0.022)
  - H1a effect size: d=1.14 (smaller by 0.99)

**Urgency vs Baseline**:
  - H2 correlation: 0.563 (weaker by 0.139)
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
- `../authority/median_split_classification.json`
- `../authority/RESEARCH_BRIEF.md`
- `../minimal_steering/median_split_classification.json`
- `../minimal_steering/RESEARCH_BRIEF.md`
- `../reminder/median_split_classification.json`
- `../reminder/RESEARCH_BRIEF.md`
- `../telemetryV3/median_split_classification.json`
- `../telemetryV3/RESEARCH_BRIEF.md`
- `../urgency/median_split_classification.json`
- `../urgency/RESEARCH_BRIEF.md`
