#!/usr/bin/env python3
"""
Comprehensive data audit for behavioral profiling research.

Verifies data integrity across all layers:
- L1: Source jobs
- L2: Profiles
- L3: Statistics
- L4: Validation (BERT, external benchmarks)
- L5: Reports

Usage:
    python3 scripts/run_data_audit.py --condition baseline
    python3 scripts/run_data_audit.py --all
    python3 scripts/run_data_audit.py --all --output audit_report.json
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import sys

# Paths
BASE_DIR = Path("outputs/behavioral_profiles")
JOBS_DIR = Path("outputs/single_prompt_jobs")
RESEARCH_DIR = BASE_DIR / "research_synthesis"

CONDITIONS = ["baseline", "authority", "urgency", "minimal_steering", "telemetryV3", "reminder", "naturalistic"]
CONDITIONS_WITH_ALL = CONDITIONS + ["all_combined"]

# Intervention suffixes for job filtering
INTERVENTION_SUFFIXES = {
    "authority": "_authority",
    "urgency": "_urgency",
    "reminder": "_reminder",
    "telemetryV3": "_telemetry",
    "minimal_steering": "_minimal_steering"
}


class AuditResult:
    """Container for audit check results."""
    def __init__(self, name: str):
        self.name = name
        self.checks = {}
        self.warnings = []
        self.errors = []

    def add_check(self, check_name: str, expected, actual, passed: bool, note: str = None):
        self.checks[check_name] = {
            "expected": expected,
            "actual": actual,
            "pass": passed,
            "note": note
        }
        if not passed:
            self.errors.append(f"{check_name}: expected {expected}, got {actual}")

    def add_warning(self, message: str):
        self.warnings.append(message)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "checks": self.checks,
            "warnings": self.warnings,
            "errors": self.errors
        }


def load_json(path: Path) -> dict:
    """Load JSON file, return empty dict if not found."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def audit_profile_integrity(condition: str) -> AuditResult:
    """Phase 1: Verify profile data integrity."""
    result = AuditResult("profile_integrity")
    profiles_dir = BASE_DIR / condition / "profiles"

    # 1.1 Profile count
    # naturalistic: 44 (llama-3-70b removed due to invalid scores)
    # all_combined: 45 (after llama-3-70b removal)
    # others: 45
    expected_count = 44 if condition == "naturalistic" else 45
    profiles = list(profiles_dir.glob("*.json")) if profiles_dir.exists() else []
    result.add_check("profile_count", expected_count, len(profiles),
                     abs(len(profiles) - expected_count) <= 1)  # Allow ±1

    # 1.2-1.4 Profile contents
    invalid_scores = 0
    zero_evaluations = 0
    nan_values = 0
    dimensions = ["warmth", "formality", "hedging", "aggression", "transgression",
                  "grandiosity", "tribalism", "depth", "authenticity"]

    for profile_file in profiles:
        data = load_json(profile_file)
        dims = data.get("dimensions", {})
        total_evals = data.get("total_evaluations", 0)

        if total_evals == 0:
            zero_evaluations += 1

        for dim in dimensions:
            dim_data = dims.get(dim, {})
            avg = dim_data.get("average")

            if avg is None or (isinstance(avg, float) and (avg != avg)):  # NaN check
                nan_values += 1
            elif not (1 <= avg <= 10):
                invalid_scores += 1

    result.add_check("dimensions_valid", 0, invalid_scores, invalid_scores == 0)
    result.add_check("no_nan_values", 0, nan_values, nan_values == 0)
    result.add_check("positive_evaluations", 0, zero_evaluations, zero_evaluations == 0,
                     note="Profiles with zero total_evaluations")

    return result


def audit_source_jobs(condition: str) -> AuditResult:
    """Phase 2: Verify source job data."""
    result = AuditResult("source_jobs")

    job_files = []

    if condition == "naturalistic":
        nat_dir = JOBS_DIR / "naturalistic_1"
        if nat_dir.exists():
            for job_dir in nat_dir.iterdir():
                if job_dir.is_dir() and job_dir.name.startswith("job_naturalistic_"):
                    job_files.extend(job_dir.glob("*.json"))
    elif condition == "all_combined":
        # Count from all sources
        for suite_dir in JOBS_DIR.glob("baseline_*"):
            if suite_dir.is_dir():
                for job_dir in suite_dir.iterdir():
                    if job_dir.is_dir():
                        job_files.extend(job_dir.glob("*.json"))
        nat_dir = JOBS_DIR / "naturalistic_1"
        if nat_dir.exists():
            for job_dir in nat_dir.iterdir():
                if job_dir.is_dir() and job_dir.name.startswith("job_naturalistic_"):
                    job_files.extend(job_dir.glob("*.json"))
    else:
        suffix = INTERVENTION_SUFFIXES.get(condition, "")
        for suite_dir in JOBS_DIR.glob("baseline_*"):
            if not suite_dir.is_dir():
                continue
            for job_dir in suite_dir.iterdir():
                if not job_dir.is_dir():
                    continue
                name = job_dir.name
                if condition == "baseline":
                    if not any(s in name for s in INTERVENTION_SUFFIXES.values()):
                        job_files.extend(job_dir.glob("*.json"))
                elif suffix and suffix in name:
                    job_files.extend(job_dir.glob("*.json"))

    result.add_check("job_files_found", ">0", len(job_files), len(job_files) > 0)

    # Sample validation
    valid_judges = 0
    invalid_judges = 0
    judge_key = "judge_evaluation_telemetry" if condition == "telemetryV3" else "judge_evaluation"

    for job_file in job_files[:50]:  # Sample first 50
        data = load_json(job_file)
        if judge_key in data or "judge_evaluation" in data:
            valid_judges += 1
        else:
            invalid_judges += 1

    sampled = min(50, len(job_files))
    result.add_check("jobs_have_judge_eval", sampled, valid_judges,
                     valid_judges >= sampled * 0.9,  # 90% threshold
                     note=f"Sampled {sampled} jobs")

    return result


def audit_statistics(condition: str) -> AuditResult:
    """Phase 3: Verify statistical files."""
    result = AuditResult("statistics")

    # 3.1 median_split_classification.json
    ms_path = BASE_DIR / condition / "median_split_classification.json"
    ms_data = load_json(ms_path)

    result.add_check("median_split_exists", True, ms_path.exists(), ms_path.exists())

    if ms_data:
        n_high = ms_data.get("n_high_sophistication", 0)
        n_low = ms_data.get("n_low_sophistication", 0)
        n_total = n_high + n_low
        # naturalistic: 44, all others including all_combined: 45
        expected_n = 44 if condition == "naturalistic" else 45

        result.add_check("model_count", expected_n, n_total, abs(n_total - expected_n) <= 1)

        median_soph = ms_data.get("median_sophistication", 0)
        result.add_check("median_in_range", "4-8", f"{median_soph:.2f}",
                         4 <= median_soph <= 8)

        # Verify correlation exists
        corr = ms_data.get("correlation", {}).get("sophistication_disinhibition", {})
        if isinstance(corr, dict):
            r = corr.get("r", 0)
        else:
            r = corr
        result.add_check("h2_correlation_valid", "-1 to 1", f"{r:.3f}",
                         -1 <= r <= 1)

    # 3.2 comprehensive_stats.json
    cs_path = BASE_DIR / condition / "comprehensive_stats.json"
    result.add_check("comprehensive_stats_exists", True, cs_path.exists(), cs_path.exists())

    return result


def audit_judge_agreement(condition: str) -> AuditResult:
    """Phase 4: Verify judge agreement data."""
    result = AuditResult("judge_agreement")

    ja_path = BASE_DIR / condition / "judge_agreement" / "judge_agreement_audit.json"
    ja_data = load_json(ja_path)

    result.add_check("judge_agreement_exists", True, ja_path.exists(), ja_path.exists())

    if ja_data:
        n_evals = ja_data.get("summary", {}).get("n_evaluations", 0)
        # Expect ~2000-2500 for single conditions, more for all_combined
        min_expected = 500 if condition != "all_combined" else 10000
        result.add_check("evaluation_count", f">={min_expected}", n_evals,
                         n_evals >= min_expected)

        overall_icc = ja_data.get("overall", {}).get("icc_avg", 0)
        result.add_check("icc_plausible", "0.5-1.0", f"{overall_icc:.3f}",
                         0.5 <= overall_icc <= 1.0)

    return result


def audit_outliers(condition: str) -> AuditResult:
    """Phase 5: Verify outlier analysis."""
    result = AuditResult("outliers")

    or_dir = BASE_DIR / condition / "outliers_removed"
    result.add_check("outliers_dir_exists", True, or_dir.exists(), or_dir.exists())

    if or_dir.exists():
        info_path = or_dir / "outlier_removal_info.json"
        info_data = load_json(info_path)
        result.add_check("outlier_info_exists", True, info_path.exists(), info_path.exists())

        # Check profile count reduced
        or_profiles = list((or_dir / "profiles").glob("*.json")) if (or_dir / "profiles").exists() else []
        orig_profiles = list((BASE_DIR / condition / "profiles").glob("*.json"))

        removed = len(orig_profiles) - len(or_profiles)
        result.add_check("outliers_removed_count", ">=0", removed, removed >= 0)

    return result


def audit_bert_validation(condition: str) -> AuditResult:
    """Phase 6: Verify BERT validation data."""
    result = AuditResult("bert_validation")

    bert_path = RESEARCH_DIR / "bert_validation" / condition / "bert_validation_results.json"
    bert_data = load_json(bert_path)

    result.add_check("bert_results_exists", True, bert_path.exists(), bert_path.exists())

    if bert_data:
        n_models = len(bert_data.get("model_results", []))
        # naturalistic: 44, all others including all_combined: 45
        expected_n = 44 if condition == "naturalistic" else 45
        result.add_check("bert_model_count", expected_n, n_models,
                         abs(n_models - expected_n) <= 2)

        corr = bert_data.get("correlations", {}).get("toxicity", {})
        r = corr.get("r", 0)
        result.add_check("bert_correlation_valid", "-1 to 1", f"{r:.3f}",
                         -1 <= r <= 1)

    return result


def audit_condition(condition: str, verbose: bool = True) -> dict:
    """Run all audit phases for a single condition."""
    if verbose:
        print(f"\n{'='*60}")
        print(f"AUDITING: {condition}")
        print(f"{'='*60}")

    phases = {}

    # Run all phases
    phases["profile_integrity"] = audit_profile_integrity(condition)
    phases["source_jobs"] = audit_source_jobs(condition)
    phases["statistics"] = audit_statistics(condition)
    phases["judge_agreement"] = audit_judge_agreement(condition)
    phases["outliers"] = audit_outliers(condition)
    phases["bert_validation"] = audit_bert_validation(condition)

    # Summary
    total_checks = sum(len(p.checks) for p in phases.values())
    passed_checks = sum(sum(1 for c in p.checks.values() if c["pass"]) for p in phases.values())
    total_errors = sum(len(p.errors) for p in phases.values())
    total_warnings = sum(len(p.warnings) for p in phases.values())

    if verbose:
        for name, phase in phases.items():
            status = "PASS" if phase.passed else "FAIL"
            print(f"\n[{status}] {name}")
            for check_name, check in phase.checks.items():
                icon = "✓" if check["pass"] else "✗"
                print(f"  {icon} {check_name}: {check['actual']} (expected: {check['expected']})")
                if check.get("note"):
                    print(f"    Note: {check['note']}")
            for error in phase.errors:
                print(f"  ERROR: {error}")
            for warning in phase.warnings:
                print(f"  WARNING: {warning}")

        print(f"\nSUMMARY: {passed_checks}/{total_checks} checks passed")
        if total_errors:
            print(f"  {total_errors} errors")
        if total_warnings:
            print(f"  {total_warnings} warnings")

    return {
        "condition": condition,
        "timestamp": datetime.now().isoformat(),
        "phases": {name: phase.to_dict() for name, phase in phases.items()},
        "summary": {
            "total_checks": total_checks,
            "passed": passed_checks,
            "failed": total_checks - passed_checks,
            "errors": total_errors,
            "warnings": total_warnings,
            "status": "PASS" if total_errors == 0 else "FAIL"
        }
    }


def audit_cross_condition(verbose: bool = True) -> dict:
    """Phase 7-9: Cross-condition verification."""
    if verbose:
        print(f"\n{'='*60}")
        print("CROSS-CONDITION AUDIT")
        print(f"{'='*60}")

    result = AuditResult("cross_condition")

    # 7.1 Model consistency across conditions
    all_models = {}
    for cond in CONDITIONS:
        profiles_dir = BASE_DIR / cond / "profiles"
        if profiles_dir.exists():
            models = {p.stem for p in profiles_dir.glob("*.json")}
            all_models[cond] = models

    if all_models:
        reference = all_models.get("baseline", set())
        mismatches = []
        for cond, models in all_models.items():
            if cond == "baseline":
                continue
            diff = reference.symmetric_difference(models)
            if diff:
                mismatches.append(f"{cond}: {len(diff)} different")

        result.add_check("model_consistency", "0 differences",
                         f"{len(mismatches)} conditions differ",
                         len(mismatches) <= 1)  # Allow 1 (naturalistic may differ)

    # 8.1-8.2 Evaluation counts
    total_judge = 0
    total_bert = 0

    for cond in CONDITIONS:  # Not all_combined to avoid double-counting
        ja_path = BASE_DIR / cond / "judge_agreement" / "judge_agreement_audit.json"
        ja_data = load_json(ja_path)
        total_judge += ja_data.get("summary", {}).get("n_evaluations", 0)

        bert_path = RESEARCH_DIR / "bert_validation" / cond / "bert_validation_results.json"
        bert_data = load_json(bert_path)
        for m in bert_data.get("model_results", []):
            total_bert += m.get("n_scored", m.get("n_responses", 0))

    result.add_check("total_judge_evals", "~14088", total_judge,
                     abs(total_judge - 14088) < 500)
    result.add_check("total_bert_evals", "~14203", total_bert,
                     abs(total_bert - 14203) < 500)

    # 9.1-9.3 External validation
    for benchmark, expected_n in [("gpqa", 35), ("arc_agi", 16), ("aime", 20)]:
        bm_path = RESEARCH_DIR / "limitations" / "external_evals" / f"{benchmark}_validation_analysis.json"
        bm_data = load_json(bm_path)
        # Try different key names
        sample = bm_data.get("sample", {})
        actual_n = sample.get("unique_matched_models", sample.get("n_matched", sample.get("n", 0)))
        result.add_check(f"{benchmark}_matched", expected_n, actual_n,
                         abs(actual_n - expected_n) <= 2)

    if verbose:
        status = "PASS" if result.passed else "FAIL"
        print(f"\n[{status}] cross_condition")
        for check_name, check in result.checks.items():
            icon = "✓" if check["pass"] else "✗"
            print(f"  {icon} {check_name}: {check['actual']} (expected: {check['expected']})")

    return {
        "phase": "cross_condition",
        "timestamp": datetime.now().isoformat(),
        "result": result.to_dict()
    }


def main():
    parser = argparse.ArgumentParser(description="Run data audit")
    parser.add_argument("--condition", type=str, choices=CONDITIONS_WITH_ALL,
                        help="Audit single condition")
    parser.add_argument("--all", action="store_true", help="Audit all conditions")
    parser.add_argument("--output", type=str, help="Save audit report to JSON file")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    args = parser.parse_args()

    if not args.condition and not args.all:
        parser.error("Specify --condition or --all")

    verbose = not args.quiet
    results = {"timestamp": datetime.now().isoformat(), "conditions": {}}

    if args.all:
        for cond in CONDITIONS_WITH_ALL:
            results["conditions"][cond] = audit_condition(cond, verbose)
        results["cross_condition"] = audit_cross_condition(verbose)
    else:
        results["conditions"][args.condition] = audit_condition(args.condition, verbose)

    # Overall summary
    total_passed = sum(r["summary"]["passed"] for r in results["conditions"].values())
    total_checks = sum(r["summary"]["total_checks"] for r in results["conditions"].values())
    total_errors = sum(r["summary"]["errors"] for r in results["conditions"].values())

    print(f"\n{'='*60}")
    print("OVERALL AUDIT RESULT")
    print(f"{'='*60}")
    print(f"Conditions audited: {len(results['conditions'])}")
    print(f"Total checks: {total_passed}/{total_checks} passed")
    print(f"Total errors: {total_errors}")
    print(f"Status: {'PASS' if total_errors == 0 else 'FAIL'}")

    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nAudit report saved to: {output_path}")

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
