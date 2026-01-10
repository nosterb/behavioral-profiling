# H1/H2 Statistical Replication - Quality Control Checklist

**Purpose**: Comprehensive validation framework to ensure statistical integrity and reproducibility across intervention conditions.

**Date**: 2026-01-10

---

## Overview

Before applying the H1/H2 analysis pipeline to new intervention conditions, we must verify:
1. **Statistical validity** - Methods are sound and assumptions are met
2. **Reproducibility** - Results are consistent when re-run
3. **Data integrity** - All required data present and valid
4. **Output quality** - Visualizations and reports meet standards
5. **Cross-condition comparability** - Results can be meaningfully compared

---

## Part 1: Statistical Methodology Review

### 1.1 Median Split Classification

**Method**: Capability-based classification using sophistication composite
- **Sophistication Score**: `(depth + authenticity) / 2`
- **Classification Rule**: Models ≥ median = High-Sophistication, < median = Low-Sophistication

**Assumptions**:
- ✅ Sophistication is continuous variable (1-10 scale)
- ✅ Distribution allows meaningful split (not all clustered at one value)
- ✅ Classification captures capability, not just version/release date

**Validation Checks**:
```python
# Check sophistication distribution
import json
from pathlib import Path

data = json.loads(Path('outputs/behavioral_profiles/baseline/median_split_classification.json').read_text())

# 1. Check median value is reasonable (should be ~5-6)
median = data['median_sophistication']
print(f"Median: {median:.3f}")
assert 4.0 < median < 7.0, "Median outside expected range"

# 2. Check group balance (should be within ±5)
n_high = data['n_high_sophistication']
n_low = data['n_low_sophistication']
print(f"High: {n_high}, Low: {n_low}, Diff: {abs(n_high - n_low)}")
assert abs(n_high - n_low) <= 5, "Groups highly imbalanced"

# 3. Check sophistication separation (Cohen's d should be ≥ 2.0)
d = data['statistics']['sophistication']['cohens_d']
print(f"Sophistication separation d: {d:.2f}")
assert d >= 2.0, "Weak sophistication separation"

print("✓ Classification validity checks passed")
```

### 1.2 Independent Samples t-tests (H1)

**Method**: Comparing High vs Low sophistication groups on disinhibition dimensions

**Formula**:
```
t = (M_high - M_low) / sqrt((SD_high² / n_high) + (SD_low² / n_low))
df = n_high + n_low - 2
Cohen's d = (M_high - M_low) / SD_pooled
```

**Assumptions**:
- ✅ **Independence**: Each model evaluated independently
- ✅ **Normality**: With n≈23 per group, t-test robust to moderate violations
- ⚠️ **Equal variances**: Assumed for pooled SD; check if ratio > 2:1

**Validation Checks**:
```python
# Check assumption violations
for dim in ['disinhibition', 'transgression', 'aggression', 'tribalism', 'grandiosity']:
    stats = data['statistics'][dim]

    # 1. Check variance ratio (Levene's test rule of thumb)
    var_ratio = (stats['high_std'] ** 2) / (stats['low_std'] ** 2)
    print(f"{dim}: Variance ratio = {var_ratio:.2f}")
    if var_ratio > 2.0 or var_ratio < 0.5:
        print(f"  ⚠️  Consider Welch's t-test for {dim}")

    # 2. Check effect size is reasonable (d should be positive for disinhibition)
    d = stats['cohens_d']
    print(f"{dim}: Cohen's d = {d:.2f}")
    assert d > 0, f"Unexpected negative effect for {dim}"

print("✓ t-test assumption checks completed")
```

### 1.3 Pearson Correlations (H2)

**Method**: Correlation between sophistication and disinhibition across all models

**Formula**:
```
r = Σ((x_i - x̄)(y_i - ȳ)) / sqrt(Σ(x_i - x̄)² * Σ(y_i - ȳ)²)
```

**Assumptions**:
- ✅ **Linearity**: Relationship should be approximately linear
- ✅ **Bivariate normality**: Required for significance testing
- ⚠️ **No outliers dominating**: That's why we identify them!

**Validation Checks**:
```python
# Check correlation validity
r = data['correlation']['sophistication_disinhibition']
print(f"Sophistication-Disinhibition r: {r:.3f}")

# 1. Check correlation is in valid range
assert -1 <= r <= 1, "Invalid correlation coefficient"

# 2. Check correlation is positive (expected theoretical direction)
assert r > 0, "Unexpected negative correlation"

# 3. Check correlation is substantial (r > 0.5 expected for baseline)
print(f"  {'Strong' if r > 0.7 else 'Moderate' if r > 0.5 else 'Weak'} correlation")

# 4. Check R² (variance explained)
r_squared = r ** 2
print(f"  R² = {r_squared:.3f} ({r_squared*100:.1f}% variance explained)")

print("✓ Correlation validity checks passed")
```

### 1.4 Effect Size Interpretation Standards

**Cohen's d thresholds** (Cohen, 1988):
- < 0.2: Negligible
- 0.2-0.5: Small
- 0.5-0.8: Medium
- ≥ 0.8: Large

**Pearson r thresholds** (Cohen, 1988):
- < 0.10: Negligible
- 0.10-0.30: Small
- 0.30-0.50: Medium
- ≥ 0.50: Large

**Validation**:
```python
# Verify effect size interpretations
def classify_d(d):
    abs_d = abs(d)
    if abs_d < 0.2: return "negligible"
    elif abs_d < 0.5: return "small"
    elif abs_d < 0.8: return "medium"
    else: return "large"

def classify_r(r):
    abs_r = abs(r)
    if abs_r < 0.10: return "negligible"
    elif abs_r < 0.30: return "small"
    elif abs_r < 0.50: return "medium"
    else: return "large"

# Check baseline expectations
d = data['statistics']['disinhibition']['cohens_d']
print(f"H1 effect: d={d:.2f} ({classify_d(d)})")
assert classify_d(d) == "large", "H1 should show large effect"

r = data['correlation']['sophistication_disinhibition']
print(f"H2 effect: r={r:.3f} ({classify_r(r)})")
assert classify_r(r) == "large", "H2 should show large effect"

print("✓ Effect sizes meet expectations")
```

---

## Part 2: Data Integrity Validation

### 2.1 Profile Completeness Check

**Required Dimensions** (all must be present):
- warmth, formality, hedging (general behavioral)
- transgression, aggression, tribalism, grandiosity (disinhibition)
- depth, authenticity (sophistication)

**Validation Script**:
```bash
#!/bin/bash
INTERVENTION="baseline"
PROFILE_DIR="outputs/behavioral_profiles/${INTERVENTION}"

echo "=== PROFILE COMPLETENESS CHECK ==="

# Check total profile count
PROFILE_COUNT=$(ls ${PROFILE_DIR}/profiles/*.json 2>/dev/null | wc -l | tr -d ' ')
echo "Total profiles: ${PROFILE_COUNT}"
if [ ${PROFILE_COUNT} -lt 40 ]; then
    echo "⚠️  Warning: Low sample size (< 40 models)"
fi

# Check for missing dimensions
python3 -c "
import json
from pathlib import Path

required_dims = ['warmth', 'formality', 'hedging', 'transgression', 'aggression',
                 'tribalism', 'grandiosity', 'depth', 'authenticity']

profile_dir = Path('${PROFILE_DIR}/profiles')
issues = []

for p in profile_dir.glob('*.json'):
    data = json.loads(p.read_text())
    scores = data.get('average_scores', {})
    missing = [d for d in required_dims if d not in scores]
    if missing:
        issues.append((p.name, missing))

if not issues:
    print('✓ All profiles have complete dimensions')
else:
    print(f'❌ Found {len(issues)} profiles with missing dimensions:')
    for name, missing in issues[:5]:
        print(f'  - {name}: missing {missing}')
"

# Check contribution counts
python3 -c "
import json
from pathlib import Path

profile_dir = Path('${PROFILE_DIR}/profiles')
low_contrib = []

for p in profile_dir.glob('*.json'):
    data = json.loads(p.read_text())
    n = data.get('n_contributions', 0)
    if n < 10:
        low_contrib.append((p.name, n))

if not low_contrib:
    print('✓ All profiles have sufficient contributions (≥10)')
else:
    print(f'⚠️  Found {len(low_contrib)} profiles with low contributions:')
    for name, n in sorted(low_contrib, key=lambda x: x[1])[:5]:
        print(f'  - {name}: only {n} contributions')
"
```

### 2.2 Score Range Validation

**Expected Ranges**:
- All dimensions: 1.0 - 10.0 (defined scale)
- Sophistication composite: 1.0 - 10.0
- Disinhibition composite: 1.0 - 10.0

**Validation**:
```python
# Check all scores are within valid range
for model in data['models']:
    for dim in ['warmth', 'formality', 'hedging', 'transgression', 'aggression',
                'tribalism', 'grandiosity', 'depth', 'authenticity']:
        score = model['scores'][dim]
        assert 1.0 <= score <= 10.0, f"{model['display_name']} {dim} out of range: {score}"

    assert 1.0 <= model['sophistication'] <= 10.0, f"Sophistication out of range"
    assert 1.0 <= model['disinhibition'] <= 10.0, f"Disinhibition out of range"

print("✓ All scores within valid range [1.0, 10.0]")
```

### 2.3 Sample Size Adequacy

**Minimum Requirements**:
- Total N ≥ 40 models (for adequate power)
- Each group N ≥ 15 (for t-test robustness)
- Correlation N ≥ 30 (for stable estimates)

**Validation**:
```python
n_total = len(data['models'])
n_high = data['n_high_sophistication']
n_low = data['n_low_sophistication']

print(f"Total N: {n_total}")
assert n_total >= 40, "Insufficient total sample size"

print(f"High-Soph N: {n_high}")
assert n_high >= 15, "High-sophistication group too small"

print(f"Low-Soph N: {n_low}")
assert n_low >= 15, "Low-sophistication group too small"

print("✓ Sample sizes adequate")
```

---

## Part 3: Reproducibility Testing

### 3.1 Baseline Re-run Test

**Purpose**: Verify that re-running analysis on baseline produces consistent results

**Test Protocol**:
```bash
# 1. Backup current baseline outputs
mkdir -p /tmp/baseline_backup
cp outputs/behavioral_profiles/baseline/*.{png,md,json} /tmp/baseline_backup/

# 2. Re-run complete pipeline
./scripts/run_h1_h2_analysis.sh baseline

# 3. Compare key statistics
python3 -c "
import json
from pathlib import Path

old = json.loads(Path('/tmp/baseline_backup/median_split_classification.json').read_text())
new = json.loads(Path('outputs/behavioral_profiles/baseline/median_split_classification.json').read_text())

# Compare key statistics
print('Checking reproducibility...')

# Median should be identical
assert old['median_sophistication'] == new['median_sophistication'], 'Median changed!'
print(f\"✓ Median: {new['median_sophistication']:.3f}\")

# Group sizes should be identical
assert old['n_high_sophistication'] == new['n_high_sophistication'], 'Group sizes changed!'
assert old['n_low_sophistication'] == new['n_low_sophistication'], 'Group sizes changed!'
print(f\"✓ Group sizes: {new['n_high_sophistication']} vs {new['n_low_sophistication']}\")

# Key statistics should be identical (or within rounding error)
old_d = old['statistics']['disinhibition']['cohens_d']
new_d = new['statistics']['disinhibition']['cohens_d']
assert abs(old_d - new_d) < 0.001, 'Cohen\\'s d changed!'
print(f\"✓ Disinhibition d: {new_d:.3f}\")

old_r = old['correlation']['sophistication_disinhibition']
new_r = new['correlation']['sophistication_disinhibition']
assert abs(old_r - new_r) < 0.001, 'Correlation changed!'
print(f\"✓ Correlation r: {new_r:.3f}\")

print('\\n✓ Baseline results are reproducible')
"
```

**Expected Result**: All statistics should be identical (no randomness in pipeline)

### 3.2 Determinism Check

**Verification**:
- No random seeds in any scripts
- No stochastic algorithms
- File ordering deterministic (sorted by sophistication/dimension values)
- Label positioning deterministic (based on model values, not random)

**Review**:
```bash
# Check for random/stochastic elements
grep -r "random\|shuffle\|seed" scripts/create_h*.py scripts/update_research_brief*.py

# Should return no results (or only in comments)
```

---

## Part 4: Output Quality Validation

### 4.1 Visualization Checklist

**H1 Bar Charts** (`h1_bar_chart_comparison.png`):
- [ ] All 5 dimensions shown (disinhibition composite + 4 individual)
- [ ] Both groups represented (high-soph green, low-soph red)
- [ ] Error bars visible (standard deviation)
- [ ] Mean values labeled on bars
- [ ] Significance markers shown (*** p < .001)
- [ ] Cohen's d values shown above comparisons
- [ ] Legend present
- [ ] Axis labels clear

**H1 Summary Table** (`h1_summary_table.png`):
- [ ] All 5 dimensions included
- [ ] Columns: Dimension, High-Soph M(SD), Low-Soph M(SD), Δ, % Δ, t(44), p, d, Effect
- [ ] Disinhibition composite highlighted
- [ ] All statistical values present
- [ ] Effect size labels correct

**H2 Composite Scatter** (`h2_scatter_sophistication_composite.png`):
- [ ] All models plotted (n=46)
- [ ] High-soph in green, low-soph in red
- [ ] Borderline models in orange squares
- [ ] Constrained models in cyan diamonds
- [ ] Statistical outliers circled in red
- [ ] Extreme models labeled (deduplicated)
- [ ] Median split line (purple dashed)
- [ ] Borderline zone shaded (orange)
- [ ] Regression line shown (black dashed)
- [ ] Group means marked (X symbols)
- [ ] Statistics box present (r, d, counts)
- [ ] Legend complete

**H2 All Dimensions** (`h2_scatter_all_dimensions.png`):
- [ ] 4 subplots (transgression, aggression, tribalism, grandiosity)
- [ ] Extreme models labeled (first subplot only, deduplicated)
- [ ] Borderline models shown in all subplots
- [ ] Dimension-specific outliers highlighted
- [ ] Statistics shown per subplot (r, d, outlier count)
- [ ] Median split line in all subplots
- [ ] Regression lines shown
- [ ] Legend on first subplot

### 4.2 Research Brief Checklist

**Required Sections**:
- [ ] Title with intervention name
- [ ] Study overview (date, condition, sample, providers)
- [ ] Hypotheses (H1 and H2)
- [ ] Methods (classification, measurement, statistical analysis)
- [ ] Results - H1 (disinhibition composite, individual dimensions, sophistication check, other dimensions)
- [ ] Results - H2 (correlation, individual dimensions)
- [ ] Results - Notable Patterns (borderline, constrained, outliers)
- [ ] Discussion (hypothesis support, effect sizes, implications)
- [ ] Supporting Files (data files, classification lists, scripts, visualizations)

**Statistical Reporting Format**:
- [ ] t-tests: `t(44) = X.XX, p < .001, d = X.XX`
- [ ] Correlations: `r = X.XXX, p < .001`
- [ ] Means: `M = X.XX, SD = X.XX`
- [ ] Effect size labels: (negligible/small/medium/large)

**Content Quality**:
- [ ] All statistics match median_split_classification.json
- [ ] Model counts correct (n_high, n_low, total)
- [ ] Borderline models listed with distances from median
- [ ] Constrained models listed with residuals
- [ ] Outliers listed with direction
- [ ] Classification lists complete (high-soph and low-soph)
- [ ] Intervention name correctly displayed throughout

### 4.3 File Integrity Check

```bash
INTERVENTION="baseline"
PROFILE_DIR="outputs/behavioral_profiles/${INTERVENTION}"

echo "=== FILE INTEGRITY CHECK ==="

# Required files
FILES=(
    "${PROFILE_DIR}/median_split_classification.json"
    "${PROFILE_DIR}/h1_bar_chart_comparison.png"
    "${PROFILE_DIR}/h1_summary_table.png"
    "${PROFILE_DIR}/h2_scatter_sophistication_composite.png"
    "${PROFILE_DIR}/h2_scatter_all_dimensions.png"
    "${PROFILE_DIR}/RESEARCH_BRIEF.md"
)

all_exist=true
for file in "${FILES[@]}"; do
    if [ -f "${file}" ]; then
        size=$(ls -lh "${file}" | awk '{print $5}')
        echo "✓ ${file##*/} (${size})"
    else
        echo "❌ ${file##*/} MISSING"
        all_exist=false
    fi
done

if [ "${all_exist}" = true ]; then
    echo -e "\n✓ All required files present"
else
    echo -e "\n❌ Some required files missing"
    exit 1
fi

# Check file sizes are reasonable
# PNGs should be > 100KB, research brief > 10KB
echo -e "\nChecking file sizes..."
h1_bar_size=$(stat -f%z "${PROFILE_DIR}/h1_bar_chart_comparison.png")
if [ ${h1_bar_size} -gt 100000 ]; then
    echo "✓ H1 bar chart size OK"
else
    echo "⚠️  H1 bar chart unusually small"
fi

h2_composite_size=$(stat -f%z "${PROFILE_DIR}/h2_scatter_sophistication_composite.png")
if [ ${h2_composite_size} -gt 100000 ]; then
    echo "✓ H2 composite size OK"
else
    echo "⚠️  H2 composite unusually small"
fi

brief_size=$(stat -f%z "${PROFILE_DIR}/RESEARCH_BRIEF.md")
if [ ${brief_size} -gt 10000 ]; then
    echo "✓ Research brief size OK"
else
    echo "⚠️  Research brief unusually small"
fi
```

---

## Part 5: Cross-Condition Readiness

### 5.1 Expected Differences Between Conditions

When applying to new intervention (e.g., "affective"), expect:

**May Change**:
- Median sophistication value (intervention may shift perceived capability)
- Group sizes (different clustering around median)
- Effect sizes (intervention may strengthen/weaken relationships)
- Which models are outliers (some may respond differently to intervention)
- Specific disinhibition dimension effects (e.g., affective may increase warmth)

**Should NOT Change** (or change minimally):
- Overall sophistication-disinhibition correlation direction (should remain positive)
- Relative sophistication rankings (high-capability models stay high)
- Statistical methodology (same tests, same thresholds)
- Classification validity (sophistication separation should remain large)

### 5.2 Success Criteria for New Condition

**Minimum Requirements**:
- ✅ All 5 output files generate without errors
- ✅ Statistics are valid (no NaN, Inf, or out-of-range values)
- ✅ Sample size adequate (N ≥ 40, groups ≥ 15 each)
- ✅ Sophistication separation remains large (d ≥ 1.5)
- ✅ Visualizations are clear and interpretable
- ✅ Research brief includes all required sections

**Quality Indicators**:
- ✅ Correlation remains substantial (r ≥ 0.3, even if weaker than baseline)
- ✅ H1 effects remain significant (p < .05, even if smaller)
- ✅ Results make theoretical sense
- ✅ Special patterns identified appropriately

### 5.3 Comparison Framework

**Create comparison table across conditions**:

| Metric | Baseline | Affective | Authority | Urgency |
|--------|----------|-----------|-----------|---------|
| Median sophistication | 5.930 | ? | ? | ? |
| N (High / Low) | 23 / 23 | ? | ? | ? |
| H1: Disinhib d | 2.17 | ? | ? | ? |
| H1: p-value | <.001 | ? | ? | ? |
| H2: r | 0.738 | ? | ? | ? |
| H2: p-value | <.001 | ? | ? | ? |
| Borderline models | 3 | ? | ? | ? |
| Constrained models | 3 | ? | ? | ? |
| Outliers | 1 | ? | ? | ? |

This allows systematic comparison of intervention effects.

---

## Part 6: Pre-Flight Checklist for New Condition

### Before Running Pipeline for "Affective" (or any new intervention):

**Step 1: Data Preparation** ✅/❌
- [ ] Profile directory exists: `outputs/behavioral_profiles/affective/`
- [ ] Profiles aggregated from job outputs
- [ ] Median split classification complete: `median_split_classification.json` exists
- [ ] Profile count ≥ 40 models
- [ ] All profiles have 9 dimensions

**Step 2: Baseline Validation** ✅/❌
- [ ] Re-run baseline to confirm reproducibility
- [ ] Baseline statistics match previous run
- [ ] All baseline visualizations regenerate correctly

**Step 3: New Condition Setup** ✅/❌
- [ ] Intervention name confirmed: "affective"
- [ ] File paths correct: `outputs/behavioral_profiles/affective/`
- [ ] No conflicting files from previous failed runs

**Step 4: Execute Pipeline** ✅/❌
- [ ] Run: `./scripts/run_h1_h2_analysis.sh affective`
- [ ] Monitor for errors
- [ ] Check console output for warnings

**Step 5: Output Validation** ✅/❌
- [ ] All 5 files generated
- [ ] File sizes reasonable (see Part 4.3)
- [ ] Visualizations open correctly
- [ ] Research brief renders properly

**Step 6: Statistical Validation** ✅/❌
- [ ] Median sophistication reasonable (4-7 range)
- [ ] Group balance acceptable (within ±5)
- [ ] Sophistication separation large (d ≥ 1.5)
- [ ] Effect sizes interpretable
- [ ] No invalid values (NaN, Inf)

**Step 7: Content Review** ✅/❌
- [ ] Research brief intervention name correct ("Affective" not "Baseline")
- [ ] All sections present and complete
- [ ] Statistics formatted properly
- [ ] Model lists accurate
- [ ] Special patterns documented

**Step 8: Comparison** ✅/❌
- [ ] Compare to baseline results
- [ ] Document key differences
- [ ] Interpret intervention effects
- [ ] Update comparison table

---

## Part 7: Troubleshooting Common Issues

### Issue 1: Unbalanced Groups (e.g., 32 vs 14)

**Cause**: Models cluster near median value
**Solution**: Document in research brief; still valid methodology
**Example Text**:
```markdown
**Note**: The median split (median = 5.93) resulted in unequal groups
(n=32 high-sophistication, n=14 low-sophistication) due to clustering
of model scores near the median value. This is a natural consequence of
the capability distribution and does not invalidate the classification approach.
```

### Issue 2: Weak Effect Sizes (d < 1.0, r < 0.3)

**Cause**: Intervention may reduce sophistication-disinhibition relationship
**Solution**: Valid finding; document as intervention effect
**Example Text**:
```markdown
The affective intervention substantially reduced the sophistication-disinhibition
correlation (r = 0.32) compared to baseline (r = 0.74), suggesting that
affective framing disrupts the typical relationship between capability and
disinhibition.
```

### Issue 3: Negative Correlation (r < 0)

**Cause**: Intervention may reverse relationship
**Solution**: Investigate and document; scientifically interesting
**Example Text**:
```markdown
Unexpectedly, the authority intervention produced a negative correlation
between sophistication and disinhibition (r = -0.15, p = .32, ns), suggesting
that authority challenges may cause high-capability models to exhibit greater
restraint while lower-capability models become more uninhibited.
```

### Issue 4: Missing Profiles

**Cause**: Some models not evaluated for this intervention
**Solution**: Document which models excluded; proceed with available N
**Check**:
```python
# Compare model sets
baseline_models = {m['model_id'] for m in baseline_data['models']}
affective_models = {m['model_id'] for m in affective_data['models']}

missing_in_affective = baseline_models - affective_models
extra_in_affective = affective_models - baseline_models

if missing_in_affective:
    print(f"Models in baseline but not affective: {missing_in_affective}")
if extra_in_affective:
    print(f"Models in affective but not baseline: {extra_in_affective}")
```

### Issue 5: Script Errors

**Common Errors**:
- `FileNotFoundError`: Profile directory or classification file missing
- `KeyError`: Missing dimension in profile
- `ValueError`: Invalid statistic (NaN, Inf)

**Debug Steps**:
1. Check profile directory exists and has correct intervention name
2. Verify median_split_classification.json exists and is valid JSON
3. Check profile completeness (all 9 dimensions)
4. Re-run median split classification if needed

---

## Part 8: Final Go/No-Go Decision

### Ready to Proceed to New Condition If:

1. ✅ **Baseline reproduces correctly** - All statistics match, visualizations regenerate
2. ✅ **Statistical methodology validated** - All assumptions checked, methods sound
3. ✅ **Data integrity confirmed** - Complete profiles, adequate sample size
4. ✅ **Output quality verified** - All visualizations clear, research brief complete
5. ✅ **Scripts parameterized correctly** - Intervention name handling works
6. ✅ **Documentation complete** - Process documented, troubleshooting guide available
7. ✅ **Comparison framework ready** - Can meaningfully compare across conditions
8. ✅ **Success criteria defined** - Know what constitutes valid results

### Do NOT Proceed If:

- ❌ Baseline results don't reproduce
- ❌ Statistical assumptions seriously violated
- ❌ Data integrity issues (missing dimensions, insufficient N)
- ❌ Scripts produce errors or invalid outputs
- ❌ Visualization quality poor
- ❌ Unclear how to interpret cross-condition differences

---

## Part 9: Execution Plan for "Affective" Condition

### Pre-Execution Checklist:

```bash
# 1. Verify affective profile directory exists
ls outputs/behavioral_profiles/affective/

# 2. Check profile count
ls outputs/behavioral_profiles/affective/profiles/*.json | wc -l

# 3. Verify median split classification exists
ls outputs/behavioral_profiles/affective/median_split_classification.json

# 4. Quick validation of classification data
python3 -c "
import json
from pathlib import Path
data = json.loads(Path('outputs/behavioral_profiles/affective/median_split_classification.json').read_text())
print(f'Models: {len(data[\"models\"])}')
print(f'Median: {data[\"median_sophistication\"]:.3f}')
print(f'Groups: {data[\"n_high_sophistication\"]} vs {data[\"n_low_sophistication\"]}')
print(f'Disinhib d: {data[\"statistics\"][\"disinhibition\"][\"cohens_d\"]:.2f}')
print(f'Correlation r: {data[\"correlation\"][\"sophistication_disinhibition\"]:.3f}')
"
```

### Execution:

```bash
# Run complete H1/H2 pipeline for affective
./scripts/run_h1_h2_analysis.sh affective
```

### Post-Execution Validation:

```bash
# 1. Verify all outputs
ls -lh outputs/behavioral_profiles/affective/*.{png,md}

# 2. Quick statistics check
python3 -c "
import json
from pathlib import Path

affective = json.loads(Path('outputs/behavioral_profiles/affective/median_split_classification.json').read_text())
baseline = json.loads(Path('outputs/behavioral_profiles/baseline/median_split_classification.json').read_text())

print('=== BASELINE VS AFFECTIVE COMPARISON ===')
print(f'Median sophistication: {baseline[\"median_sophistication\"]:.3f} → {affective[\"median_sophistication\"]:.3f}')
print(f'H1 Cohen\\'s d: {baseline[\"statistics\"][\"disinhibition\"][\"cohens_d\"]:.2f} → {affective[\"statistics\"][\"disinhibition\"][\"cohens_d\"]:.2f}')
print(f'H2 correlation r: {baseline[\"correlation\"][\"sophistication_disinhibition\"]:.3f} → {affective[\"correlation\"][\"sophistication_disinhibition\"]:.3f}')
print(f'Outliers: {len([m for m in baseline[\"models\"] if m.get(\"outlier\")])} → {len([m for m in affective[\"models\"] if m.get(\"outlier\")])}')
"

# 3. View research brief
head -100 outputs/behavioral_profiles/affective/RESEARCH_BRIEF.md
```

---

## Part 10: Documentation Updates

After successfully running affective condition:

1. **Update comparison table** in this document with affective results
2. **Document key findings** - What's different from baseline?
3. **Note any issues encountered** and solutions
4. **Update H1_H2_ANALYSIS_GUIDE.md** if any new insights
5. **Consider automation** if running many conditions

---

## Summary: Statistical Replication Quality Control

### Core Principles:
1. **Methodology is sound** - Standard statistical tests, appropriate for data
2. **Assumptions are verified** - Checked for each condition
3. **Reproducibility is guaranteed** - No randomness in pipeline
4. **Quality is enforced** - Comprehensive validation at each step
5. **Comparability is ensured** - Same methods applied consistently

### Key Strengths:
- ✅ Deterministic pipeline (no random elements)
- ✅ Comprehensive validation checks
- ✅ Clear success criteria
- ✅ Well-documented methods
- ✅ Automated execution
- ✅ Cross-condition comparison framework

### Potential Limitations:
- ⚠️ Median split reduces power (vs regression)
- ⚠️ Assumes linearity (for correlations)
- ⚠️ Requires adequate sample size (N≥40)
- ⚠️ Equal variances assumed (for pooled Cohen's d)

### Mitigations:
- Large effect sizes overcome power loss
- Visual inspection confirms linearity
- Sample size adequate for all conditions
- Variance ratios monitored; Welch's t-test available if needed

---

**Status**: Ready to proceed to "affective" condition
**Confidence Level**: High
**Risk Assessment**: Low (comprehensive validation framework in place)

---

**Version**: 1.0
**Date**: 2026-01-10
**Next Review**: After completing 3-4 intervention conditions
