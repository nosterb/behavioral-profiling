#!/usr/bin/env python3
"""
Audit Statistics Consistency

Ensures all statistics in CONSOLIDATED_STATISTICS.md and MAIN_RESEARCH_BRIEF.md
are consistent with each other and with source JSON files.

Usage:
    python3 scripts/audit_statistics_consistency.py
    python3 scripts/audit_statistics_consistency.py --output audit_report.json
    python3 scripts/audit_statistics_consistency.py --verbose
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configuration
BASE_DIR = Path("outputs/behavioral_profiles")
CONSOLIDATED_PATH = BASE_DIR / "research_synthesis" / "CONSOLIDATED_STATISTICS.md"
MAIN_BRIEF_PATH = BASE_DIR / "research_synthesis" / "MAIN_RESEARCH_BRIEF.md"

CONDITIONS = ["baseline", "authority", "urgency", "minimal_steering", "telemetryV3", "reminder", "naturalistic", "all_combined"]

# Tolerance thresholds for numerical comparisons
TOLERANCE = {
    "r": 0.001,      # Correlation coefficients
    "p": 0.001,      # P-values (may have precision differences)
    "d": 0.01,       # Effect sizes
    "n": 0,          # Counts must match exactly
    "default": 0.01  # Default tolerance
}


def load_json(path):
    """Load JSON file, return None if not found."""
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def parse_markdown_table(content, section_pattern, header_pattern=None):
    """Extract data from a markdown table following a section header."""
    lines = content.split('\n')
    in_section = False
    in_table = False
    headers = []
    rows = []

    for line in lines:
        # Check for section header
        if re.search(section_pattern, line):
            in_section = True
            continue

        # Check for next section (exit)
        if in_section and line.startswith('## ') and not re.search(section_pattern, line):
            break

        if in_section:
            # Detect table header row
            if '|' in line and not in_table:
                # Skip separator lines (|---|---|)
                if re.match(r'^\|[-:\s|]+\|$', line.strip()):
                    continue
                cells = [c.strip() for c in line.strip('|').split('|')]
                if header_pattern is None or any(re.search(header_pattern, c) for c in cells):
                    headers = cells
                    in_table = True
                continue

            # Parse data rows
            if in_table and '|' in line:
                # Skip separator lines
                if re.match(r'^\|[-:\s|]+\|$', line.strip()):
                    continue
                cells = [c.strip() for c in line.strip('|').split('|')]
                if len(cells) == len(headers):
                    row = dict(zip(headers, cells))
                    rows.append(row)
                continue

            # End of table
            if in_table and '|' not in line and line.strip():
                break

    return rows


def extract_number(text):
    """Extract numeric value from text."""
    if not text:
        return None
    # Handle scientific notation
    match = re.search(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', text.replace(',', ''))
    if match:
        return float(match.group())
    return None


def values_match(val1, val2, stat_type="default"):
    """Check if two values match within tolerance."""
    if val1 is None or val2 is None:
        return val1 == val2

    tol = TOLERANCE.get(stat_type, TOLERANCE["default"])
    return abs(val1 - val2) <= tol


def load_source_data():
    """Load all source JSON files."""
    sources = {}

    # H1/H2 Core statistics
    for cond in CONDITIONS:
        path = BASE_DIR / cond / "median_split_classification.json"
        data = load_json(path)
        if data:
            sources[f"h1h2_{cond}"] = data

    # Outliers removed
    for cond in CONDITIONS:
        path = BASE_DIR / cond / "outliers_removed" / "median_split_classification.json"
        data = load_json(path)
        if data:
            sources[f"outliers_{cond}"] = data

    # BERT validation
    for cond in CONDITIONS:
        path = BASE_DIR / "research_synthesis" / "bert_validation" / cond / "bert_validation_results.json"
        data = load_json(path)
        if data:
            sources[f"bert_{cond}"] = data

    # BERT soph/disin
    for cond in CONDITIONS:
        path = BASE_DIR / "research_synthesis" / "bert_validation" / cond / "bert_soph_disin_results.json"
        data = load_json(path)
        if data:
            sources[f"bert_soph_disin_{cond}"] = data

    # Judge agreement
    for cond in CONDITIONS:
        path = BASE_DIR / cond / "judge_agreement" / "judge_agreement_audit.json"
        data = load_json(path)
        if data:
            sources[f"judge_agreement_{cond}"] = data

    # External validation
    for benchmark in ["gpqa", "aime", "arc_agi"]:
        path = BASE_DIR / "research_synthesis" / "limitations" / "external_evals" / f"{benchmark}_validation_analysis.json"
        data = load_json(path)
        if data:
            sources[f"external_{benchmark}"] = data

    # Provider ANOVA
    for cond in CONDITIONS:
        path = BASE_DIR / cond / "provider_comparison_stats.json"
        data = load_json(path)
        if data:
            sources[f"provider_{cond}"] = data

    return sources


def audit_h1h2_table(consolidated_content, sources, verbose=False):
    """Audit H1/H2 Core Statistics table."""
    results = []

    rows = parse_markdown_table(consolidated_content, r"## 1\. H1/H2 CORE STATISTICS")

    for row in rows:
        condition = row.get("Condition", "").strip()
        if not condition or condition not in CONDITIONS:
            continue

        source = sources.get(f"h1h2_{condition}")
        if not source:
            results.append({
                "check": f"H1H2_{condition}",
                "status": "MISSING_SOURCE",
                "message": f"No source file for {condition}"
            })
            continue

        # The actual structure:
        # - N = n_high_sophistication + n_low_sophistication
        # - H1_d = statistics.disinhibition.cohens_d
        # - H2_r = correlation.sophistication_disinhibition

        # Check N
        doc_n = extract_number(row.get("N", ""))
        src_n_high = source.get("n_high_sophistication", 0)
        src_n_low = source.get("n_low_sophistication", 0)
        src_n = src_n_high + src_n_low
        if not values_match(doc_n, src_n, "n"):
            results.append({
                "check": f"H1H2_{condition}_N",
                "status": "MISMATCH",
                "doc_value": doc_n,
                "source_value": src_n,
                "delta": abs(doc_n - src_n) if doc_n and src_n else None
            })
        else:
            results.append({
                "check": f"H1H2_{condition}_N",
                "status": "MATCH",
                "value": src_n
            })

        # Check H1_d (Cohen's d for disinhibition group difference)
        doc_d = extract_number(row.get("H1_d", ""))
        src_d = source.get("statistics", {}).get("disinhibition", {}).get("cohens_d")
        if not values_match(doc_d, src_d, "d"):
            results.append({
                "check": f"H1H2_{condition}_H1_d",
                "status": "MISMATCH",
                "doc_value": doc_d,
                "source_value": src_d,
                "delta": abs(doc_d - src_d) if doc_d and src_d else None
            })
        else:
            results.append({
                "check": f"H1H2_{condition}_H1_d",
                "status": "MATCH",
                "value": src_d
            })

        # Check H2_r (correlation between sophistication and disinhibition)
        doc_r = extract_number(row.get("H2_r", ""))
        src_r = source.get("correlation", {}).get("sophistication_disinhibition")
        if not values_match(doc_r, src_r, "r"):
            results.append({
                "check": f"H1H2_{condition}_H2_r",
                "status": "MISMATCH",
                "doc_value": doc_r,
                "source_value": src_r,
                "delta": abs(doc_r - src_r) if doc_r and src_r else None
            })
        else:
            results.append({
                "check": f"H1H2_{condition}_H2_r",
                "status": "MATCH",
                "value": src_r
            })

    return results


def audit_outliers_table(consolidated_content, sources, verbose=False):
    """Audit H1/H2 Outliers Removed table."""
    results = []

    rows = parse_markdown_table(consolidated_content, r"## 2\. H1/H2 OUTLIERS REMOVED")

    for row in rows:
        condition = row.get("Condition", "").strip()
        if not condition or condition not in CONDITIONS:
            continue

        source = sources.get(f"outliers_{condition}")
        if not source:
            results.append({
                "check": f"Outliers_{condition}",
                "status": "MISSING_SOURCE",
                "message": f"No outliers source file for {condition}"
            })
            continue

        # Same structure as main h1h2 file
        # - N_Final = n_high_sophistication + n_low_sophistication
        # - H1_d = statistics.disinhibition.cohens_d
        # - H2_r = correlation.sophistication_disinhibition

        # Check N_Final
        doc_n = extract_number(row.get("N_Final", ""))
        src_n_high = source.get("n_high_sophistication", 0)
        src_n_low = source.get("n_low_sophistication", 0)
        src_n = src_n_high + src_n_low
        if not values_match(doc_n, src_n, "n"):
            results.append({
                "check": f"Outliers_{condition}_N_Final",
                "status": "MISMATCH",
                "doc_value": doc_n,
                "source_value": src_n
            })
        else:
            results.append({
                "check": f"Outliers_{condition}_N_Final",
                "status": "MATCH",
                "value": src_n
            })

        # Check H1_d (Cohen's d for disinhibition)
        doc_d = extract_number(row.get("H1_d", ""))
        src_d = source.get("statistics", {}).get("disinhibition", {}).get("cohens_d")
        if not values_match(doc_d, src_d, "d"):
            results.append({
                "check": f"Outliers_{condition}_H1_d",
                "status": "MISMATCH",
                "doc_value": doc_d,
                "source_value": src_d
            })
        else:
            results.append({
                "check": f"Outliers_{condition}_H1_d",
                "status": "MATCH",
                "value": src_d
            })

        # Check H2_r (correlation)
        doc_r = extract_number(row.get("H2_r", ""))
        src_r = source.get("correlation", {}).get("sophistication_disinhibition")
        if not values_match(doc_r, src_r, "r"):
            results.append({
                "check": f"Outliers_{condition}_H2_r",
                "status": "MISMATCH",
                "doc_value": doc_r,
                "source_value": src_r
            })
        else:
            results.append({
                "check": f"Outliers_{condition}_H2_r",
                "status": "MATCH",
                "value": src_r
            })

    return results


def audit_bert_validation(consolidated_content, sources, verbose=False):
    """Audit BERT VALIDATION - TOXICITY vs AGGRESSION table."""
    results = []

    rows = parse_markdown_table(consolidated_content, r"## 3\. BERT VALIDATION")

    for row in rows:
        condition = row.get("Condition", "").strip()
        if not condition or condition not in CONDITIONS:
            continue

        source = sources.get(f"bert_{condition}")
        if not source:
            results.append({
                "check": f"BERT_{condition}",
                "status": "MISSING_SOURCE",
                "message": f"No BERT source file for {condition}"
            })
            continue

        corr = source.get("correlations", {})

        # Check r_tox
        doc_r = extract_number(row.get("r_tox", ""))
        src_r = corr.get("toxicity", {}).get("r")
        if not values_match(doc_r, src_r, "r"):
            results.append({
                "check": f"BERT_{condition}_r_tox",
                "status": "MISMATCH",
                "doc_value": doc_r,
                "source_value": src_r
            })
        else:
            results.append({
                "check": f"BERT_{condition}_r_tox",
                "status": "MATCH",
                "value": src_r
            })

        # Check r_ins
        doc_r = extract_number(row.get("r_ins", ""))
        src_r = corr.get("insult", {}).get("r")
        if not values_match(doc_r, src_r, "r"):
            results.append({
                "check": f"BERT_{condition}_r_ins",
                "status": "MISMATCH",
                "doc_value": doc_r,
                "source_value": src_r
            })
        else:
            results.append({
                "check": f"BERT_{condition}_r_ins",
                "status": "MATCH",
                "value": src_r
            })

    return results


def audit_bert_soph_disin(consolidated_content, sources, verbose=False):
    """Audit BERT vs SOPHISTICATION/DISINHIBITION table."""
    results = []

    rows = parse_markdown_table(consolidated_content, r"## 5\. BERT vs SOPHISTICATION/DISINHIBITION")

    for row in rows:
        condition = row.get("Condition", "").strip()
        if not condition or condition not in CONDITIONS:
            continue

        source = sources.get(f"bert_soph_disin_{condition}")
        if not source:
            results.append({
                "check": f"BERT_SophDisin_{condition}",
                "status": "MISSING_SOURCE",
                "message": f"No BERT soph/disin source file for {condition}"
            })
            continue

        corr = source.get("correlations", {})

        # Check r_tox_soph
        doc_r = extract_number(row.get("r_tox_soph", ""))
        src_r = corr.get("toxicity_vs_sophistication", {}).get("r")
        if not values_match(doc_r, src_r, "r"):
            results.append({
                "check": f"BERT_SophDisin_{condition}_r_tox_soph",
                "status": "MISMATCH",
                "doc_value": doc_r,
                "source_value": src_r
            })
        else:
            results.append({
                "check": f"BERT_SophDisin_{condition}_r_tox_soph",
                "status": "MATCH",
                "value": src_r
            })

        # Check r_tox_disin
        doc_r = extract_number(row.get("r_tox_disin", ""))
        src_r = corr.get("toxicity_vs_disinhibition", {}).get("r")
        if not values_match(doc_r, src_r, "r"):
            results.append({
                "check": f"BERT_SophDisin_{condition}_r_tox_disin",
                "status": "MISMATCH",
                "doc_value": doc_r,
                "source_value": src_r
            })
        else:
            results.append({
                "check": f"BERT_SophDisin_{condition}_r_tox_disin",
                "status": "MATCH",
                "value": src_r
            })

    return results


def audit_judge_agreement(consolidated_content, sources, verbose=False):
    """Audit JUDGE AGREEMENT - ICC(3) table."""
    results = []

    rows = parse_markdown_table(consolidated_content, r"## 8\. JUDGE AGREEMENT")

    for row in rows:
        condition = row.get("Condition", "").strip()
        if not condition or condition not in CONDITIONS:
            continue

        source = sources.get(f"judge_agreement_{condition}")
        if not source:
            results.append({
                "check": f"JudgeAgreement_{condition}",
                "status": "MISSING_SOURCE",
                "message": f"No judge agreement source file for {condition}"
            })
            continue

        summary = source.get("summary", {})

        # Check N_Evals
        doc_n = extract_number(row.get("N_Evals", ""))
        src_n = summary.get("n_evaluations")
        if not values_match(doc_n, src_n, "n"):
            results.append({
                "check": f"JudgeAgreement_{condition}_N_Evals",
                "status": "MISMATCH",
                "doc_value": doc_n,
                "source_value": src_n
            })
        else:
            results.append({
                "check": f"JudgeAgreement_{condition}_N_Evals",
                "status": "MATCH",
                "value": src_n
            })

        # Check Overall ICC
        doc_icc = extract_number(row.get("Overall", ""))
        src_icc = summary.get("overall_icc")
        if not values_match(doc_icc, src_icc, "r"):
            results.append({
                "check": f"JudgeAgreement_{condition}_Overall_ICC",
                "status": "MISMATCH",
                "doc_value": doc_icc,
                "source_value": src_icc
            })
        else:
            results.append({
                "check": f"JudgeAgreement_{condition}_Overall_ICC",
                "status": "MATCH",
                "value": src_icc
            })

    return results


def audit_external_validation(consolidated_content, sources, verbose=False):
    """Audit External Validation Per-Benchmark table."""
    results = []

    rows = parse_markdown_table(consolidated_content, r"### 11\.1 Per-Benchmark Correlations")

    benchmark_map = {
        "GPQA": "gpqa",
        "AIME": "aime",
        "ARC-AGI": "arc_agi"
    }

    for row in rows:
        benchmark = row.get("Benchmark", "").strip()
        if benchmark not in benchmark_map:
            continue

        source_key = f"external_{benchmark_map[benchmark]}"
        source = sources.get(source_key)
        if not source:
            results.append({
                "check": f"External_{benchmark}",
                "status": "MISSING_SOURCE",
                "message": f"No external validation source file for {benchmark}"
            })
            continue

        corr = source.get("correlations", {})

        # Check r(BM->Soph)
        doc_r = extract_number(row.get("r(BM→Soph)", ""))
        src_r = corr.get("sophistication", {}).get("r")
        if not values_match(doc_r, src_r, "r"):
            results.append({
                "check": f"External_{benchmark}_r_soph",
                "status": "MISMATCH",
                "doc_value": doc_r,
                "source_value": src_r
            })
        else:
            results.append({
                "check": f"External_{benchmark}_r_soph",
                "status": "MATCH",
                "value": src_r
            })

        # Check r(BM->Disin)
        doc_r = extract_number(row.get("r(BM→Disin)", ""))
        src_r = corr.get("disinhibition", {}).get("r")
        if not values_match(doc_r, src_r, "r"):
            results.append({
                "check": f"External_{benchmark}_r_disin",
                "status": "MISMATCH",
                "doc_value": doc_r,
                "source_value": src_r
            })
        else:
            results.append({
                "check": f"External_{benchmark}_r_disin",
                "status": "MATCH",
                "value": src_r
            })

    return results


def cross_check_documents(consolidated_content, main_brief_content, verbose=False):
    """Cross-check matching statistics between the two documents."""
    results = []

    # Extract H2_r from CONSOLIDATED
    consol_h1h2 = parse_markdown_table(consolidated_content, r"## 1\. H1/H2 CORE STATISTICS")

    # Extract from MAIN_BRIEF (look for h1h2_table AUTO block)
    # The table starts after <!-- AUTO-START:h1h2_table -->
    brief_h1h2 = parse_markdown_table(main_brief_content, r"<!-- AUTO-START:h1h2_table -->")

    # Create lookup dictionaries
    consol_lookup = {r.get("Condition"): r for r in consol_h1h2}
    brief_lookup = {r.get("Condition"): r for r in brief_h1h2}

    for condition in CONDITIONS:
        if condition not in consol_lookup or condition not in brief_lookup:
            continue

        # Check H2_r matches between documents
        consol_r = extract_number(consol_lookup[condition].get("H2_r", ""))
        brief_r = extract_number(brief_lookup[condition].get("H2 r", ""))  # Different column name in brief

        if consol_r and brief_r and not values_match(consol_r, brief_r, "r"):
            results.append({
                "check": f"CrossDoc_{condition}_H2_r",
                "status": "MISMATCH",
                "consolidated_value": consol_r,
                "brief_value": brief_r,
                "delta": abs(consol_r - brief_r)
            })
        elif consol_r and brief_r:
            results.append({
                "check": f"CrossDoc_{condition}_H2_r",
                "status": "MATCH",
                "value": consol_r
            })

    return results


def run_audit(output_path=None, verbose=False):
    """Run the full statistics consistency audit."""
    print("=" * 60)
    print("STATISTICS CONSISTENCY AUDIT")
    print("=" * 60)
    print(f"Date: {datetime.now().isoformat()}")
    print()

    # Load documents
    print("Loading documents...")
    consolidated_content = CONSOLIDATED_PATH.read_text()
    main_brief_content = MAIN_BRIEF_PATH.read_text()

    # Load source data
    print("Loading source JSON files...")
    sources = load_source_data()
    print(f"  Loaded {len(sources)} source files")

    # Run audits
    all_results = []

    print("\nAuditing H1/H2 Core Statistics...")
    all_results.extend(audit_h1h2_table(consolidated_content, sources, verbose))

    print("Auditing Outliers Removed Statistics...")
    all_results.extend(audit_outliers_table(consolidated_content, sources, verbose))

    print("Auditing BERT Validation...")
    all_results.extend(audit_bert_validation(consolidated_content, sources, verbose))

    print("Auditing BERT vs Soph/Disin...")
    all_results.extend(audit_bert_soph_disin(consolidated_content, sources, verbose))

    print("Auditing Judge Agreement...")
    all_results.extend(audit_judge_agreement(consolidated_content, sources, verbose))

    print("Auditing External Validation...")
    all_results.extend(audit_external_validation(consolidated_content, sources, verbose))

    print("Cross-checking CONSOLIDATED vs MAIN_BRIEF...")
    all_results.extend(cross_check_documents(consolidated_content, main_brief_content, verbose))

    # Summarize results
    total = len(all_results)
    matches = sum(1 for r in all_results if r["status"] == "MATCH")
    mismatches = [r for r in all_results if r["status"] == "MISMATCH"]
    missing = [r for r in all_results if r["status"] == "MISSING_SOURCE"]

    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)
    print(f"Total checks: {total}")
    print(f"Matches: {matches}")
    print(f"Mismatches: {len(mismatches)}")
    print(f"Missing sources: {len(missing)}")
    print()

    if mismatches:
        print("MISMATCHES:")
        for m in mismatches:
            print(f"  - {m['check']}")
            if "doc_value" in m:
                print(f"    Doc: {m['doc_value']}, Source: {m['source_value']}")
            if "consolidated_value" in m:
                print(f"    Consolidated: {m['consolidated_value']}, Brief: {m['brief_value']}")
        print()

    if missing:
        print("MISSING SOURCES:")
        for m in missing:
            print(f"  - {m['check']}: {m.get('message', 'No source file')}")
        print()

    if len(mismatches) == 0 and len(missing) == 0:
        print("STATUS: ALL CHECKS PASSED")
    else:
        print(f"STATUS: {len(mismatches)} MISMATCHES, {len(missing)} MISSING")

    # Create audit report
    audit_report = {
        "audit_date": datetime.now().isoformat(),
        "files_checked": {
            "consolidated": str(CONSOLIDATED_PATH),
            "brief": str(MAIN_BRIEF_PATH),
            "source_jsons": list(sources.keys())
        },
        "results": all_results,
        "summary": {
            "total_checks": total,
            "matches": matches,
            "mismatches": len(mismatches),
            "missing_sources": len(missing),
            "status": "PASS" if len(mismatches) == 0 and len(missing) == 0 else "FAIL"
        }
    }

    # Write output if requested
    if output_path:
        output_file = Path(output_path)
        output_file.write_text(json.dumps(audit_report, indent=2))
        print(f"\nAudit report written to: {output_file}")

    return audit_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit statistics consistency")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    run_audit(output_path=args.output, verbose=args.verbose)
