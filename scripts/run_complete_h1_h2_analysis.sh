#!/bin/bash
# Complete H1/H2 Analysis Pipeline
# Runs median split classification + H1/H2 analysis in one step

if [ -z "$1" ]; then
    echo "Usage: $0 <intervention_name>"
    echo ""
    echo "Examples:"
    echo "  $0 baseline"
    echo "  $0 affective"
    echo "  $0 authority"
    echo "  $0 urgency"
    echo ""
    echo "This script will:"
    echo "  1. Calculate median split classification"
    echo "  2. Generate H1 visualizations (bar chart, summary table)"
    echo "  3. Generate H2 scatter plots (composite + all dimensions)"
    echo "  4. Generate research brief"
    echo "  5. Generate provider analysis (summary, H2 scatters, dimensions, heatmap, stats)"
    echo "  6. Run cross-provider statistical comparisons (ANOVA, pairwise t-tests)"
    echo ""
    echo "Output: 16 files (5 H1/H2 core + 8 provider analysis + 3 data exports)"
    exit 1
fi

INTERVENTION="$1"
PROFILE_DIR="outputs/behavioral_profiles/${INTERVENTION}"

echo "=========================================================================="
echo "COMPLETE H1/H2 ANALYSIS PIPELINE"
echo "=========================================================================="
echo "Intervention: ${INTERVENTION}"
echo "Profile Directory: ${PROFILE_DIR}"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# =============================================================================
# PREREQUISITE CHECKS
# =============================================================================

echo "=== PREREQUISITE CHECKS ==="
echo ""

# Check if profile directory exists
if [ ! -d "${PROFILE_DIR}" ]; then
    echo "❌ ERROR: Profile directory not found: ${PROFILE_DIR}"
    echo ""
    echo "You need to run profile aggregation first:"
    echo "  python3 scripts/update_behavioral_profiles.py \\"
    echo "    outputs/single_prompt_jobs/*/job_*_${INTERVENTION}_*.json \\"
    echo "    --profile-dir ${PROFILE_DIR}"
    exit 1
fi
echo "✓ Profile directory exists: ${PROFILE_DIR}"

# Check if profiles subdirectory exists and has files
if [ ! -d "${PROFILE_DIR}/profiles" ]; then
    echo "❌ ERROR: Profiles subdirectory not found: ${PROFILE_DIR}/profiles"
    exit 1
fi

PROFILE_COUNT=$(ls ${PROFILE_DIR}/profiles/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ ${PROFILE_COUNT} -eq 0 ]; then
    echo "❌ ERROR: No profile files found in ${PROFILE_DIR}/profiles/"
    echo ""
    echo "You need to run profile aggregation first:"
    echo "  python3 scripts/update_behavioral_profiles.py \\"
    echo "    outputs/single_prompt_jobs/*/job_*_${INTERVENTION}_*.json \\"
    echo "    --profile-dir ${PROFILE_DIR}"
    exit 1
fi
echo "✓ Found ${PROFILE_COUNT} profile files"

if [ ${PROFILE_COUNT} -lt 40 ]; then
    echo "⚠️  WARNING: Low sample size (${PROFILE_COUNT} < 40 models)"
    echo "   Analysis will proceed but results may be less reliable"
fi

echo ""

# =============================================================================
# STAGE 2: MEDIAN SPLIT CLASSIFICATION
# =============================================================================

echo "=== STAGE 2: MEDIAN SPLIT CLASSIFICATION ==="
echo ""

# Check if median split already exists
if [ -f "${PROFILE_DIR}/median_split_classification.json" ]; then
    echo "⚠️  median_split_classification.json already exists"
    echo ""
    read -p "Overwrite existing classification? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping median split recalculation, using existing file"
        echo ""
    else
        echo "Recalculating median split classification..."
        python3 scripts/calculate_median_split.py ${PROFILE_DIR}
        if [ $? -ne 0 ]; then
            echo "❌ ERROR: Median split calculation failed"
            exit 1
        fi
        echo ""
    fi
else
    echo "Calculating median split classification..."
    python3 scripts/calculate_median_split.py ${PROFILE_DIR}
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Median split calculation failed"
        exit 1
    fi
    echo ""
fi

# Verify median split file was created
if [ ! -f "${PROFILE_DIR}/median_split_classification.json" ]; then
    echo "❌ ERROR: median_split_classification.json was not created"
    exit 1
fi
echo "✓ Median split classification complete"

# Quick preview of classification results
echo ""
echo "Classification Summary:"
python3 -c "
import json
from pathlib import Path

intervention = '${INTERVENTION}'
profile_dir = Path(f'outputs/behavioral_profiles/{intervention}')
data = json.loads((profile_dir / 'median_split_classification.json').read_text())

print(f'  Models: {len(data[\"models\"])}')
print(f'  Median sophistication: {data[\"median_sophistication\"]:.3f}')
print(f'  High-Sophistication: n = {data[\"n_high_sophistication\"]}')
print(f'  Low-Sophistication: n = {data[\"n_low_sophistication\"]}')
print(f'  Group balance: {abs(data[\"n_high_sophistication\"] - data[\"n_low_sophistication\"])} model difference')
print(f'  Sophistication separation: d = {data[\"statistics\"][\"sophistication\"][\"cohens_d\"]:.2f}')
"

echo ""

# =============================================================================
# STAGE 3: H1/H2 VISUALIZATIONS AND RESEARCH BRIEF
# =============================================================================

echo "=== STAGE 3: H1/H2 ANALYSIS ==="
echo ""

echo "Step 3a: Generating H1 visualizations..."
python3 scripts/create_h1_bar_chart.py ${INTERVENTION}
if [ $? -ne 0 ]; then
    echo "❌ ERROR: H1 visualization generation failed"
    exit 1
fi
echo ""

echo "Step 3b: Generating H2 scatter plots..."
python3 scripts/create_h2_color_coded_scatters.py ${INTERVENTION}
if [ $? -ne 0 ]; then
    echo "❌ ERROR: H2 visualization generation failed"
    exit 1
fi
echo ""

echo "Step 3c: Generating research brief..."
python3 scripts/update_research_brief_median.py ${INTERVENTION}
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Research brief generation failed"
    exit 1
fi
echo ""

# =============================================================================
# STAGE 4: PROVIDER ANALYSIS
# =============================================================================

echo "=== STAGE 4: PROVIDER ANALYSIS ==="
echo ""

echo "Step 4a: Generating provider summary (4-panel visualization)..."
python3 scripts/create_provider_summary.py ${INTERVENTION}
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Provider summary generation failed"
    exit 1
fi
echo ""

echo "Step 4b: Generating provider H2 scatters (correlation by provider)..."
python3 scripts/create_provider_h2_scatters.py ${INTERVENTION}
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Provider H2 scatters generation failed"
    exit 1
fi
echo ""

echo "Step 4c: Generating comprehensive provider analysis..."
python3 scripts/analyze_all_models_by_provider.py ${INTERVENTION}
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Provider comprehensive analysis failed"
    exit 1
fi
echo ""

# =============================================================================
# STAGE 5: CROSS-PROVIDER STATISTICAL COMPARISONS
# =============================================================================

echo "=== STAGE 5: CROSS-PROVIDER COMPARISONS ==="
echo ""

echo "Step 5: Running cross-provider statistical comparisons (ANOVA, pairwise t-tests)..."
python3 scripts/analyze_provider_comparisons.py ${INTERVENTION}
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Cross-provider comparisons failed"
    exit 1
fi
echo ""

# =============================================================================
# STAGE 6: CROSS-CONDITION COMPARISON
# =============================================================================

echo "=== STAGE 6: CROSS-CONDITION COMPARISON ==="
echo ""

echo "Step 6: Updating cross-condition comparison..."
python3 scripts/update_cross_condition_comparison.py
if [ $? -ne 0 ]; then
    echo "⚠️  WARNING: Cross-condition comparison update failed (non-fatal)"
fi
echo ""

# =============================================================================
# COMPLETION AND SUMMARY
# =============================================================================

echo "=========================================================================="
echo "PIPELINE COMPLETE!"
echo "=========================================================================="
echo ""
echo "Output files created in: ${PROFILE_DIR}"
echo ""

# List all generated files
echo "Generated Files (Expected: 16 total):"
ls -lh ${PROFILE_DIR}/*.{png,md,json,csv,txt} 2>/dev/null | while read line; do
    filename=$(echo "$line" | awk '{print $9}')
    size=$(echo "$line" | awk '{print $5}')
    basename=$(basename "$filename")
    echo "  ✓ ${basename} (${size})"
done

# Count files
PNG_COUNT=$(ls ${PROFILE_DIR}/*.png 2>/dev/null | wc -l | tr -d ' ')
JSON_COUNT=$(ls ${PROFILE_DIR}/*.json 2>/dev/null | wc -l | tr -d ' ')
MD_COUNT=$(ls ${PROFILE_DIR}/*.md 2>/dev/null | wc -l | tr -d ' ')
CSV_COUNT=$(ls ${PROFILE_DIR}/*.csv 2>/dev/null | wc -l | tr -d ' ')
TXT_COUNT=$(ls ${PROFILE_DIR}/*.txt 2>/dev/null | wc -l | tr -d ' ')
TOTAL_COUNT=$((PNG_COUNT + JSON_COUNT + MD_COUNT + CSV_COUNT + TXT_COUNT))

echo ""
echo "File Count Summary:"
echo "  PNG files: ${PNG_COUNT}/10 (visualizations)"
echo "  JSON files: ${JSON_COUNT}/3 (data)"
echo "  CSV files: ${CSV_COUNT}/1 (export)"
echo "  TXT files: ${TXT_COUNT}/1 (report)"
echo "  MD files: ${MD_COUNT}/1 (brief)"
echo "  Total: ${TOTAL_COUNT}/16"

echo ""

# Show key statistics
echo "Key Results:"
python3 -c "
import json
from pathlib import Path
import numpy as np

intervention = '${INTERVENTION}'
profile_dir = Path(f'outputs/behavioral_profiles/{intervention}')
data = json.loads((profile_dir / 'median_split_classification.json').read_text())

print(f'  H1 (Group Difference):')
print(f'    - Cohen\\'s d = {data[\"statistics\"][\"disinhibition\"][\"cohens_d\"]:.2f}')
print(f'    - p-value = {data[\"statistics\"][\"disinhibition\"][\"p_value\"]:.6f}')
d = abs(data['statistics']['disinhibition']['cohens_d'])
effect = 'Large' if d >= 0.8 else 'Medium' if d >= 0.5 else 'Small'
print(f'    - Effect: {effect}')
print()
print(f'  H2 (Correlation):')
print(f'    - r = {data[\"correlation\"][\"sophistication_disinhibition\"]:.3f}')
r = abs(data['correlation']['sophistication_disinhibition'])
effect = 'Large' if r >= 0.5 else 'Medium' if r >= 0.3 else 'Small'
print(f'    - Effect: {effect}')

# Identify special patterns
borderline = [m for m in data['models'] if abs(m['sophistication'] - data['median_sophistication']) < 0.15]
print()
print(f'  Special Patterns:')
print(f'    - Borderline models: {len(borderline)}')

# Count constrained models
all_soph = [m['sophistication'] for m in data['models']]
all_disinhib = [m['disinhibition'] for m in data['models']]
z = np.polyfit(all_soph, all_disinhib, 1)
p = np.poly1d(z)
predicted = p(all_soph)
residuals = np.array(all_disinhib) - predicted
constrained = sum(1 for i, m in enumerate(data['models']) if m['sophistication'] > 6.5 and residuals[i] < -0.15)
print(f'    - Constrained models: {constrained}')

# Count outliers
residual_std = np.std(residuals)
outliers = sum(1 for r in residuals if abs(r) > 2 * residual_std)
print(f'    - Statistical outliers: {outliers}')
"

echo ""
echo "=========================================================================="
echo "NEXT STEPS"
echo "=========================================================================="
echo ""
echo "1. Review visualizations:"
echo "   open ${PROFILE_DIR}/*.png"
echo ""
echo "2. Review research brief:"
echo "   cat ${PROFILE_DIR}/RESEARCH_BRIEF.md"
echo ""
echo "3. Compare to baseline (if applicable):"
echo "   python3 scripts/compare_conditions.py baseline ${INTERVENTION}"
echo ""
echo "4. Run analysis for next condition:"
echo "   $0 <next_intervention_name>"
echo ""
