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
