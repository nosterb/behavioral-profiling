# Statistical Quality Control Framework

**Version**: 1.0
**Last Updated**: 2026-01-10
**Applies To**: All phases of research synthesis (H1/H2, H3, Combined, Main Brief)

---

## Purpose

This document establishes statistical methods, quality control procedures, and audit protocols for all analyses in the behavioral profiling research initiative. It consolidates validated practices from Phase 1 (H1/H2 replication) and extends them to future phases.

---

## Table of Contents

1. [Statistical Methods Standards](#statistical-methods-standards)
2. [Quality Control Procedures](#quality-control-procedures)
3. [Audit Protocols](#audit-protocols)
4. [Validation Checklists](#validation-checklists)
5. [Data Integrity Requirements](#data-integrity-requirements)
6. [Reporting Standards](#reporting-standards)
7. [Reproducibility Requirements](#reproducibility-requirements)
8. [Troubleshooting Decision Trees](#troubleshooting-decision-trees)

---

## Statistical Methods Standards

### Core Principles

1. **Transparency**: All methods fully documented with code and parameters
2. **Reproducibility**: Deterministic analyses with fixed random seeds where needed
3. **Appropriate Testing**: Match statistical test to research question and data characteristics
4. **Effect Sizes**: Always report effect sizes alongside p-values
5. **Multiple Comparisons**: Correct when testing multiple hypotheses
6. **Assumptions**: Verify and document assumption checks
7. **Sensitivity**: Test robustness of findings to methodological choices

### Phase 1: Per-Condition H1/H2 Analysis

#### H1 Group Comparison

**Method**: Independent samples t-test with pooled variance

**Assumptions**:
- Independence: Models evaluated independently ✓
- Normality: Check with Shapiro-Wilk test (p > .05 acceptable for n ≥ 20)
- Homogeneity of variance: Check with Levene's test
  - Acceptable: Variance ratio ≤ 4:1
  - Borderline: Variance ratio 4:1 to 10:1 (document, consider Welch's t-test)
  - Unacceptable: Variance ratio > 10:1 (use Welch's t-test)

**Effect Size**: Cohen's d with pooled standard deviation
```
d = (M_high - M_low) / SD_pooled
SD_pooled = sqrt(((n1-1)*SD1^2 + (n2-1)*SD2^2) / (n1+n2-2))
```

**Interpretation Thresholds**:
- Negligible: |d| < 0.2
- Small: 0.2 ≤ |d| < 0.5
- Medium: 0.5 ≤ |d| < 0.8
- Large: |d| ≥ 0.8

**Quality Checks**:
- ✅ Group sizes reasonably balanced (difference ≤ 5 models)
- ✅ Sophistication separation strong (d ≥ 1.5 for median split validity)
- ✅ No NaN or Inf values in results
- ✅ P-values in valid range [0, 1]
- ✅ Degrees of freedom correct: df = n1 + n2 - 2

#### H2 Correlation Analysis

**Method**: Pearson product-moment correlation

**Assumptions**:
- Independence: Models evaluated independently ✓
- Linearity: Visual inspection of scatter plot
- Bivariate normality: Check both variables for normality
- Homoscedasticity: Check scatter plot for constant variance

**Effect Size**: Pearson's r
```
r = cov(X,Y) / (SD_X * SD_Y)
```

**Interpretation Thresholds**:
- Negligible: |r| < 0.10
- Small: 0.10 ≤ |r| < 0.30
- Medium: 0.30 ≤ |r| < 0.50
- Large: |r| ≥ 0.50

**Quality Checks**:
- ✅ Linearity confirmed visually
- ✅ No extreme outliers (|residual| > 3 SD) dominating relationship
- ✅ Correlation coefficient in valid range [-1, 1]
- ✅ P-value calculation correct
- ✅ Sample size adequate (N ≥ 40 preferred)

#### Median Split Classification

**Method**: Split on median sophistication composite score

**Quality Requirements**:
- ✅ Median value in expected range (4-7 on 10-point scale)
- ✅ Groups reasonably balanced (within ±5 models)
- ✅ Sophistication separation strong (d ≥ 1.5)
- ✅ Classification deterministic (ties handled consistently)
- ✅ All models classified (no missing data)

**Known Limitations**:
- Reduces statistical power vs. continuous regression
- Dichotomizes inherently continuous variable
- Median value condition-specific (not directly comparable)

**Mitigation**:
- Document borderline models (within ±0.15 of median)
- Report continuous correlation (H2) alongside dichotomous comparison (H1)
- Sensitivity analyses for borderline models

### Phase 2: Cross-Condition H3 Analysis

#### H3a: Median Shift Analysis

**Method**: Bootstrapped confidence intervals for medians

**Procedure**:
1. Calculate median sophistication per condition
2. Bootstrap 95% CI (10,000 iterations)
3. Compare non-overlapping CIs for differences

**Quality Checks**:
- ✅ Bootstrap samples ≥ 10,000
- ✅ CI width reasonable (not too narrow/wide)
- ✅ Median estimates stable across bootstrap samples

#### H3b: Correlation Comparison

**Method**: Fisher's r-to-z transformation for independent correlations

**Procedure**:
```
z1 = 0.5 * ln((1+r1)/(1-r1))
z2 = 0.5 * ln((1+r2)/(1-r2))
SE_diff = sqrt(1/(n1-3) + 1/(n2-3))
Z = (z1 - z2) / SE_diff
```

**Quality Checks**:
- ✅ Sample sizes adequate (n ≥ 20 per condition)
- ✅ Correlations from independent samples
- ✅ Transformation applied correctly
- ✅ Two-tailed test unless directional hypothesis pre-specified

#### H3c: Effect Size Comparison

**Method**: Confidence interval overlap for Cohen's d

**Procedure**:
1. Calculate d per condition with 95% CI
2. Check for overlapping CIs
3. Formal test if needed: Hedge's g comparison test

**Quality Checks**:
- ✅ Same measurement scales across conditions
- ✅ CI calculation accounts for sample size
- ✅ Effect size direction consistent with hypothesis

#### H3d: Dimension-Level Analysis

**Method**: Repeated measures ANOVA or linear mixed model

**Procedure**:
- DV: Effect size or correlation coefficient
- Within-subjects: Dimension (4 or 9 levels)
- Between-subjects: Condition
- Test: Condition × Dimension interaction

**Quality Checks**:
- ✅ Sphericity assumption checked (Mauchly's test)
- ✅ Greenhouse-Geisser correction if sphericity violated
- ✅ Bonferroni correction for post-hoc comparisons
- ✅ Effect sizes reported (partial η²)

### Phase 3: Combined Meta-Analysis

#### Random Effects Model

**Method**: Restricted Maximum Likelihood (REML) random effects meta-analysis

**Model**:
```
Effect_i ~ N(θ + u_condition, σ²)
u_condition ~ N(0, τ²)
```

**Heterogeneity Measures**:
- **I²**: % variance due to heterogeneity (not sampling error)
  - Low: I² < 25%
  - Moderate: 25% ≤ I² < 75%
  - High: I² ≥ 75%
- **Q statistic**: Test for heterogeneity (χ² distribution)
- **τ²**: Between-condition variance estimate

**Quality Checks**:
- ✅ Minimum 3 conditions for meta-analysis
- ✅ Effect sizes on same scale
- ✅ Direction consistent across studies
- ✅ Heterogeneity assessed and reported
- ✅ Publication bias not applicable (no selection)

#### Model Stability Coefficients

**Method**: Intraclass Correlation Coefficient (ICC)

**Formula**:
```
ICC = σ²_between / (σ²_between + σ²_within)
```

**Interpretation**:
- High stability: ICC > 0.80
- Moderate stability: 0.50 ≤ ICC ≤ 0.80
- Low stability: ICC < 0.50

**Quality Checks**:
- ✅ Same models measured across conditions
- ✅ ICC in valid range [0, 1]
- ✅ Sufficient conditions (≥3) for reliable estimate

---

## Quality Control Procedures

### Pre-Execution Checks

**Before ANY analysis**:

1. **Data Completeness**
   - [ ] All expected model profiles present
   - [ ] All 9 behavioral dimensions populated
   - [ ] No missing values (NaN, null, undefined)
   - [ ] Profile counts documented

2. **Data Validity**
   - [ ] All scores in valid range (1-10 for dimensions)
   - [ ] Contribution counts > 0 for all profiles
   - [ ] Timestamps chronologically ordered
   - [ ] Model IDs match expected format

3. **Sample Size**
   - [ ] N ≥ 40 models (preferred)
   - [ ] N ≥ 30 models (acceptable with caveat)
   - [ ] N < 30 models (warning issued, proceed with caution)

4. **Directory Structure**
   - [ ] Output directory exists
   - [ ] Write permissions confirmed
   - [ ] Previous results backed up if overwriting

### During-Execution Monitoring

1. **Computation Validation**
   - Monitor for numerical instabilities
   - Check for warnings in statistical packages
   - Verify convergence for iterative methods

2. **Intermediate Results**
   - Spot-check calculation steps
   - Verify expected relationships (e.g., correlation direction)
   - Flag anomalies for review

### Post-Execution Validation

**After EVERY analysis**:

1. **Statistical Results Validation**
   - [ ] No NaN, Inf, or undefined values
   - [ ] Test statistics in plausible range
   - [ ] P-values between 0 and 1
   - [ ] Effect sizes match interpretation
   - [ ] Degrees of freedom correct

2. **Assumption Checks**
   - [ ] All required assumptions documented
   - [ ] Violations noted and addressed
   - [ ] Alternative methods used if needed

3. **Visualization Validation**
   - [ ] All plots render correctly
   - [ ] Axes labeled with units
   - [ ] Legends clear and accurate
   - [ ] File sizes reasonable (< 2 MB per PNG)
   - [ ] Resolution adequate (≥ 300 DPI for publication)

4. **Report Validation**
   - [ ] All sections complete
   - [ ] Tables formatted correctly
   - [ ] Statistics reported with precision
   - [ ] References accurate

---

## Audit Protocols

### Automated Audits

**Frequency**: Every analysis run

**Checks**:
1. File integrity (checksums for critical data)
2. Reproducibility (re-run deterministic parts)
3. Consistency (compare to previous runs if applicable)

**Implementation**:
```python
# Audit script pseudocode
def audit_analysis(condition):
    # 1. Check data integrity
    verify_profile_checksums()

    # 2. Validate results
    check_no_nan_inf()
    check_value_ranges()

    # 3. Compare to expected
    if baseline_exists():
        compare_to_baseline_patterns()

    # 4. Log results
    write_audit_log(timestamp, checks, status)
```

### Manual Audits

**Frequency**:
- After first condition (baseline): Full audit
- After each new condition: Spot audit
- After cross-condition analysis: Full audit
- Before final publication: Full audit

**Audit Checklist**:

1. **Data Provenance** (10 min)
   - [ ] Trace data back to source jobs
   - [ ] Verify job configurations match expectations
   - [ ] Check judge evaluation quality

2. **Statistical Methods** (15 min)
   - [ ] Methods match documentation
   - [ ] Formulas implemented correctly
   - [ ] Assumptions verified
   - [ ] Alternative methods considered if assumptions violated

3. **Results Plausibility** (10 min)
   - [ ] Effect sizes match visual inspection
   - [ ] Results theoretically sensible
   - [ ] Extreme values investigated
   - [ ] Outliers documented

4. **Reproducibility** (15 min)
   - [ ] Re-run analysis from scratch
   - [ ] Verify identical results
   - [ ] Check random seed control
   - [ ] Document any discrepancies

5. **Reporting Accuracy** (15 min)
   - [ ] Numbers match output files
   - [ ] Tables transcribed correctly
   - [ ] Figures match descriptions
   - [ ] Statistics rounded appropriately

**Total Time**: ~65 minutes per full audit

### Audit Documentation

All audits documented in:
```
<condition>/audit/
├── audit_log.json          # Automated checks
├── manual_audit_YYYYMMDD.md # Manual review notes
└── discrepancies.json      # Any issues found
```

**Audit Log Format**:
```json
{
  "audit_id": "baseline_20260110_001",
  "timestamp": "2026-01-10T10:30:00Z",
  "condition": "baseline",
  "audit_type": "automated",
  "checks": {
    "data_integrity": "PASS",
    "statistical_validity": "PASS",
    "visualization_quality": "PASS",
    "report_completeness": "PASS"
  },
  "warnings": [],
  "errors": [],
  "auditor": "automated_system"
}
```

---

## Validation Checklists

### Per-Condition H1/H2 Validation

**Status**: ✅ Validated on baseline condition

**Before Accepting Results**:

- [ ] **Sample Quality**
  - N ≥ 40 models OR justified exception
  - All dimensions complete
  - No data anomalies

- [ ] **Classification Quality**
  - Median in range 4-7
  - Groups balanced (|n_high - n_low| ≤ 5)
  - Sophistication separation d ≥ 1.5

- [ ] **H1 Statistics**
  - t-statistic reasonable
  - p-value < 0.05 for all disinhibition dimensions (expected)
  - Cohen's d ≥ 0.8 (large effect expected)
  - Variance ratio ≤ 4:1 (or justified exception)

- [ ] **H2 Statistics**
  - Scatter plot shows linear relationship
  - r ≥ 0.50 (large effect expected)
  - p-value < 0.05
  - No extreme outliers dominating

- [ ] **Outputs Generated**
  - 5 files created (1 JSON, 4 PNG, 1 MD)
  - File sizes reasonable
  - All visualizations clear

- [ ] **Special Patterns Documented**
  - Borderline models identified
  - Constrained models identified
  - Outliers identified
  - All documented in brief

### Cross-Condition H3 Validation

**Status**: 🚧 Template ready, to be validated

**Before Accepting Results**:

- [ ] **Sample Requirements**
  - ≥3 conditions analyzed
  - Same models across conditions
  - Comparable sample sizes

- [ ] **H3a: Median Shifts**
  - Bootstrap CIs reasonable width
  - Medians interpretable
  - Differences make theoretical sense

- [ ] **H3b: Correlation Comparison**
  - Fisher's z transformation applied
  - Tests appropriate for independent samples
  - Confidence intervals reported

- [ ] **H3c: Effect Size Comparison**
  - Same scale across conditions
  - CIs calculated correctly
  - Interpretations justified

- [ ] **H3d: Dimension Effects**
  - Multiple comparison correction applied
  - Interaction plots interpretable
  - Post-hoc tests justified

### Combined Meta-Analysis Validation

**Status**: 🚧 Template ready, to be validated

**Before Accepting Results**:

- [ ] **Meta-Analytic Model**
  - Random effects appropriate
  - REML estimation converged
  - Heterogeneity assessed

- [ ] **Pooled Effects**
  - Weighted average sensible
  - CIs reasonable width
  - Heterogeneity interpreted

- [ ] **Model Stability**
  - ICC calculations correct
  - Patterns interpretable
  - Exceptions documented

---

## Data Integrity Requirements

### Profile Data

**Required Fields** (per model profile):
```json
{
  "model_id": "string",
  "display_name": "string",
  "scores": {
    "warmth": "float [1-10]",
    "formality": "float [1-10]",
    "hedging": "float [1-10]",
    "aggression": "float [1-10]",
    "transgression": "float [1-10]",
    "grandiosity": "float [1-10]",
    "tribalism": "float [1-10]",
    "depth": "float [1-10]",
    "authenticity": "float [1-10]"
  },
  "contribution_count": "int > 0",
  "last_updated": "ISO 8601 timestamp"
}
```

**Validation Rules**:
1. All scores in range [1, 10]
2. No missing dimensions
3. No NaN or null values
4. Contribution count > 0
5. Model ID unique within condition
6. Display name human-readable

### Classification Data

**Required Fields**:
```json
{
  "median_sophistication": "float [4-7]",
  "n_high_sophistication": "int [15-35]",
  "n_low_sophistication": "int [15-35]",
  "models": "array [length 40-60]",
  "statistics": "object",
  "correlation": "object"
}
```

**Validation Rules**:
1. Median in expected range
2. Groups reasonably balanced
3. All models classified
4. Statistics complete
5. No computational errors

### Historical Data

**Contribution Tracking**:
- Job IDs traced to source
- Timestamps sequential
- Updates logged
- Reversible operations documented

---

## Reporting Standards

### Statistical Reporting Format

**Effect Sizes**:
- Always report with 2 decimal places
- Include 95% CI in brackets
- Example: "d = 2.17 (95% CI [1.85, 2.49])"

**P-Values**:
- Report exact values when p ≥ .001
- Report as "p < .001" when p < .001
- Never report as "p = 0.000"
- Example: "p = .023" or "p < .001"

**Test Statistics**:
- Include degrees of freedom
- Example: "t(44) = 7.35"
- Example: "F(3, 135) = 12.45"

**Correlations**:
- Report r with 3 decimal places
- Include sample size
- Example: "r(44) = .738, p < .001"

### Table Standards

**Required Elements**:
1. Clear column headers with units
2. Consistent decimal places within columns
3. Alignment (numbers right-aligned)
4. Summary statistics (M, SD, n)
5. Effect sizes alongside inferential tests
6. Footnotes for special cases

**Example**:
```
| Dimension | High-Soph | Low-Soph | Δ | t(44) | p | d |
|-----------|-----------|----------|---|-------|---|---|
| Trans.    | 1.83 (0.16) | 1.41 (0.08) | +0.42 | 6.28 | <.001 | 1.85 |
```

### Figure Standards

**Required Elements**:
1. Axis labels with units
2. Legend (if multiple series)
3. Title or caption
4. Error bars with definition (SE, SD, CI)
5. Sample sizes noted
6. Statistical significance markers (if applicable)

**Quality Requirements**:
- Resolution ≥ 300 DPI for publication
- Font size ≥ 10pt
- Color-blind friendly palette
- High contrast (readable in grayscale)

---

## Reproducibility Requirements

### Deterministic Operations

**Must Be Reproducible**:
1. Data loading and aggregation
2. Median split classification
3. Statistical tests
4. Table generation
5. Core visualizations

**Implementation**:
- No randomness in core pipeline
- Consistent file ordering (sorted)
- Fixed precision in calculations
- Documented software versions

### Random Operations

**If Randomness Required**:
1. Set random seed explicitly
2. Document seed value
3. Report software version
4. Provide seed in code comments

**Example**:
```python
import numpy as np
np.random.seed(42)  # Fixed seed for reproducibility
bootstrap_samples = bootstrap(data, n_iterations=10000)
```

### Software Environment

**Document**:
1. Python version (e.g., 3.11.5)
2. Key package versions:
   - numpy == 1.24.3
   - scipy == 1.11.2
   - matplotlib == 3.7.2
   - pandas == 2.0.3

**Recommendation**: Use `requirements.txt` or `environment.yml`

### Version Control

**Critical Files Under Version Control**:
- Analysis scripts
- Configuration files
- Documentation
- Templates

**Generated Files (Not Under Version Control)**:
- Output data (too large)
- Visualizations (regenerable)
- Intermediate results (regenerable)

**Exception**: Baseline reference files may be versioned for comparison

---

## Troubleshooting Decision Trees

### Issue: Variance Ratio > 4:1

**Decision Tree**:
```
Variance ratio > 4:1?
├─ Yes → Check sample sizes
│  ├─ Both n ≥ 20?
│  │  ├─ Yes → Use Welch's t-test, document in brief
│  │  └─ No → Warning: Low power, proceed with caution
│  └─ Effect size large (d > 1.5)?
│     ├─ Yes → Proceed, note robustness
│     └─ No → Consider non-parametric test
└─ No → Standard t-test OK
```

### Issue: Non-Normal Distribution

**Decision Tree**:
```
Shapiro-Wilk p < .05?
├─ Yes (non-normal) → Check sample size
│  ├─ n ≥ 30?
│  │  ├─ Yes → t-test robust, proceed (CLT applies)
│  │  └─ No → Consider Mann-Whitney U test
│  └─ Outliers present?
│     ├─ Yes → Investigate, possibly remove with justification
│     └─ No → Use robust methods
└─ No (normal) → Standard tests OK
```

### Issue: Low Sample Size (N < 40)

**Decision Tree**:
```
N < 40?
├─ Yes → Determine minimum
│  ├─ N ≥ 30?
│  │  ├─ Yes → Proceed with warning
│  │  │  └─ Document: "N=X, below preferred N≥40"
│  │  └─ No → N ≥ 20?
│  │     ├─ Yes → Proceed with strong caution
│  │     │  └─ Document: Power likely insufficient
│  │     └─ No → Do not proceed
│  │        └─ Collect more data
└─ No → Standard analysis
```

### Issue: Outliers Detected

**Decision Tree**:
```
Outlier detected (|residual| > 2 SD)?
├─ Yes → Investigate cause
│  ├─ Data entry error?
│  │  ├─ Yes → Correct data, re-run
│  │  └─ No → True outlier?
│  │     ├─ Yes → Document, keep in analysis
│  │     │  └─ Report with/without outlier
│  │     └─ Suspicious?
│  │        └─ Manual review required
└─ No → Proceed normally
```

---

## Audit Trail Example

### Baseline Condition (2026-01-10)

**Pre-Execution Audit**:
- ✅ N = 46 models (adequate)
- ✅ All profiles complete
- ✅ No missing values
- ✅ Previous results backed up

**Statistical Validation**:
- ✅ Median = 5.930 (within 4-7)
- ✅ Groups perfectly balanced (23 vs 23)
- ✅ Sophistication separation d = 3.18 (excellent)
- ✅ H1: d = 2.17, p < .001 (large effect, significant)
- ✅ H2: r = .738, p < .001 (large effect, significant)
- ⚠️ Variance ratios >2:1 for tribalism (4.74), grandiosity (4.65)
  - Mitigation: Large effect sizes robust to heterogeneity
  - Documented in brief

**Output Validation**:
- ✅ All 5 files generated
- ✅ File sizes reasonable (237KB - 1.1MB)
- ✅ Visualizations clear
- ✅ Research brief complete

**Manual Audit**:
- ✅ Data provenance confirmed
- ✅ Methods match documentation
- ✅ Results plausible
- ✅ Reproducible (re-run identical)
- ✅ Reporting accurate

**Audit Status**: ✅ PASSED (with documented variance heterogeneity noted)

---

## Standards Evolution

### Version History

**v1.0 (2026-01-10)**:
- Initial framework
- Validated on baseline H1/H2 analysis
- Templates for H3 and combined analyses

**Future Versions**:
- v1.1: After H3 analysis, update with learned lessons
- v1.2: After combined analysis, finalize meta-analytic standards
- v2.0: After Phase 4, comprehensive revision

### Amendment Process

**To Update Standards**:
1. Document proposed change with rationale
2. Pilot on test dataset
3. Compare old vs new methods
4. Update documentation
5. Increment version number
6. Notify research team

### Grandfathering

**Existing Analyses**:
- Baseline (v1.0): Validated, meets all standards
- Future analyses: Must meet current version standards
- Retrospective: No need to re-run unless methods changed

---

## Reference Standards

### Statistical Software

**Primary**: Python 3.x with scipy.stats
- Independent samples t-test: `scipy.stats.ttest_ind()`
- Welch's t-test: `scipy.stats.ttest_ind(equal_var=False)`
- Pearson correlation: `scipy.stats.pearsonr()`

**Alternative**: R with stats package
- t.test(y ~ group)
- cor.test(x, y, method="pearson")

### Effect Size Conventions

**Source**: Cohen, J. (1988). *Statistical power analysis for the behavioral sciences* (2nd ed.). Hillsdale, NJ: Erlbaum.

**APA Style**: American Psychological Association. (2020). *Publication manual* (7th ed.).

### Meta-Analysis

**Source**: Borenstein, M., Hedges, L. V., Higgins, J. P., & Rothstein, H. R. (2009). *Introduction to meta-analysis*. Chichester, UK: Wiley.

---

**Document Status**: ✅ Active
**Next Review**: After Phase 2 (H3) completion
**Maintained By**: Research team
**Questions**: See research_synthesis/INDEX.md for contact
