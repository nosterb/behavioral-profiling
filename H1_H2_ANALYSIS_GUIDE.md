# H1/H2 Analysis Pipeline Guide

**Purpose**: Complete workflow for generating H1 (group comparison) and H2 (correlation) analysis with visualizations and research brief for any intervention condition.

**Last Updated**: 2026-01-09

---

## Prerequisites

Before running this analysis pipeline, ensure you have:

1. ✅ Completed median split classification: `median_split_classification.json` exists
2. ✅ Profile directory with behavioral profiles for all models
3. ✅ Python dependencies installed (matplotlib, numpy, scipy, seaborn)

**Verify prerequisites**:
```bash
# Check if classification file exists
ls -lh outputs/behavioral_profiles/baseline/median_split_classification.json

# Check profile count
ls outputs/behavioral_profiles/baseline/profiles/*.json | wc -l
```

---

## Pipeline Overview

The H1/H2 analysis pipeline consists of three scripts that must be run in order:

1. **`create_h1_bar_chart.py`** - Generates H1 group comparison visualizations
2. **`create_h2_color_coded_scatters.py`** - Generates H2 correlation scatter plots with special pattern detection
3. **`update_research_brief_median.py`** - Generates publication-ready research brief

---

## Step 1: Generate H1 Visualizations

**Purpose**: Create bar charts and statistical tables comparing High-Sophistication vs Low-Sophistication groups.

**Command**:
```bash
python3 scripts/create_h1_bar_chart.py <intervention_name>
```

**Examples**:
```bash
# Baseline condition (no intervention)
python3 scripts/create_h1_bar_chart.py baseline

# Affective intervention
python3 scripts/create_h1_bar_chart.py affective

# Authority intervention
python3 scripts/create_h1_bar_chart.py authority

# Urgency intervention
python3 scripts/create_h1_bar_chart.py urgency
```

**Output Files**:
- `outputs/behavioral_profiles/<intervention>/h1_bar_chart_comparison.png` - Side-by-side bar chart with error bars
- `outputs/behavioral_profiles/<intervention>/h1_summary_table.png` - Statistical summary table

**What's Shown**:
- Disinhibition composite (primary outcome)
- Four disinhibition dimensions (transgression, aggression, tribalism, grandiosity)
- Group means with standard deviation error bars
- Statistical significance markers (*** p < .001)
- Cohen's d effect sizes above each comparison

**Verification**:
```bash
# Check output files exist
ls -lh outputs/behavioral_profiles/baseline/h1_*.png

# Expected output:
# h1_bar_chart_comparison.png (~200-300 KB)
# h1_summary_table.png (~100-200 KB)
```

---

## Step 2: Generate H2 Scatter Plots

**Purpose**: Create correlation scatter plots showing sophistication-disinhibition relationship with special pattern detection.

**Command**:
```bash
python3 scripts/create_h2_color_coded_scatters.py <intervention_name>
```

**Examples**:
```bash
# Baseline condition
python3 scripts/create_h2_color_coded_scatters.py baseline

# Affective intervention
python3 scripts/create_h2_color_coded_scatters.py affective

# Authority intervention
python3 scripts/create_h2_color_coded_scatters.py authority
```

**Output Files**:
- `outputs/behavioral_profiles/<intervention>/h2_scatter_sophistication_composite.png` - Main correlation plot
- `outputs/behavioral_profiles/<intervention>/h2_scatter_all_dimensions.png` - 2x2 grid with all four dimensions

**What's Shown**:

### Main Composite Plot Features:
- **Green circles**: High-Sophistication models (normal)
- **Red circles**: Low-Sophistication models (normal)
- **Orange squares**: Borderline models (within ±0.15 of median split)
- **Cyan diamonds**: Constrained models (high sophistication, low disinhibition)
- **Red circle outlines**: Statistical outliers (residual > 2 SD)
- **Purple dashed line**: Median split threshold
- **Orange shaded zone**: Borderline region (±0.15)
- **Black dashed line**: Regression line (best fit)
- **Green/Red X markers**: Group means

### All Dimensions Plot Features:
- 2x2 grid showing transgression, aggression, tribalism, grandiosity
- Borderline models labeled in each subplot
- Dimension-specific outliers highlighted
- Individual correlation statistics (r, d) for each dimension

**Verification**:
```bash
# Check output files exist
ls -lh outputs/behavioral_profiles/baseline/h2_scatter_*.png

# Expected output:
# h2_scatter_sophistication_composite.png (~500-700 KB)
# h2_scatter_all_dimensions.png (~1.0-1.2 MB)
```

**Expected Console Output**:
```
Intervention: baseline
Loading median split classification data...
Loaded 46 models
Median sophistication: 5.930
High-Sophistication: n=23
Low-Sophistication: n=23

Creating color-coded scatter plots with outlier detection...
✓ Created: outputs/behavioral_profiles/baseline/h2_scatter_sophistication_composite.png
  - Borderline models: 3 (within ±0.15 of median)
    • Claude-4.1-Opus-Thinking (Thinking): 5.892 (-0.038 from median)
    • Claude-4-Opus: 5.924 (-0.006 from median)
    • Claude-4-Opus-Thinking (Thinking): 5.937 (+0.006 from median)
  - Constrained models: 3 (high-soph > 6.5, residual < -0.15)
    • GPT-OSS-120B: soph=7.122, disinhib=1.491, residual=-0.222
    • GPT-5.2 Pro: soph=7.340, disinhib=1.550, residual=-0.193
    • O3: soph=7.177, disinhib=1.548, residual=-0.172
  - Statistical outliers: 1 (residual > 2 SD)
  - Top outliers labeled:
    • Gemini-3-Pro-Preview: residual = +0.541
✓ Created: outputs/behavioral_profiles/baseline/h2_scatter_all_dimensions.png
```

---

## Step 3: Generate Research Brief

**Purpose**: Create publication-ready research brief with comprehensive H1/H2 statistical reporting and notable pattern documentation.

**Command**:
```bash
python3 scripts/update_research_brief_median.py <intervention_name>
```

**Examples**:
```bash
# Baseline condition
python3 scripts/update_research_brief_median.py baseline

# Affective intervention
python3 scripts/update_research_brief_median.py affective

# Authority intervention
python3 scripts/update_research_brief_median.py authority
```

**Output File**:
- `outputs/behavioral_profiles/<intervention>/RESEARCH_BRIEF.md` - Comprehensive markdown report

**What's Included**:

### 1. Study Overview
- Date, condition name, sample size
- Provider breakdown
- Hypothesis statements (H1 and H2)

### 2. Methods Section
- Classification approach (median split)
- Measurement definitions (9 behavioral dimensions)
- Statistical analysis plan (t-tests, correlations, effect sizes)

### 3. Results Section

**H1: Group Comparison**
- Disinhibition composite (primary outcome) with M, SD, t-test, p-value, Cohen's d
- Individual disinhibition dimensions table (transgression, aggression, tribalism, grandiosity)
- Sophistication dimensions (manipulation check)
- Other behavioral dimensions (warmth, formality, hedging)

**H2: Correlation Analysis**
- Sophistication-disinhibition correlation (r, p-value)
- Individual dimension correlations

**Notable Patterns** (NEW)
- **Borderline models**: Models within ±0.15 of median (edge cases for sensitivity analysis)
- **Constrained models**: High sophistication but low disinhibition (deliberate constraint strategies)
- **Statistical outliers**: Models deviating >2 SD from regression line (qualitative review needed)

### 4. Discussion Section
- Hypothesis support summary
- Effect size interpretation
- Key findings and implications
- Notable exceptions discussion

### 5. Supporting Files Section
- Data files list
- Classification lists (high/low sophistication models)
- Analysis scripts
- Visualization files

**Verification**:
```bash
# Check research brief exists
ls -lh outputs/behavioral_profiles/baseline/RESEARCH_BRIEF.md

# Preview first 50 lines
head -50 outputs/behavioral_profiles/baseline/RESEARCH_BRIEF.md

# Check for key sections
grep "^##" outputs/behavioral_profiles/baseline/RESEARCH_BRIEF.md

# Expected sections:
# ## Hypotheses
# ## Methods
# ## Results
# ## Discussion
# ## Supporting Files
```

**Expected Console Output**:
```
✓ Updated RESEARCH_BRIEF.md for baseline
  - Focused on H1 (group differences) and H2 (correlations)
  - Industry-standard statistical reporting
  - Supporting files listed at bottom
  - Ready for publication/presentation
```

---

## Complete Pipeline Example

### Running Analysis for Baseline Condition

```bash
# Step 1: H1 visualizations
python3 scripts/create_h1_bar_chart.py baseline

# Step 2: H2 scatter plots with special pattern detection
python3 scripts/create_h2_color_coded_scatters.py baseline

# Step 3: Research brief
python3 scripts/update_research_brief_median.py baseline

# Verify all outputs
ls -lh outputs/behavioral_profiles/baseline/*.{png,md}
```

### Running Analysis for Affective Intervention

```bash
# Step 1: H1 visualizations
python3 scripts/create_h1_bar_chart.py affective

# Step 2: H2 scatter plots
python3 scripts/create_h2_color_coded_scatters.py affective

# Step 3: Research brief
python3 scripts/update_research_brief_median.py affective

# Verify all outputs
ls -lh outputs/behavioral_profiles/affective/*.{png,md}
```

### Running Analysis for Authority Intervention

```bash
# Step 1: H1 visualizations
python3 scripts/create_h1_bar_chart.py authority

# Step 2: H2 scatter plots
python3 scripts/create_h2_color_coded_scatters.py authority

# Step 3: Research brief
python3 scripts/update_research_brief_median.py authority

# Verify all outputs
ls -lh outputs/behavioral_profiles/authority/*.{png,md}
```

---

## Automated Pipeline Script

You can automate the entire pipeline with a shell script:

**Save as `scripts/run_h1_h2_analysis.sh`**:
```bash
#!/bin/bash
# Complete H1/H2 analysis pipeline for any intervention

if [ -z "$1" ]; then
    echo "Usage: $0 <intervention_name>"
    echo "Example: $0 baseline"
    echo "Example: $0 affective"
    exit 1
fi

INTERVENTION="$1"
PROFILE_DIR="outputs/behavioral_profiles/${INTERVENTION}"

# Check if profile directory exists
if [ ! -d "${PROFILE_DIR}" ]; then
    echo "Error: Profile directory not found: ${PROFILE_DIR}"
    exit 1
fi

# Check if classification file exists
if [ ! -f "${PROFILE_DIR}/median_split_classification.json" ]; then
    echo "Error: median_split_classification.json not found"
    echo "Run calculate_median_split.py first"
    exit 1
fi

echo "========================================="
echo "H1/H2 Analysis Pipeline"
echo "Intervention: ${INTERVENTION}"
echo "========================================="
echo ""

echo "Step 1: Generating H1 visualizations..."
python3 scripts/create_h1_bar_chart.py ${INTERVENTION}
echo ""

echo "Step 2: Generating H2 scatter plots..."
python3 scripts/create_h2_color_coded_scatters.py ${INTERVENTION}
echo ""

echo "Step 3: Generating research brief..."
python3 scripts/update_research_brief_median.py ${INTERVENTION}
echo ""

echo "========================================="
echo "Pipeline Complete!"
echo "========================================="
echo ""
echo "Output files:"
ls -lh ${PROFILE_DIR}/*.{png,md} 2>/dev/null
echo ""
echo "Next steps:"
echo "  1. Review visualizations: open ${PROFILE_DIR}/*.png"
echo "  2. Review research brief: cat ${PROFILE_DIR}/RESEARCH_BRIEF.md"
echo "  3. Check for interesting patterns in borderline/constrained/outlier models"
```

**Make executable**:
```bash
chmod +x scripts/run_h1_h2_analysis.sh
```

**Usage**:
```bash
# Run for baseline
./scripts/run_h1_h2_analysis.sh baseline

# Run for affective
./scripts/run_h1_h2_analysis.sh affective

# Run for authority
./scripts/run_h1_h2_analysis.sh authority
```

---

## Expected Output File Sizes

For reference (baseline condition):

```
h1_bar_chart_comparison.png          ~250 KB
h1_summary_table.png                 ~150 KB
h2_scatter_sophistication_composite.png  ~614 KB
h2_scatter_all_dimensions.png        ~1.1 MB
RESEARCH_BRIEF.md                    ~12 KB
```

---

## Special Pattern Detection

The H2 scatter plots now automatically detect and highlight three types of special patterns:

### 1. Borderline Models
**Definition**: Models within ±0.15 of median sophistication score
**Significance**: Edge cases that could be classified either way; important for sensitivity analysis
**Visual Marker**: Orange squares with labels
**Example (Baseline)**:
- Claude-4.1-Opus-Thinking: 5.892 (just below median of 5.930)
- Claude-4-Opus: 5.924 (almost exactly at median)
- Claude-4-Opus-Thinking: 5.937 (just above median)

### 2. Constrained Models
**Definition**: Models with high sophistication (>6.5) but below-predicted disinhibition (residual < -0.15)
**Significance**: Suggests deliberate constraint strategies despite high capability
**Visual Marker**: Cyan diamonds with labels
**Example (Baseline)**:
- GPT-OSS-120B: sophistication=7.12, disinhibition=1.49 (residual=-0.222)
- GPT-5.2 Pro: sophistication=7.34, disinhibition=1.55 (residual=-0.193)
- O3: sophistication=7.18, disinhibition=1.55 (residual=-0.172)

### 3. Statistical Outliers
**Definition**: Models with residuals > 2 SD from regression line
**Significance**: Deviate substantially from correlation; warrant qualitative review
**Visual Marker**: Red circle outlines with yellow labels
**Example (Baseline)**:
- Gemini-3-Pro-Preview: residual=+0.541 (above predicted disinhibition)

---

## Troubleshooting

### Error: "Profile directory not found"
**Solution**: Create the profile directory first and ensure median split classification has been run
```bash
mkdir -p outputs/behavioral_profiles/<intervention>
python3 scripts/calculate_median_split.py outputs/behavioral_profiles/<intervention>
```

### Error: "median_split_classification.json not found"
**Solution**: Run the median split classification first
```bash
python3 scripts/calculate_median_split.py outputs/behavioral_profiles/<intervention>
```

### Error: "No module named 'matplotlib'"
**Solution**: Install required dependencies
```bash
pip install matplotlib numpy scipy seaborn
```

### Error: IndentationError
**Solution**: Ensure you're using Python 3 and that all scripts have consistent indentation
```bash
python3 --version  # Should be 3.7 or higher
```

---

## Quality Assurance Checklist

After running the pipeline, verify:

- [ ] All 5 output files generated (2 H1 PNGs, 2 H2 PNGs, 1 RESEARCH_BRIEF.md)
- [ ] H1 bar chart shows all 5 dimensions (disinhibition composite + 4 individual)
- [ ] H2 composite plot shows all special patterns (borderline, constrained, outliers)
- [ ] H2 all-dimensions plot shows 4 subplots (transgression, aggression, tribalism, grandiosity)
- [ ] Research brief includes Notable Patterns section
- [ ] Research brief lists correct intervention name in title
- [ ] Research brief has properly formatted statistical tests (t(44) = ..., p = ..., d = ...)
- [ ] Console output reports expected model counts for each pattern type

---

## Integration with Standard Analytics Package

This H1/H2 pipeline is part of the broader Standard Analytics Package documented in `ANALYTICS_PACKAGE_GUIDE.md`.

**Full workflow**:
1. Profile aggregation (`update_behavioral_profiles.py`)
2. Median split classification (`calculate_median_split.py`)
3. **→ H1/H2 Analysis (this guide)** ←
4. Optional: Additional visualizations (`visualize_all_behavioral.py`, etc.)

---

## References

- **Standard Analytics Package**: `ANALYTICS_PACKAGE_GUIDE.md`
- **Median Split Classification**: `scripts/calculate_median_split.py`
- **Example Research Brief**: `outputs/behavioral_profiles/baseline/RESEARCH_BRIEF.md`
- **Baseline Results**: First fully analyzed condition using this pipeline

---

**Document Version**: 1.0
**Last Updated**: 2026-01-09
**Scripts**: `create_h1_bar_chart.py`, `create_h2_color_coded_scatters.py`, `update_research_brief_median.py`
