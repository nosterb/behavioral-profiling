#!/bin/bash
# =============================================================================
# MASTER REGENERATION SCRIPT
# =============================================================================
# Regenerates ALL analysis outputs from raw data (job outputs + profiles)
# Ensures full reproducibility and auditability
#
# Usage:
#   ./scripts/regenerate_all.sh [--dry-run] [--condition COND] [--skip-judge]
#
# Prerequisites:
#   - Raw job outputs exist in outputs/single_prompt_jobs/
#   - Judge evaluations complete (or use --skip-judge to skip)
#   - Python 3.x with scipy, numpy, matplotlib
#
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DRY_RUN=false
SINGLE_CONDITION=""
SKIP_JUDGE=false
BASE_DIR="outputs/behavioral_profiles"

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --condition)
            SINGLE_CONDITION="$2"
            shift 2
            ;;
        --skip-judge)
            SKIP_JUDGE=true
            shift
            ;;
        --base-dir)
            BASE_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--condition COND] [--skip-judge] [--base-dir DIR]"
            echo ""
            echo "Options:"
            echo "  --dry-run       Show what would be done without executing"
            echo "  --condition     Regenerate only specified condition"
            echo "  --skip-judge    Skip judge evaluation step"
            echo "  --base-dir      Base directory for behavioral profiles (default: outputs/behavioral_profiles)"
            echo ""
            echo "Conditions: baseline, authority, urgency, minimal_steering, telemetryV3, reminder, naturalistic, naturalistic_50"
            echo ""
            echo "Examples:"
            echo "  $0 --condition naturalistic_r2"
            echo "  $0 --condition naturalistic_r2 --base-dir outputs/experiment/behavioral_profiles"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# All conditions in dependency order
ALL_CONDITIONS="baseline authority urgency minimal_steering telemetryV3 reminder naturalistic naturalistic_50"

# Select conditions to process
if [ -n "$SINGLE_CONDITION" ]; then
    CONDITIONS="$SINGLE_CONDITION"
else
    CONDITIONS="$ALL_CONDITIONS"
fi

echo "=========================================================================="
echo "MASTER REGENERATION PIPELINE"
echo "=========================================================================="
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Conditions: $CONDITIONS"
echo "Base directory: $BASE_DIR"
echo "Dry run: $DRY_RUN"
echo ""

# =============================================================================
# PHASE 0: PREREQUISITES CHECK
# =============================================================================
phase_header() {
    echo ""
    echo "=========================================================================="
    echo -e "${BLUE}PHASE $1: $2${NC}"
    echo "=========================================================================="
}

run_cmd() {
    local desc="$1"
    shift
    echo -e "${YELLOW}>> $desc${NC}"
    if [ "$DRY_RUN" = true ]; then
        echo "   [DRY RUN] $*"
    else
        "$@"
    fi
}

phase_header "0" "PREREQUISITES CHECK"

echo "Checking directory structure..."
if [ ! -d "outputs/single_prompt_jobs" ]; then
    echo -e "${RED}ERROR: outputs/single_prompt_jobs/ not found${NC}"
    exit 1
fi
echo -e "${GREEN}OK${NC}: Job outputs directory exists"

if [ ! -d "$BASE_DIR" ]; then
    echo -e "${YELLOW}Creating base directory: $BASE_DIR${NC}"
    mkdir -p "$BASE_DIR"
fi
echo -e "${GREEN}OK${NC}: Behavioral profiles directory exists ($BASE_DIR)"

# =============================================================================
# PHASE 1: PROFILE AGGREGATION (per condition)
# =============================================================================
phase_header "1" "PROFILE AGGREGATION"

for COND in $CONDITIONS; do
    echo ""
    echo "--- Condition: $COND ---"

    PROFILE_DIR="$BASE_DIR/$COND"

    run_cmd "Aggregating profiles for $COND" \
        python3 scripts/update_behavioral_profiles.py \
            outputs/single_prompt_jobs --recursive \
            --condition "$COND" \
            --profile-dir "$PROFILE_DIR"
done

# =============================================================================
# PHASE 2: H1/H2 ANALYSIS (per condition)
# =============================================================================
phase_header "2" "H1/H2 ANALYSIS PIPELINE"

for COND in $CONDITIONS; do
    echo ""
    echo "--- Condition: $COND ---"

    PROFILE_DIR="$BASE_DIR/$COND"

    # Check if profiles exist
    if [ ! -d "$PROFILE_DIR/profiles" ]; then
        echo -e "${YELLOW}SKIP${NC}: No profiles for $COND"
        continue
    fi

    PROFILE_COUNT=$(ls "$PROFILE_DIR/profiles"/*.json 2>/dev/null | wc -l | tr -d ' ')
    if [ "$PROFILE_COUNT" -lt 10 ]; then
        echo -e "${YELLOW}SKIP${NC}: Insufficient profiles for $COND ($PROFILE_COUNT < 10)"
        continue
    fi

    echo "Found $PROFILE_COUNT profiles"

    # Stage 2.1: Median split classification
    run_cmd "Calculating median split for $COND" \
        python3 scripts/calculate_median_split.py "$PROFILE_DIR"

    # Stage 2.2: H1 visualizations
    run_cmd "Generating H1 visualizations for $COND" \
        python3 scripts/create_h1_bar_chart.py "$COND" --base-dir "$BASE_DIR"

    # Stage 2.3: H2 visualizations
    run_cmd "Generating H2 visualizations for $COND" \
        python3 scripts/create_h2_color_coded_scatters.py "$COND" --base-dir "$BASE_DIR"

    # Stage 2.4: Research brief
    run_cmd "Generating research brief for $COND" \
        python3 scripts/generate_research_brief_v2.py "$COND" --base-dir "$BASE_DIR"

    # Stage 2.5: Provider analysis
    run_cmd "Generating provider summary for $COND" \
        python3 scripts/create_provider_summary.py "$COND" --base-dir "$BASE_DIR"

    run_cmd "Generating provider H2 scatters for $COND" \
        python3 scripts/create_provider_h2_scatters.py "$COND" --base-dir "$BASE_DIR"

    run_cmd "Generating comprehensive provider analysis for $COND" \
        python3 scripts/analyze_all_models_by_provider.py "$COND" --base-dir "$BASE_DIR"

    # Stage 2.6: Cross-provider comparisons
    run_cmd "Running cross-provider comparisons for $COND" \
        python3 scripts/analyze_provider_comparisons.py "$COND" --base-dir "$BASE_DIR"
done

# =============================================================================
# PHASE 3: STATISTICAL ASSUMPTIONS & ROBUSTNESS
# =============================================================================
phase_header "3" "STATISTICAL ASSUMPTIONS & ROBUSTNESS"

for COND in $CONDITIONS; do
    PROFILE_DIR="$BASE_DIR/$COND"

    if [ ! -f "$PROFILE_DIR/median_split_classification.json" ]; then
        echo -e "${YELLOW}SKIP${NC}: No median split for $COND"
        continue
    fi

    echo ""
    echo "--- Condition: $COND ---"

    # Statistical assumptions
    run_cmd "Checking statistical assumptions for $COND" \
        python3 scripts/check_statistical_assumptions.py --condition "$COND" --base-dir "$BASE_DIR" || true

    # Outlier sensitivity
    run_cmd "Analyzing outlier sensitivity for $COND" \
        python3 scripts/analyze_outliers_removed.py "$COND" --force --base-dir "$BASE_DIR" || true

    # Judge agreement per-condition
    run_cmd "Analyzing judge agreement for $COND" \
        python3 scripts/check_judge_agreement.py --condition "$COND" --base-dir "$BASE_DIR" || true
done

# =============================================================================
# PHASE 4: CROSS-CONDITION ANALYSIS
# =============================================================================
phase_header "4" "CROSS-CONDITION ANALYSIS"

if [ -z "$SINGLE_CONDITION" ]; then
    run_cmd "Updating cross-condition comparison" \
        python3 scripts/update_cross_condition_comparison.py || true

    run_cmd "Running repeated-measures ANOVA" \
        python3 scripts/run_repeated_measures_anova.py --both || true

    run_cmd "Analyzing cross-condition patterns" \
        python3 scripts/analyze_cross_condition_patterns.py || true

    run_cmd "Consolidating statistical assumptions" \
        python3 scripts/consolidate_statistical_assumptions.py || true

    run_cmd "Analyzing provider balance (all conditions)" \
        python3 scripts/analyze_provider_balance.py --all || true

    run_cmd "Consolidating judge agreement" \
        python3 scripts/check_judge_agreement.py --all || true

    run_cmd "Auditing job metrics" \
        python3 scripts/audit_job_metrics.py || true
else
    echo "Skipping cross-condition analysis (single condition mode)"
fi

# =============================================================================
# PHASE 5: BERT VALIDATION (if applicable)
# =============================================================================
phase_header "5" "BERT VALIDATION"

BERT_SCRIPT="outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_validation.py"

if [ -f "$BERT_SCRIPT" ]; then
    for COND in $CONDITIONS; do
        PROFILE_DIR="$BASE_DIR/$COND"

        if [ ! -f "$PROFILE_DIR/median_split_classification.json" ]; then
            continue
        fi

        echo ""
        echo "--- Condition: $COND ---"

        run_cmd "Running BERT validation for $COND" \
            python3 "$BERT_SCRIPT" --condition "$COND" || true

        run_cmd "Running BERT soph/disin validation for $COND" \
            python3 "outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/run_bert_soph_disin_validation.py" --condition "$COND" || true
    done
else
    echo "BERT validation script not found, skipping"
fi

# =============================================================================
# PHASE 6: RESEARCH SYNTHESIS
# =============================================================================
phase_header "6" "RESEARCH SYNTHESIS"

if [ -z "$SINGLE_CONDITION" ]; then
    run_cmd "Regenerating BERT validation brief" \
        python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/regenerate_validation_reports.py || true

    run_cmd "Regenerating main research brief" \
        python3 scripts/regenerate_main_brief.py || true
else
    echo "Skipping research synthesis (single condition mode)"
fi

# =============================================================================
# PHASE 7: AUDIT COMPLIANCE CHECK
# =============================================================================
phase_header "7" "AUDIT COMPLIANCE CHECK"

run_cmd "Checking audit compliance" \
    python3 scripts/check_audit_compliance.py --full-report || true

# =============================================================================
# COMPLETION SUMMARY
# =============================================================================
echo ""
echo "=========================================================================="
echo -e "${GREEN}REGENERATION COMPLETE${NC}"
echo "=========================================================================="
echo ""
echo "Outputs regenerated for conditions: $CONDITIONS"
echo ""
echo "Verify outputs:"
echo "  - Per-condition briefs: outputs/behavioral_profiles/<condition>/RESEARCH_BRIEF.md"
echo "  - Cross-condition: outputs/behavioral_profiles/research_synthesis/cross_condition/"
echo "  - Main brief: outputs/behavioral_profiles/research_synthesis/MAIN_RESEARCH_BRIEF.md"
echo ""
echo "Run audit check:"
echo "  python3 scripts/check_audit_compliance.py --json"
echo ""
