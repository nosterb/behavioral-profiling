#!/bin/bash
# Job Completion Script
# Runs all incomplete jobs for each condition and re-aggregates profiles
#
# Usage:
#   ./scripts/run_completion_jobs.sh              # Run all conditions
#   ./scripts/run_completion_jobs.sh minimal_steering  # Run single condition
#   ./scripts/run_completion_jobs.sh --dry-run    # Preview commands only
#
# Generated: 2026-01-19

set -e

DRY_RUN=false
CONDITION=""
MAX_PARALLEL=3

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --max-parallel)
            MAX_PARALLEL="$2"
            shift 2
            ;;
        *)
            CONDITION="$1"
            shift
            ;;
    esac
done

# Job counts
declare -A JOB_COUNTS
JOB_COUNTS[minimal_steering]=16
JOB_COUNTS[telemetryV3]=14
JOB_COUNTS[reminder]=2
JOB_COUNTS[naturalistic]=6
JOB_COUNTS[naturalistic_50]=8

# Conditions to process
if [[ -n "$CONDITION" ]]; then
    CONDITIONS=("$CONDITION")
else
    CONDITIONS=(minimal_steering telemetryV3 reminder naturalistic naturalistic_50)
fi

echo "================================================"
echo "JOB COMPLETION SCRIPT"
echo "================================================"
echo ""
echo "Conditions to process: ${CONDITIONS[*]}"
echo "Max parallel jobs: $MAX_PARALLEL"
echo "Dry run: $DRY_RUN"
echo ""

# Calculate total
TOTAL_JOBS=0
for cond in "${CONDITIONS[@]}"; do
    TOTAL_JOBS=$((TOTAL_JOBS + JOB_COUNTS[$cond]))
done
echo "Total jobs to run: $TOTAL_JOBS"
echo ""

run_cmd() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY RUN] $*"
    else
        echo "[RUNNING] $*"
        "$@"
    fi
}

# Phase 1: Run incomplete jobs
echo "================================================"
echo "PHASE 1: RUN INCOMPLETE JOBS"
echo "================================================"

for cond in "${CONDITIONS[@]}"; do
    JOB_LIST="payload/job_lists/incomplete_${cond}.yaml"

    if [[ ! -f "$JOB_LIST" ]]; then
        echo "SKIP: Job list not found: $JOB_LIST"
        continue
    fi

    echo ""
    echo "--- ${cond^^} (${JOB_COUNTS[$cond]} jobs) ---"
    run_cmd python3 scripts/run_jobs_parallel.py "$JOB_LIST" --max-parallel "$MAX_PARALLEL" --skip-behavioral-prompts
done

# Phase 2: Re-aggregate profiles
echo ""
echo "================================================"
echo "PHASE 2: RE-AGGREGATE PROFILES"
echo "================================================"

for cond in "${CONDITIONS[@]}"; do
    echo ""
    echo "--- Aggregating $cond ---"
    run_cmd python3 scripts/update_behavioral_profiles.py \
        outputs/single_prompt_jobs --recursive \
        --condition "$cond" \
        --profile-dir "outputs/behavioral_profiles/$cond"
done

# Phase 3: Re-run H1/H2 analysis
echo ""
echo "================================================"
echo "PHASE 3: RE-RUN H1/H2 ANALYSIS"
echo "================================================"

for cond in "${CONDITIONS[@]}"; do
    echo ""
    echo "--- H1/H2 Analysis: $cond ---"
    run_cmd ./scripts/run_complete_h1_h2_analysis.sh "$cond"
done

# Phase 4: Re-run statistical assumptions and judge agreement
echo ""
echo "================================================"
echo "PHASE 4: UPDATE STATISTICAL ANALYSES"
echo "================================================"

echo "--- Statistical Assumptions ---"
run_cmd python3 scripts/check_statistical_assumptions.py --all

echo ""
echo "--- Judge Agreement ---"
run_cmd python3 scripts/check_judge_agreement.py --all

# Phase 5: Update cross-condition documents
echo ""
echo "================================================"
echo "PHASE 5: UPDATE CROSS-CONDITION DOCS"
echo "================================================"

run_cmd python3 scripts/update_cross_condition_comparison.py

echo ""
echo "================================================"
echo "COMPLETION SUMMARY"
echo "================================================"
echo ""
echo "Jobs completed: $TOTAL_JOBS"
echo "Conditions updated: ${#CONDITIONS[@]}"
echo ""
echo "Next steps:"
echo "  1. Review updated briefs in outputs/behavioral_profiles/<condition>/RESEARCH_BRIEF.md"
echo "  2. Regenerate main brief: python3 scripts/regenerate_main_brief.py"
echo "  3. Sync to CDN: python3 scripts/sync_research_assets.py --invalidate"
