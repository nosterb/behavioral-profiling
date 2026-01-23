#!/usr/bin/env python3
"""
Audit Compliance Checker

Validates that research synthesis outputs meet the provenance and audit requirements
specified in AUDIT_STANDARDS.md.

Usage:
    python3 scripts/check_audit_compliance.py [path]
    python3 scripts/check_audit_compliance.py --full-report
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Default paths
DEFAULT_RESEARCH_PATH = "outputs/behavioral_profiles/research_synthesis"

# Required fields in audit JSON files
REQUIRED_AUDIT_FIELDS = {
    "root": ["schema_version", "metadata", "provenance", "results"],
    "metadata": ["generated", "analysis"],
    "provenance": ["source_files", "methodology"],
}

# Files to skip in markdown analysis (documentation, not analysis files)
SKIP_MD_PATTERNS = [
    "CLAUDE.md",
    "AUDIT_STANDARDS.md",
    "AUDIT_MEMORY.md",
    "EXPERIMENT_PLAN.md",
    "AUDIT_PLAN.md",
    "_INVENTORY.md",
    "_MANIFEST.md",
    "LANGUAGE_GUIDE",
    "AUDIT_REPORT",  # Audit reports themselves don't need provenance sections
    "CONDITION_COMPARISON.md",  # Auto-generated reference table
    "OUTLIERS_REMOVED_COMPARISON.md",  # Auto-generated reference table
]

# Template files (incomplete, don't require provenance yet)
TEMPLATE_PATTERNS = [
    "TEMPLATE",
    "PENDING",
    "TBD",
]


def is_template_file(content: str) -> bool:
    """Check if file appears to be a template/incomplete."""
    first_500 = content[:500].upper()
    return any(pattern in first_500 for pattern in TEMPLATE_PATTERNS)


def is_skip_file(filename: str) -> bool:
    """Check if file should be skipped."""
    return any(pattern in filename for pattern in SKIP_MD_PATTERNS)


def validate_audit_json(filepath: Path) -> Dict[str, Any]:
    """
    Validate an audit JSON file against the schema.
    Returns dict with 'valid', 'errors', 'warnings'.
    """
    result = {"valid": True, "errors": [], "warnings": [], "filepath": str(filepath)}

    try:
        with open(filepath) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result["valid"] = False
        result["errors"].append(f"Invalid JSON: {e}")
        return result
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Read error: {e}")
        return result

    # Check root-level required fields
    for field in REQUIRED_AUDIT_FIELDS["root"]:
        if field not in data:
            if field == "results":
                # Allow alternatives to "results"
                if not any(k in data for k in ["correlations", "model_comparison", "relationships"]):
                    result["warnings"].append(f"Missing 'results' (or equivalent like 'correlations')")
            else:
                result["errors"].append(f"Missing required field: {field}")
                result["valid"] = False

    # Check schema_version
    if "schema_version" in data:
        if data["schema_version"] != "1.0":
            result["warnings"].append(f"schema_version is '{data['schema_version']}', expected '1.0'")

    # Check metadata fields
    if "metadata" in data:
        for field in REQUIRED_AUDIT_FIELDS["metadata"]:
            if field not in data["metadata"]:
                result["warnings"].append(f"Missing metadata.{field}")

    # Check provenance fields
    if "provenance" in data:
        for field in REQUIRED_AUDIT_FIELDS["provenance"]:
            if field not in data["provenance"]:
                result["warnings"].append(f"Missing provenance.{field}")

    # Check for absolute paths (should be relative)
    def check_paths(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                check_paths(v, f"{path}.{k}")
        elif isinstance(obj, str):
            if obj.startswith("/Users/") or obj.startswith("/home/"):
                result["warnings"].append(f"Absolute path found at {path}: {obj[:50]}...")

    check_paths(data)

    return result


def check_results_audit_coverage(research_path: Path) -> Dict[str, Any]:
    """
    Find all *_results.json files and check for corresponding *_audit.json.
    """
    results_files = list(research_path.rglob("*_results.json"))
    audit_files = {str(p) for p in research_path.rglob("*_audit.json")}

    coverage = {
        "total_results": len(results_files),
        "covered": [],
        "uncovered": [],
        "covered_by_consolidated": [],
    }

    # Known consolidated audits that cover multiple results files
    consolidated_audits = {
        "bert_validation": "bert_validation/bert_validation_audit.json",
    }

    for results_file in results_files:
        # Try to find corresponding audit file
        stem = results_file.stem.replace("_results", "_audit")
        audit_path = results_file.parent / f"{stem}.json"

        # Also check for consolidated audit in parent
        parent_audit = results_file.parent / f"{results_file.parent.name}_audit.json"

        # Check for consolidated audit covering this directory
        results_str = str(results_file)
        is_consolidated = False
        for key, audit_rel in consolidated_audits.items():
            if key in results_str:
                audit_full = research_path / audit_rel
                if audit_full.exists():
                    coverage["covered_by_consolidated"].append(str(results_file))
                    is_consolidated = True
                    break

        if is_consolidated:
            continue

        if str(audit_path) in audit_files or str(parent_audit) in audit_files:
            coverage["covered"].append(str(results_file))
        else:
            # Check if there's ANY audit file in the same directory
            dir_audits = [a for a in audit_files if str(results_file.parent) in a]
            if dir_audits:
                coverage["covered"].append(str(results_file))
            else:
                coverage["uncovered"].append(str(results_file))

    # Combine covered and consolidated for total
    coverage["covered"] = coverage["covered"] + coverage["covered_by_consolidated"]

    return coverage


def check_markdown_provenance(research_path: Path) -> Dict[str, Any]:
    """
    Check all analysis markdown files for Data Provenance sections.
    """
    md_files = list(research_path.rglob("*.md"))

    results = {
        "total_files": 0,
        "with_provenance": [],
        "without_provenance": [],
        "templates_skipped": [],
        "documentation_skipped": [],
    }

    for md_file in md_files:
        filename = md_file.name

        # Skip documentation files
        if is_skip_file(filename):
            results["documentation_skipped"].append(str(md_file))
            continue

        # Skip qualitative analysis files
        if "qualitative_analysis" in str(md_file):
            results["documentation_skipped"].append(str(md_file))
            continue

        results["total_files"] += 1

        try:
            content = md_file.read_text()
        except Exception:
            continue

        # Skip templates
        if is_template_file(content):
            results["templates_skipped"].append(str(md_file))
            continue

        # Check for provenance section
        if "## Data Provenance" in content or "## Provenance" in content:
            results["with_provenance"].append(str(md_file))
        else:
            results["without_provenance"].append(str(md_file))

    return results


def generate_report(research_path: Path, verbose: bool = False) -> str:
    """Generate compliance report."""
    lines = []
    lines.append("=" * 60)
    lines.append("AUDIT COMPLIANCE REPORT")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append(f"Path: {research_path}")
    lines.append("=" * 60)
    lines.append("")

    # 1. Validate audit JSON files
    lines.append("## 1. Audit JSON Schema Compliance")
    lines.append("-" * 40)

    audit_files = list(research_path.rglob("*_audit.json"))
    valid_count = 0
    warning_count = 0

    for audit_file in audit_files:
        result = validate_audit_json(audit_file)
        if result["valid"]:
            valid_count += 1
            if result["warnings"]:
                warning_count += 1
                if verbose:
                    lines.append(f"  ⚠️  {audit_file.name}: {len(result['warnings'])} warnings")
                    for w in result["warnings"]:
                        lines.append(f"      - {w}")
            else:
                if verbose:
                    lines.append(f"  ✅ {audit_file.name}")
        else:
            lines.append(f"  ❌ {audit_file.name}:")
            for e in result["errors"]:
                lines.append(f"      - {e}")

    lines.append(f"\nSummary: {valid_count}/{len(audit_files)} valid")
    if warning_count:
        lines.append(f"         {warning_count} with warnings")
    lines.append("")

    # 2. Results -> Audit coverage
    lines.append("## 2. Results File → Audit File Coverage")
    lines.append("-" * 40)

    coverage = check_results_audit_coverage(research_path)
    coverage_pct = (len(coverage["covered"]) / max(coverage["total_results"], 1)) * 100

    lines.append(f"Total *_results.json files: {coverage['total_results']}")
    lines.append(f"With audit coverage: {len(coverage['covered'])} ({coverage_pct:.0f}%)")

    if coverage["uncovered"]:
        lines.append(f"\nUncovered results files ({len(coverage['uncovered'])}):")
        for f in coverage["uncovered"]:
            lines.append(f"  ❌ {f}")
    else:
        lines.append("\n✅ All results files have audit coverage")
    lines.append("")

    # 3. Markdown provenance sections
    lines.append("## 3. Markdown Provenance Sections")
    lines.append("-" * 40)

    md_results = check_markdown_provenance(research_path)
    total_analysis = md_results["total_files"] - len(md_results["templates_skipped"])
    with_prov = len(md_results["with_provenance"])
    prov_pct = (with_prov / max(total_analysis, 1)) * 100

    lines.append(f"Analysis markdown files: {total_analysis}")
    lines.append(f"Templates skipped: {len(md_results['templates_skipped'])}")
    lines.append(f"Documentation skipped: {len(md_results['documentation_skipped'])}")
    lines.append(f"With provenance section: {with_prov} ({prov_pct:.0f}%)")

    if md_results["without_provenance"]:
        lines.append(f"\nMissing provenance section ({len(md_results['without_provenance'])}):")
        for f in md_results["without_provenance"]:
            lines.append(f"  ❌ {Path(f).name}")
    else:
        lines.append("\n✅ All analysis files have provenance sections")
    lines.append("")

    # Summary
    lines.append("=" * 60)
    lines.append("SUMMARY")
    lines.append("=" * 60)

    all_good = (
        valid_count == len(audit_files) and
        not coverage["uncovered"] and
        not md_results["without_provenance"]
    )

    if all_good:
        lines.append("✅ All audit compliance checks passed!")
    else:
        issues = []
        if valid_count < len(audit_files):
            issues.append(f"{len(audit_files) - valid_count} invalid audit files")
        if coverage["uncovered"]:
            issues.append(f"{len(coverage['uncovered'])} results files without audit")
        if md_results["without_provenance"]:
            issues.append(f"{len(md_results['without_provenance'])} markdown files without provenance")

        lines.append("⚠️  Issues found:")
        for issue in issues:
            lines.append(f"   - {issue}")

    lines.append("")
    lines.append("See AUDIT_STANDARDS.md for compliance requirements.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check audit compliance for research synthesis")
    parser.add_argument("path", nargs="?", default=DEFAULT_RESEARCH_PATH,
                       help="Path to check (default: research_synthesis)")
    parser.add_argument("--full-report", "-f", action="store_true",
                       help="Show detailed report with all files")
    parser.add_argument("--json", "-j", action="store_true",
                       help="Output as JSON")

    args = parser.parse_args()

    research_path = Path(args.path)
    if not research_path.exists():
        print(f"Error: Path does not exist: {research_path}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        # JSON output
        result = {
            "timestamp": datetime.now().isoformat(),
            "path": str(research_path),
            "audit_files": [],
            "results_coverage": check_results_audit_coverage(research_path),
            "markdown_provenance": check_markdown_provenance(research_path),
        }

        for audit_file in research_path.rglob("*_audit.json"):
            result["audit_files"].append(validate_audit_json(audit_file))

        print(json.dumps(result, indent=2))
    else:
        # Text report
        report = generate_report(research_path, verbose=args.full_report)
        print(report)


if __name__ == "__main__":
    main()
