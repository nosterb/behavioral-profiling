#!/bin/bash
#
# Master workflow script for regenerating and auditing statistics documents.
#
# This script ensures CONSOLIDATED_STATISTICS.md and MAIN_RESEARCH_BRIEF.md
# are both up-to-date and consistent with their source JSON files.
#
# Usage:
#   ./scripts/regenerate_and_audit.sh           # Full regeneration + audit
#   ./scripts/regenerate_and_audit.sh --dry-run # Preview changes only
#   ./scripts/regenerate_and_audit.sh --audit   # Audit only (no regeneration)
#

set -e

DRY_RUN=false
AUDIT_ONLY=false
OUTPUT_DIR="outputs/behavioral_profiles/research_synthesis"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --audit)
            AUDIT_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run] [--audit]"
            exit 1
            ;;
    esac
done

echo "=============================================="
echo "STATISTICS REGENERATION AND AUDIT WORKFLOW"
echo "=============================================="
echo "Date: $(date +%Y-%m-%d\ %H:%M:%S)"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "Mode: DRY RUN (no changes will be made)"
    echo ""
fi

if [ "$AUDIT_ONLY" = true ]; then
    echo "Mode: AUDIT ONLY (no regeneration)"
    echo ""
fi

# Step 1: Regenerate CONSOLIDATED_STATISTICS.md
if [ "$AUDIT_ONLY" = false ]; then
    echo "Step 1: Regenerating CONSOLIDATED_STATISTICS.md..."
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY RUN] Would run: python3 scripts/generate_consolidated_statistics.py"
    else
        python3 scripts/generate_consolidated_statistics.py
    fi
    echo ""
fi

# Step 2: Regenerate MAIN_RESEARCH_BRIEF.md
if [ "$AUDIT_ONLY" = false ]; then
    echo "Step 2: Regenerating MAIN_RESEARCH_BRIEF.md..."
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY RUN] Would run: python3 scripts/regenerate_main_brief_v2.py"
        python3 scripts/regenerate_main_brief_v2.py --dry-run 2>&1 | head -20
    else
        python3 scripts/regenerate_main_brief_v2.py
    fi
    echo ""
fi

# Step 3: Run consistency audit
echo "Step 3: Running statistics consistency audit..."
AUDIT_OUTPUT="$OUTPUT_DIR/audit_report_$(date +%Y%m%d).json"
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would run audit and save to: $AUDIT_OUTPUT"
    python3 scripts/audit_statistics_consistency.py
else
    python3 scripts/audit_statistics_consistency.py --output "$AUDIT_OUTPUT"
fi
echo ""

# Step 4: Summary
echo "=============================================="
echo "WORKFLOW COMPLETE"
echo "=============================================="

if [ "$DRY_RUN" = false ] && [ "$AUDIT_ONLY" = false ]; then
    echo "Files regenerated:"
    echo "  - $OUTPUT_DIR/CONSOLIDATED_STATISTICS.md"
    echo "  - $OUTPUT_DIR/MAIN_RESEARCH_BRIEF.md"
    echo ""
    echo "Audit report:"
    echo "  - $AUDIT_OUTPUT"
    echo ""
    echo "Next steps:"
    echo "  1. Review the audit report for any mismatches"
    echo "  2. Run 'python3 scripts/sync_research_assets.py --invalidate' to publish"
fi

if [ "$AUDIT_ONLY" = true ]; then
    echo "Audit completed. Check results above."
fi

if [ "$DRY_RUN" = true ]; then
    echo "Dry run complete. No files were modified."
fi
