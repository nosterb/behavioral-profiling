#!/bin/bash
# Complete audit script for behavioral profiling analysis
# Usage: ./scripts/audit_analysis.sh baseline

if [ -z "$1" ]; then
    echo "Usage: $0 <intervention_name>"
    echo "Example: $0 baseline"
    echo "         $0 authority"
    echo "         $0 urgency"
    echo "         $0 minimal_steering"
    exit 1
fi

INTERVENTION="$1"
PROFILE_DIR="outputs/behavioral_profiles/${INTERVENTION}"

if [ ! -d "${PROFILE_DIR}" ]; then
    echo "Error: Profile directory not found: ${PROFILE_DIR}"
    exit 1
fi

echo "========================================================================"
echo "ANALYSIS AUDIT: ${INTERVENTION}"
echo "========================================================================"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Profile Directory: ${PROFILE_DIR}"
echo ""

# ============================================================================
# STAGE 1: PROFILE DATA AUDIT
# ============================================================================
echo "=== PROFILE DATA AUDIT ==="
echo ""

# 1. Count total profiles
PROFILE_COUNT=$(ls ${PROFILE_DIR}/profiles/*.json 2>/dev/null | wc -l | tr -d ' ')
echo "Total profiles: ${PROFILE_COUNT}"
if [ "${PROFILE_COUNT}" -ge 40 ]; then
    echo "✓ Sufficient sample size"
else
    echo "⚠️  Warning: Low sample size (expected ≥40)"
fi
echo ""

# 2. Check for missing dimensions in profiles
echo "Checking dimension completeness..."
python3 -c "
import json
from pathlib import Path

profile_dir = Path('${PROFILE_DIR}/profiles')
dimensions = ['warmth', 'formality', 'hedging', 'aggression', 'transgression',
              'grandiosity', 'tribalism', 'depth', 'authenticity']

issues = []
for p in profile_dir.glob('*.json'):
    data = json.loads(p.read_text())

    # Handle both profile formats
    if 'average_scores' in data:
        scores = data['average_scores']
    elif 'dimensions' in data:
        scores = data['dimensions']
    else:
        scores = {}

    missing = [d for d in dimensions if d not in scores]
    if missing:
        issues.append((p.name, missing))

if not issues:
    print('✓ All profiles have complete dimensions')
else:
    print(f'⚠️  Found {len(issues)} profiles with missing dimensions:')
    for name, missing in issues[:5]:
        print(f'  - {name}: missing {missing}')
"
echo ""

# 3. Check contribution counts
echo "Checking contribution counts..."
python3 -c "
import json
from pathlib import Path

profile_dir = Path('${PROFILE_DIR}/profiles')
low_contrib = []
for p in profile_dir.glob('*.json'):
    data = json.loads(p.read_text())

    # Handle different field names
    n = data.get('n_contributions') or data.get('total_evaluations') or 0
    if n < 10:
        low_contrib.append((p.name, n))

if not low_contrib:
    print('✓ All profiles have sufficient contributions (≥10)')
else:
    print(f'⚠️  Found {len(low_contrib)} profiles with low contributions:')
    for name, n in low_contrib[:5]:
        print(f'  - {name}: {n} contributions')
"
echo ""

# ============================================================================
# STAGE 2: CLASSIFICATION AUDIT
# ============================================================================
echo "=== CLASSIFICATION AUDIT ==="
echo ""

# 1. Verify classification file exists
if [ ! -f "${PROFILE_DIR}/median_split_classification.json" ]; then
    echo "❌ median_split_classification.json not found"
    echo "   Run: python3 scripts/calculate_median_split.py ${PROFILE_DIR}"
    exit 1
fi
echo "✓ Classification file exists"
echo ""

# 2. Check group balance
python3 -c "
import json
from pathlib import Path

data = json.loads(Path('${PROFILE_DIR}/median_split_classification.json').read_text())

n_high = data['n_high_sophistication']
n_low = data['n_low_sophistication']
median = data['median_sophistication']

print(f'Median sophistication: {median:.3f}')
print(f'High-Sophistication: n={n_high}')
print(f'Low-Sophistication: n={n_low}')
print(f'Balance: {abs(n_high - n_low)} model difference')
print()

if abs(n_high - n_low) <= 2:
    print('✓ Well-balanced groups')
elif abs(n_high - n_low) <= 5:
    print('⚠️  Moderate imbalance (acceptable)')
else:
    print('⚠️  High imbalance - review classification')
"
echo ""

# 3. Check sophistication separation
python3 -c "
import json
from pathlib import Path

data = json.loads(Path('${PROFILE_DIR}/median_split_classification.json').read_text())
soph_stats = data['statistics']['sophistication']

cohens_d = soph_stats['cohens_d']
print(f'Sophistication Cohen\'s d: {cohens_d:.2f}')

if cohens_d >= 2.0:
    print('✓ Very large separation (d ≥ 2.0)')
elif cohens_d >= 1.5:
    print('✓ Large separation (d ≥ 1.5)')
elif cohens_d >= 0.8:
    print('⚠️  Moderate separation (d ≥ 0.8)')
else:
    print('⚠️  Weak separation - review classification criteria')
"
echo ""

# ============================================================================
# STAGE 3: STATISTICAL RESULTS AUDIT
# ============================================================================
echo "=== STATISTICAL RESULTS AUDIT ==="
echo ""

# 1. Check H1: Disinhibition composite effect
python3 -c "
import json
from pathlib import Path

data = json.loads(Path('${PROFILE_DIR}/median_split_classification.json').read_text())
disinhib = data['statistics']['disinhibition']

d = disinhib['cohens_d']
p = disinhib['p_value']

print(f'H1: Disinhibition Composite')
print(f'  Cohen\'s d: {d:.2f}')
print(f'  p-value: {p:.6f}')

if d >= 1.5 and p < 0.001:
    print('  ✓ Large effect, highly significant')
elif d >= 0.8 and p < 0.05:
    print('  ✓ Medium-large effect, significant')
elif d >= 0.5 and p < 0.05:
    print('  ⚠️  Medium effect, significant (weaker than baseline)')
else:
    print('  ⚠️  Weak or non-significant effect')
"
echo ""

# 2. Check H1: Individual disinhibition dimensions
python3 -c "
import json
from pathlib import Path

data = json.loads(Path('${PROFILE_DIR}/median_split_classification.json').read_text())

print('H1: Individual Disinhibition Dimensions')
dims = ['transgression', 'aggression', 'tribalism', 'grandiosity']
all_large = True

for dim in dims:
    stats = data['statistics'][dim]
    d = stats['cohens_d']
    p = stats['p_value']

    status = '✓' if (d >= 0.8 and p < 0.05) else '⚠️'
    print(f'  {status} {dim.capitalize()}: d={d:.2f}, p={p:.6f}')

    if d < 0.8 or p >= 0.05:
        all_large = False

print()
if all_large:
    print('  ✓ All dimensions show large effects (d ≥ 0.8)')
else:
    print('  ⚠️  Some dimensions show weak effects (expected for some interventions)')
"
echo ""

# 3. Check H2: Sophistication-disinhibition correlation
python3 -c "
import json
from pathlib import Path

data = json.loads(Path('${PROFILE_DIR}/median_split_classification.json').read_text())
r = data['correlation']['sophistication_disinhibition']

print(f'H2: Sophistication-Disinhibition Correlation')
print(f'  r = {r:.3f}')

if r >= 0.60:
    print('  ✓ Large correlation (r ≥ 0.60)')
elif r >= 0.50:
    print('  ✓ Large correlation (r ≥ 0.50)')
elif r >= 0.30:
    print('  ⚠️  Medium correlation (r ≥ 0.30)')
else:
    print('  ⚠️  Weak correlation (may be intervention-specific)')
"
echo ""

# ============================================================================
# STAGE 4: FILE OUTPUT AUDIT
# ============================================================================
echo "=== FILE OUTPUT AUDIT ==="
echo ""

# Check required files
FILES=(
    "${PROFILE_DIR}/median_split_classification.json"
    "${PROFILE_DIR}/RESEARCH_BRIEF.md"
    "${PROFILE_DIR}/history/contributions.json"
    "${PROFILE_DIR}/history/updates_log.json"
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
echo ""

if [ "${all_exist}" = true ]; then
    echo "✓ All required files present"
else
    echo "❌ Some required files missing - re-run pipeline stages"
fi
echo ""

# Check profile count consistency
echo "Checking profile count consistency..."
python3 -c "
import json
from pathlib import Path

profile_dir = Path('${PROFILE_DIR}/profiles')
profile_count = len(list(profile_dir.glob('*.json')))

median_split = json.loads(Path('${PROFILE_DIR}/median_split_classification.json').read_text())
median_count = len(median_split['models'])

print(f'Profiles directory: {profile_count} models')
print(f'median_split_classification.json: {median_count} models')
print()

if profile_count == median_count:
    print('✓ Counts match across all files')
else:
    print('⚠️  Count mismatch detected - re-run pipeline')
"
echo ""

# ============================================================================
# STAGE 5: RESEARCH BRIEF AUDIT
# ============================================================================
echo "=== RESEARCH BRIEF AUDIT ==="
echo ""

# 1. Check required sections exist
echo "Checking required sections..."
REQUIRED_SECTIONS=(
    "## Hypotheses"
    "## Methods"
    "## Results"
    "## Discussion"
    "## Supporting Files"
)

all_sections=true
for section in "${REQUIRED_SECTIONS[@]}"; do
    if grep -q "^${section}" "${PROFILE_DIR}/RESEARCH_BRIEF.md"; then
        echo "✓ ${section}"
    else
        echo "❌ ${section} MISSING"
        all_sections=false
    fi
done
echo ""

# 2. Check t-test format
echo "Checking t-test format..."
# Count lines with t-statistic reporting (either full format or table format)
full_format=$(grep -c "t(44) = " "${PROFILE_DIR}/RESEARCH_BRIEF.md" || echo "0")
table_rows=$(grep -E "^\| [A-Z]" "${PROFILE_DIR}/RESEARCH_BRIEF.md" | grep -v "Dimension" | wc -l | tr -d ' ')
total_tests=$((full_format + table_rows))
echo "Found ${total_tests} t-test reports (${full_format} full format + ${table_rows} table rows)"
if [ ${total_tests} -ge 10 ]; then
    echo "✓ Sufficient statistical reporting"
else
    echo "⚠️  Limited statistical reporting (expected ≥10)"
fi
echo ""

# 3. Check for proper effect size reporting
echo "Checking effect size reporting..."
if grep -q "Cohen's d" "${PROFILE_DIR}/RESEARCH_BRIEF.md" && \
   grep -q "large effect" "${PROFILE_DIR}/RESEARCH_BRIEF.md"; then
    echo "✓ Effect sizes properly reported"
else
    echo "⚠️  Effect size reporting incomplete"
fi
echo ""

# 4. Check supporting files section
echo "Checking supporting files section..."
if grep -q "median_split_classification.json" "${PROFILE_DIR}/RESEARCH_BRIEF.md"; then
    echo "✓ Supporting files documented"
else
    echo "⚠️  Supporting files not properly listed"
fi
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "========================================================================"
echo "AUDIT COMPLETE: ${INTERVENTION}"
echo "========================================================================"
echo ""

# Generate summary
python3 -c "
import json
from pathlib import Path

data = json.loads(Path('${PROFILE_DIR}/median_split_classification.json').read_text())

print('SUMMARY:')
print(f'  Models: {len(data[\"models\"])}')
print(f'  Classification: {data[\"n_high_sophistication\"]} high / {data[\"n_low_sophistication\"]} low')
print(f'  H1 (Disinhibition): d = {data[\"statistics\"][\"disinhibition\"][\"cohens_d\"]:.2f}')
print(f'  H2 (Correlation): r = {data[\"correlation\"][\"sophistication_disinhibition\"]:.3f}')
print()
print('Review any warnings (⚠️) above before finalizing results.')
print('All checks passed (✓) = ready for publication')
"
