# Quick Start: H1/H2 Analysis for New Condition

**One-Command Pipeline**: Complete median split + H1/H2 analysis in a single step

---

## TL;DR - Run Analysis for New Condition

```bash
# One command does everything:
./scripts/run_complete_h1_h2_analysis.sh <intervention_name>

# Examples:
./scripts/run_complete_h1_h2_analysis.sh affective
./scripts/run_complete_h1_h2_analysis.sh authority
./scripts/run_complete_h1_h2_analysis.sh urgency
```

**That's it!** The script will:
1. ✅ Check prerequisites (profile directory exists, sufficient profiles)
2. ✅ Calculate median split classification
3. ✅ Generate H1 visualizations (bar charts + table)
4. ✅ Generate H2 scatter plots (composite + all dimensions)
5. ✅ Generate research brief (publication-ready markdown)
6. ✅ Report key statistics and next steps

---

## Prerequisites

Before running the pipeline, you need **Stage 1: Profile Aggregation** completed:

```bash
# Aggregate profiles from job outputs
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs/*/job_*_<intervention>_*.json \
    --profile-dir outputs/behavioral_profiles/<intervention>
```

**Example for affective**:
```bash
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs/*/job_*_affective_*.json \
    --profile-dir outputs/behavioral_profiles/affective
```

Then run the complete pipeline:
```bash
./scripts/run_complete_h1_h2_analysis.sh affective
```

---

## What Gets Created

For each intervention condition, the pipeline generates **5 files**:

### Data File
- `median_split_classification.json` - Complete classification data with statistics

### Visualizations (4 files)
- `h1_bar_chart_comparison.png` - Group comparison bar chart
- `h1_summary_table.png` - Statistical summary table
- `h2_scatter_sophistication_composite.png` - Main correlation plot
- `h2_scatter_all_dimensions.png` - 4-subplot grid

### Report
- `RESEARCH_BRIEF.md` - Publication-ready research brief

---

## Example: Complete Workflow for "Affective" Condition

### Step 1: Profile Aggregation (if not done)
```bash
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs/affective_suite/*.json \
    --profile-dir outputs/behavioral_profiles/affective
```

### Step 2: Run Complete H1/H2 Analysis
```bash
./scripts/run_complete_h1_h2_analysis.sh affective
```

### Expected Output
```
==========================================================================
COMPLETE H1/H2 ANALYSIS PIPELINE
==========================================================================
Intervention: affective
Profile Directory: outputs/behavioral_profiles/affective

=== PREREQUISITE CHECKS ===
✓ Profile directory exists
✓ Found 46 profile files

=== STAGE 2: MEDIAN SPLIT CLASSIFICATION ===
Calculating median split classification...
✓ Median split classification complete

Classification Summary:
  Models: 46
  Median sophistication: 5.850
  High-Sophistication: n = 24
  Low-Sophistication: n = 22
  Group balance: 2 model difference
  Sophistication separation: d = 3.05

=== STAGE 3: H1/H2 ANALYSIS ===
Step 3a: Generating H1 visualizations...
✓ Created: h1_bar_chart_comparison.png
✓ Created: h1_summary_table.png

Step 3b: Generating H2 scatter plots...
✓ Created: h2_scatter_sophistication_composite.png
✓ Created: h2_scatter_all_dimensions.png

Step 3c: Generating research brief...
✓ Updated RESEARCH_BRIEF.md

==========================================================================
PIPELINE COMPLETE!
==========================================================================

Generated Files:
  ✓ h1_bar_chart_comparison.png (245K)
  ✓ h1_summary_table.png (238K)
  ✓ h2_scatter_sophistication_composite.png (687K)
  ✓ h2_scatter_all_dimensions.png (1.1M)
  ✓ RESEARCH_BRIEF.md (13K)

Key Results:
  H1 (Group Difference):
    - Cohen's d = 1.98
    - p-value = 0.000001
    - Effect: Large

  H2 (Correlation):
    - r = 0.682
    - Effect: Large

  Special Patterns:
    - Borderline models: 4
    - Constrained models: 2
    - Statistical outliers: 1

==========================================================================
NEXT STEPS
==========================================================================

1. Review visualizations:
   open outputs/behavioral_profiles/affective/*.png

2. Review research brief:
   cat outputs/behavioral_profiles/affective/RESEARCH_BRIEF.md

3. Compare to baseline (if applicable):
   python3 scripts/compare_conditions.py baseline affective

4. Run analysis for next condition:
   ./scripts/run_complete_h1_h2_analysis.sh authority
```

---

## Features

### ✅ Automatic Prerequisites Check
- Verifies profile directory exists
- Checks for sufficient profiles (warns if < 40)
- Ensures median split classification present

### ✅ Interactive Overwrite Protection
If median split already exists, asks before recalculating:
```
⚠️  median_split_classification.json already exists
Overwrite existing classification? (y/N):
```

### ✅ Error Handling
Script stops if any step fails with clear error messages:
- Missing profile directory → instructions for profile aggregation
- Failed median split → calculation error reported
- Failed visualizations → generation error reported

### ✅ Comprehensive Summary
Shows key results immediately:
- Median sophistication value
- Group balance
- H1 effect size (Cohen's d)
- H2 correlation (r)
- Special pattern counts

---

## Running Multiple Conditions in Sequence

```bash
# Run all conditions sequentially
for condition in baseline affective authority urgency; do
    echo "Processing: $condition"
    ./scripts/run_complete_h1_h2_analysis.sh $condition
    echo ""
    sleep 2  # Brief pause between conditions
done
```

---

## Comparison to Baseline

After running a new condition, compare to baseline:

```bash
# Quick comparison (manual)
python3 << 'EOF'
import json
from pathlib import Path

baseline = json.loads(Path('outputs/behavioral_profiles/baseline/median_split_classification.json').read_text())
affective = json.loads(Path('outputs/behavioral_profiles/affective/median_split_classification.json').read_text())

print("BASELINE vs AFFECTIVE")
print("="*50)
print(f"Median:     {baseline['median_sophistication']:.3f} → {affective['median_sophistication']:.3f}")
print(f"H1 d:       {baseline['statistics']['disinhibition']['cohens_d']:.2f} → {affective['statistics']['disinhibition']['cohens_d']:.2f}")
print(f"H2 r:       {baseline['correlation']['sophistication_disinhibition']:.3f} → {affective['correlation']['sophistication_disinhibition']:.3f}")
EOF
```

---

## Troubleshooting

### Error: "Profile directory not found"
**Solution**: Run profile aggregation first:
```bash
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs/*/job_*_<intervention>_*.json \
    --profile-dir outputs/behavioral_profiles/<intervention>
```

### Error: "No profile files found"
**Solution**: Check job output pattern is correct:
```bash
# List available job files
ls outputs/single_prompt_jobs/*/job_*_<intervention>_*.json | head -5

# If none found, check job file naming
ls outputs/single_prompt_jobs/*/ | grep <intervention>
```

### Warning: "Low sample size"
**Impact**: Results less reliable with N < 40
**Solution**:
- Continue if N ≥ 30 (acceptable)
- Investigate if N < 30 (may need more jobs)

### Median split file already exists
**Options**:
- Type `n` to use existing classification (faster)
- Type `y` to recalculate (if you updated profiles)

---

## Script Architecture

### Original 3-Step Manual Process:
```bash
# OLD WAY (3 separate commands):
python3 scripts/calculate_median_split.py outputs/behavioral_profiles/affective
python3 scripts/create_h1_bar_chart.py affective
python3 scripts/create_h2_color_coded_scatters.py affective
python3 scripts/update_research_brief_median.py affective
```

### New 1-Step Automated Process:
```bash
# NEW WAY (1 command):
./scripts/run_complete_h1_h2_analysis.sh affective
```

The new script wraps all 4 steps with:
- Prerequisites checking
- Error handling
- Progress reporting
- Results summary

---

## Files Reference

### Main Script
- `scripts/run_complete_h1_h2_analysis.sh` - **One-command pipeline**

### Individual Scripts (called by main script)
- `scripts/calculate_median_split.py` - Stage 2
- `scripts/create_h1_bar_chart.py` - Stage 3a
- `scripts/create_h2_color_coded_scatters.py` - Stage 3b
- `scripts/update_research_brief_median.py` - Stage 3c

### Documentation
- `QUICK_START_H1_H2.md` - This file (quick reference)
- `H1_H2_ANALYSIS_GUIDE.md` - Detailed user guide
- `H1_H2_QUALITY_CONTROL.md` - Validation framework
- `H1_H2_REPLICATION_READY.md` - Go/no-go decision
- `ANALYTICS_PACKAGE_GUIDE.md` - Full pipeline documentation

---

## Quick Reference Commands

```bash
# Run complete analysis for one condition
./scripts/run_complete_h1_h2_analysis.sh <intervention>

# Run for multiple conditions
for cond in affective authority urgency; do
    ./scripts/run_complete_h1_h2_analysis.sh $cond
done

# View research brief
cat outputs/behavioral_profiles/<intervention>/RESEARCH_BRIEF.md

# Open visualizations
open outputs/behavioral_profiles/<intervention>/*.png

# Check statistics
jq '.statistics.disinhibition' outputs/behavioral_profiles/<intervention>/median_split_classification.json
```

---

## Success Criteria

Analysis is successful if you see:
- ✅ `PIPELINE COMPLETE!` message
- ✅ 5 output files created
- ✅ H1 Cohen's d reported
- ✅ H2 correlation r reported
- ✅ No error messages

---

**Ready to Go**: Run `./scripts/run_complete_h1_h2_analysis.sh <intervention>`

**Estimated Time**: 2-3 minutes per condition

**Support**: See `H1_H2_ANALYSIS_GUIDE.md` for detailed documentation
