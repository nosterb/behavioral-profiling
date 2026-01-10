# H1/H2 Analysis Parameterization - COMPLETE

**Date**: 2026-01-09
**Status**: ✅ Complete and tested

---

## Summary

Successfully parameterized the entire H1/H2 analysis pipeline to work with any intervention condition. The three core scripts now accept an intervention name as a command-line argument and dynamically generate all visualizations and research briefs.

---

## Changes Made

### 1. `scripts/create_h1_bar_chart.py` ✅
**Changes**:
- Wrapped all code in `main()` function
- Added command-line argument parsing for intervention name
- Defaults to "baseline" if no argument provided
- Dynamic path construction: `outputs/behavioral_profiles/{intervention}/`

**Usage**:
```bash
python3 scripts/create_h1_bar_chart.py baseline
python3 scripts/create_h1_bar_chart.py affective
python3 scripts/create_h1_bar_chart.py authority
```

**Outputs**:
- `h1_bar_chart_comparison.png` - Side-by-side bar chart
- `h1_summary_table.png` - Statistical table

---

### 2. `scripts/create_h2_color_coded_scatters.py` ✅
**Changes**:
- Wrapped all code in `main()` function
- Added command-line argument parsing for intervention name
- Defaults to "baseline" if no argument provided
- Dynamic path construction: `outputs/behavioral_profiles/{intervention}/`
- Enhanced with three special pattern detection types:
  - **Borderline models** (within ±0.15 of median)
  - **Constrained models** (high sophistication, low disinhibition)
  - **Statistical outliers** (residual > 2 SD)

**Usage**:
```bash
python3 scripts/create_h2_color_coded_scatters.py baseline
python3 scripts/create_h2_color_coded_scatters.py affective
python3 scripts/create_h2_color_coded_scatters.py authority
```

**Outputs**:
- `h2_scatter_sophistication_composite.png` - Main correlation plot with all special patterns
- `h2_scatter_all_dimensions.png` - 2x2 grid with dimension-specific outliers

---

### 3. `scripts/update_research_brief_median.py` ✅
**Changes**:
- Wrapped all code in `main()` function
- Added command-line argument parsing for intervention name
- Defaults to "baseline" if no argument provided
- Dynamic path construction for input/output files
- Dynamic intervention name formatting (e.g., "affective" → "Affective Condition")
- Added **Notable Patterns** section documenting:
  - Borderline models
  - Constrained models
  - Statistical outliers
- Updated Discussion section to mention all three pattern types
- Updated Visualizations section to list all new plots
- Fixed all indentation errors from wrapping in `main()` function

**Usage**:
```bash
python3 scripts/update_research_brief_median.py baseline
python3 scripts/update_research_brief_median.py affective
python3 scripts/update_research_brief_median.py authority
```

**Outputs**:
- `RESEARCH_BRIEF.md` - Publication-ready research brief with:
  - H1 group comparison results
  - H2 correlation analysis
  - Notable patterns documentation
  - Discussion and implications

---

## New Files Created

### 1. `H1_H2_ANALYSIS_GUIDE.md` ✅
**Purpose**: Comprehensive user guide for running H1/H2 analysis pipeline

**Contents**:
- Prerequisites checklist
- Step-by-step pipeline instructions
- Complete examples for multiple interventions
- Expected output file sizes
- Special pattern detection explanation
- Troubleshooting section
- Quality assurance checklist
- Integration with Standard Analytics Package

---

### 2. `scripts/run_h1_h2_analysis.sh` ✅
**Purpose**: Automated shell script to run complete H1/H2 pipeline

**Features**:
- Validates prerequisites (profile directory, classification file)
- Runs all three scripts in order
- Reports completion status
- Lists output files
- Provides next steps

**Usage**:
```bash
chmod +x scripts/run_h1_h2_analysis.sh
./scripts/run_h1_h2_analysis.sh baseline
./scripts/run_h1_h2_analysis.sh affective
```

---

## Testing Results

All scripts tested successfully with baseline condition:

### Test 1: H1 Bar Charts
```bash
python3 scripts/create_h1_bar_chart.py baseline
✓ Created: h1_bar_chart_comparison.png (237 KB)
✓ Created: h1_summary_table.png (233 KB)
```

### Test 2: H2 Scatter Plots
```bash
python3 scripts/create_h2_color_coded_scatters.py baseline
✓ Created: h2_scatter_sophistication_composite.png (614 KB)
✓ Created: h2_scatter_all_dimensions.png (1.1 MB)
✓ Detected 3 borderline models
✓ Detected 3 constrained models (GPT-OSS-120B, GPT-5.2 Pro, O3)
✓ Detected 1 statistical outlier (Gemini-3-Pro-Preview)
```

### Test 3: Research Brief
```bash
python3 scripts/update_research_brief_median.py baseline
✓ Updated RESEARCH_BRIEF.md (13 KB)
✓ Includes Notable Patterns section
✓ All statistical tests properly formatted
```

### Test 4: Automated Pipeline
```bash
./scripts/run_h1_h2_analysis.sh baseline
✓ All three steps completed
✓ All output files generated
✓ Pipeline complete
```

---

## Special Pattern Detection

The H2 scatter plots now automatically detect and visually highlight three types of interesting patterns:

### Borderline Models (Orange Squares)
Models very close to the median split (±0.15), representing edge cases for sensitivity analysis.

**Baseline Examples**:
- Claude-4.1-Opus-Thinking: 5.892 (-0.038 from median)
- Claude-4-Opus: 5.924 (-0.006 from median)
- Claude-4-Opus-Thinking: 5.937 (+0.006 from median)

### Constrained Models (Cyan Diamonds)
High sophistication (>6.5) but below-predicted disinhibition (residual < -0.15), suggesting deliberate constraint strategies.

**Baseline Examples**:
- GPT-OSS-120B: soph=7.12, disinhib=1.49 (residual=-0.222)
- GPT-5.2 Pro: soph=7.34, disinhib=1.55 (residual=-0.193)
- O3: soph=7.18, disinhib=1.55 (residual=-0.172)

### Statistical Outliers (Red Circles)
Models with residuals > 2 SD from regression line, deviating substantially from the correlation.

**Baseline Examples**:
- Gemini-3-Pro-Preview: residual=+0.541 (above predicted)

---

## Usage Examples

### Running for Baseline
```bash
# Individual scripts
python3 scripts/create_h1_bar_chart.py baseline
python3 scripts/create_h2_color_coded_scatters.py baseline
python3 scripts/update_research_brief_median.py baseline

# Or use automated pipeline
./scripts/run_h1_h2_analysis.sh baseline
```

### Running for Affective Intervention
```bash
# Individual scripts
python3 scripts/create_h1_bar_chart.py affective
python3 scripts/create_h2_color_coded_scatters.py affective
python3 scripts/update_research_brief_median.py affective

# Or use automated pipeline
./scripts/run_h1_h2_analysis.sh affective
```

### Running for Authority Intervention
```bash
# Individual scripts
python3 scripts/create_h1_bar_chart.py authority
python3 scripts/create_h2_color_coded_scatters.py authority
python3 scripts/update_research_brief_median.py authority

# Or use automated pipeline
./scripts/run_h1_h2_analysis.sh authority
```

---

## Expected Outputs

For any intervention condition, the pipeline generates:

1. **H1 Visualizations** (2 files):
   - `h1_bar_chart_comparison.png` - Bar chart with error bars
   - `h1_summary_table.png` - Statistical table

2. **H2 Visualizations** (2 files):
   - `h2_scatter_sophistication_composite.png` - Main correlation plot
   - `h2_scatter_all_dimensions.png` - 4-subplot grid

3. **Research Brief** (1 file):
   - `RESEARCH_BRIEF.md` - Publication-ready markdown report

**Total**: 5 files per intervention condition

---

## Integration with Standard Analytics Package

This H1/H2 pipeline is now fully integrated into the Standard Analytics Package workflow:

**Complete Workflow**:
```bash
# Stage 1: Profile aggregation
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs/*/job_*_affective_*.json \
    --profile-dir outputs/behavioral_profiles/affective

# Stage 2: Median split classification
python3 scripts/calculate_median_split.py \
    outputs/behavioral_profiles/affective

# Stage 3: H1/H2 Analysis (THIS PIPELINE)
./scripts/run_h1_h2_analysis.sh affective

# Stage 4: Optional additional visualizations
python3 scripts/visualize_all_behavioral.py outputs/behavioral_profiles/affective/
```

---

## Quality Assurance

### Checklist ✅
- [x] All three scripts parameterized
- [x] Default to "baseline" if no argument provided
- [x] Dynamic path construction works
- [x] Error handling for missing directories
- [x] All indentation errors fixed
- [x] Tested with baseline condition
- [x] Automated pipeline script created
- [x] Comprehensive user guide created
- [x] Special pattern detection working
- [x] Research brief includes Notable Patterns section

### Files Modified ✅
- [x] `scripts/create_h1_bar_chart.py`
- [x] `scripts/create_h2_color_coded_scatters.py`
- [x] `scripts/update_research_brief_median.py`

### Files Created ✅
- [x] `H1_H2_ANALYSIS_GUIDE.md`
- [x] `scripts/run_h1_h2_analysis.sh`
- [x] `H1_H2_PARAMETERIZATION_COMPLETE.md` (this file)

---

## Next Steps for Users

To run H1/H2 analysis for a new intervention condition:

1. **Ensure prerequisites are met**:
   ```bash
   # Check that median split classification exists
   ls outputs/behavioral_profiles/affective/median_split_classification.json
   ```

2. **Run the automated pipeline**:
   ```bash
   ./scripts/run_h1_h2_analysis.sh affective
   ```

3. **Review outputs**:
   ```bash
   # View visualizations
   open outputs/behavioral_profiles/affective/*.png

   # Read research brief
   cat outputs/behavioral_profiles/affective/RESEARCH_BRIEF.md
   ```

4. **Check for interesting patterns**:
   - Identify borderline models (edge cases)
   - Identify constrained models (training strategies)
   - Identify statistical outliers (qualitative review)

---

## Documentation

All changes are fully documented in:
- **User Guide**: `H1_H2_ANALYSIS_GUIDE.md` (step-by-step instructions)
- **Standard Analytics Package**: `ANALYTICS_PACKAGE_GUIDE.md` (full pipeline context)
- **This Summary**: `H1_H2_PARAMETERIZATION_COMPLETE.md` (change log)

---

## Technical Notes

### Indentation Fixes
Fixed multiple indentation errors in `update_research_brief_median.py` when wrapping code in `main()` function:
- Line 172-176: for loop for individual correlations
- Line 192-194: for loop for borderline models
- Line 211-216: for loop with if statement for constrained models
- Line 218-220: for loop for constrained model reporting
- Line 222-226: if statement for constrained models text
- Line 234-239: for loop with if statement for outliers
- Line 241-244: for loop for outlier reporting
- Line 246-247: if statement for no outliers case
- Line 283-284: for loop for high-sophistication models
- Line 293-294: for loop for low-sophistication models

All fixed by ensuring proper 4-space indentation inside function bodies and loop blocks.

### Command-Line Argument Pattern
All three scripts follow the same pattern:
```python
def main():
    import sys

    if len(sys.argv) > 1:
        intervention = sys.argv[1]
    else:
        intervention = "baseline"

    profile_dir = Path(f"outputs/behavioral_profiles/{intervention}")

    if not profile_dir.exists():
        print(f"Error: Profile directory not found: {profile_dir}")
        print(f"Usage: python3 {sys.argv[0]} [intervention_name]")
        sys.exit(1)

    # ... rest of code ...

if __name__ == "__main__":
    main()
```

---

## Success Criteria Met ✅

All original objectives achieved:

1. ✅ **Parameterize H1 visualizations** - Done
2. ✅ **Parameterize H2 scatter plots** - Done
3. ✅ **Parameterize research brief generation** - Done
4. ✅ **Add special pattern detection** - Done (borderline, constrained, outliers)
5. ✅ **Document patterns in research brief** - Done (Notable Patterns section)
6. ✅ **Make repeatable for any condition** - Done (command-line arguments)
7. ✅ **Create user guide** - Done (H1_H2_ANALYSIS_GUIDE.md)
8. ✅ **Create automated pipeline** - Done (run_h1_h2_analysis.sh)
9. ✅ **Test with baseline** - Done (all scripts working)
10. ✅ **Document changes** - Done (this summary)

---

**Status**: Ready for use with any intervention condition
**Tested**: Baseline condition (2026-01-09)
**Documentation**: Complete
**Next Use Case**: Affective, Authority, Urgency, or other interventions

---

**Completion Date**: 2026-01-09
**Version**: 1.0
