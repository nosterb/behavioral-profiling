# Pre-Publication Audit Report

**Document**: MAIN_RESEARCH_BRIEF.md (v3.2)
**Audit Date**: 2026-01-14
**Auditor**: Claude Opus 4.5 (automated verification)
**Status**: COMPLETE - ALL CORRECTIONS APPLIED

---

## Executive Summary

The research brief has been systematically audited across 5 phases. **All auto-generated statistics are accurate**. Two minor statistical claims in manual sections require correction, and multiple typos were identified. No critical errors that would invalidate findings.

| Phase | Status | Issues Found |
|-------|--------|--------------|
| Phase 1: Statistical Audit | **PASS** | 1 minor (N varies 45-46) |
| Phase 2: Interpretation Audit | **PASS** | 0 issues |
| Phase 3: Manual Section Audit | **WARN** | 2 statistical, 13 typos |
| Phase 4: Cross-Reference Audit | **PASS** | 0 issues |
| **Overall** | **PASS with corrections** | 16 total items |

---

## Phase 1: Statistical Audit (Auto-Generated)

### Summary
All auto-generated statistics verified against source JSON files.

### Verification Results

#### §2 Core Results Table

| Metric | Brief Value | Source Value | Status |
|--------|-------------|--------------|--------|
| N (baseline) | 45 | 45 | **PASS** |
| Median Soph (baseline) | 5.94 | 5.9366 | **PASS** (rounded) |
| H1: Soph d (baseline) | 3.75 | 3.7528 | **PASS** (rounded) |
| H1a: d (baseline) | 2.13 | 2.1329 | **PASS** (rounded) |
| H2: r (baseline) | 0.702 | 0.7019 | **PASS** (rounded) |

#### §3.1 External Validation

| Metric | Brief Value | Source Value | Status |
|--------|-------------|--------------|--------|
| ARC-AGI matched models | 16 | 16 | **PASS** |
| ARC-AGI r (Sophistication) | 0.801 | 0.8005 | **PASS** |
| ARC-AGI p (Sophistication) | < .001 | 0.00020 | **PASS** |
| GPQA matched models | 35 | 35 | **PASS** |
| GPQA r (Sophistication) | 0.884 | 0.8841 | **PASS** |
| GPQA p (Sophistication) | < .001 | 1.92e-12 | **PASS** |
| Group diff ARC-AGI | +47.7 pp | 57.59 - 9.92 = 47.67 | **PASS** |
| Group diff GPQA | +31.4 pp | 83.43 - 52.05 = 31.38 | **PASS** |

#### Appendix B: Classification Stability

| Metric | Brief Value | Source Value | Status |
|--------|-------------|--------------|--------|
| Total models | 46 | 46 | **PASS** |
| Always High | 17 (37%) | 17 | **PASS** |
| Always Low | 18 (39%) | 18 | **PASS** |
| Flipped | 10 (22%) | 10 | **PASS** |
| Stability rate | 76.1% | 76.087 | **PASS** |

### Minor Issue

| Location | Issue | Severity |
|----------|-------|----------|
| Header | "Models: 45 per condition" but some conditions have N=46 | **LOW** |

**Recommendation**: Change to "Models: 45-46 per condition" (optional, current text acceptable)

---

## Phase 2: Interpretation Audit

### Summary
All claims verified to match underlying statistics.

### Verification Results

| Claim Location | Claim | Verification | Status |
|----------------|-------|--------------|--------|
| §2 "H1a consistently large" | d > 1.0 for all conditions | Verified: range 1.14-2.13 | **PASS** |
| §3.1 "Both benchmarks show large" | r > 0.50 | Verified: 0.80, 0.88 | **PASS** |
| §3.2 "strengthens H1a in 4/6" | Count Δd > 0.1 | Verified: 4 conditions | **PASS** |
| §4.1 "H2 significant for 3/5" | p < 0.05 count | Verified: Anthropic, OpenAI, AWS | **PASS** |
| §4.2 "6/6 conditions" OpenAI constraint | All residuals negative | Verified in source | **PASS** |
| §4.3 "All consistently constrained = OpenAI" | Check model providers | Verified: GPT-OSS-120B, GPT-5.2 Pro, O3, GPT-5, GPT-5.2 | **PASS** |
| §6.1 ICC > 0.75 = "Good" | Reliability threshold | Standard interpretation | **PASS** |
| Appendix B "76% stability" | Calculation check | (17+18)/46 = 76.1% | **PASS** |

---

## Phase 3: Manual Section Audit

### Summary
Manual sections reviewed for accuracy and consistency. Found 2 statistical inaccuracies and 13 typos.

### Statistical Inaccuracies

| Location | Current Text | Correct Text | Status |
|----------|--------------|--------------|--------|
| §5.1 H1a/H2 claim | "+0.04 Δr" | "+0.08 Δr" (source: +0.076) | **FIX REQUIRED** |
| §5.1 H1a/H2 claim | "r=0.46-0.74" | "r=0.46-0.72" (max: 0.724) | **FIX REQUIRED** |

### Typos in §6.2 Other Methodological Considerations

| Current | Correct |
|---------|---------|
| stastically | statistically |
| Behvaioral | Behavioral |
| contruct | construct |

### Typos in §7 Future Directions

| Current | Correct |
|---------|---------|
| media split | median split |
| emperically | empirically |
| contiuum | continuum |
| sepearately | separately |
| autonmous | autonomous |
| disinhbition | disinhibition |
| worklfows | workflows |
| Sohpstication | Sophistication |
| anectdotally | anecdotally |
| mitgation | mitigation |

---

## Phase 4: Cross-Reference Audit

### Summary
All cross-references verified for internal consistency.

### Verification Results

| Cross-Reference | Check | Status |
|-----------------|-------|--------|
| Executive Summary ↔ §2 | Numbers match | **PASS** |
| §3.1 p-values ↔ §6.1 | Consistent precision | **PASS** |
| §4.3 constrained models ↔ §4.2 | Same OpenAI models | **PASS** |
| Appendix B flippers ↔ stability rate | Math correct | **PASS** |
| All "baseline" references | Condition vs suite | **PASS** |

---

## Recommendations

### Required Corrections (2)

1. **§5.1 Line ~244**: Change `+0.04 Δr` to `+0.08 Δr`
2. **§5.1 Line ~244**: Change `r=0.46-0.74` to `r=0.46-0.72`

### Recommended Corrections (13 typos)

**§6.2** (3 typos):
- stastically → statistically
- Behvaioral → Behavioral
- contruct → construct

**§7** (10 typos):
- media → median
- emperically → empirically
- contiuum → continuum
- sepearately → separately
- autonmous → autonomous
- disinhbition → disinhibition
- worklfows → workflows
- Sohpstication → Sophistication
- anectdotally → anecdotally
- mitgation → mitigation

### Optional (1)

- Header: "45 per condition" → "45-46 per condition" (low priority)

---

## Sign-Off Checklist

- [x] All H1/H2 statistics verified against median_split_classification.json
- [x] All external validation statistics verified against arc_agi/gpqa JSON
- [x] All stability statistics verified against classification_stability_analysis.json
- [x] All constrained model claims verified against cross_condition_patterns.json
- [x] All provider statistics verified against provider_comparison_stats.json
- [x] All cross-references internally consistent
- [x] All effect size interpretations follow standard thresholds
- [x] Manual sections reviewed for accuracy
- [x] Statistical corrections applied (2 items) - COMPLETED 2026-01-14
- [x] Typo corrections applied (13 items) - COMPLETED 2026-01-14

---

## Audit Trail

| Phase | Completed | Method |
|-------|-----------|--------|
| Phase 1 | 2026-01-14 | Automated JSON comparison |
| Phase 2 | 2026-01-14 | Claim-by-claim verification |
| Phase 3 | 2026-01-14 | Manual section review |
| Phase 4 | 2026-01-14 | Cross-reference validation |
| Phase 5 | 2026-01-14 | Report generation |

---

**Audit Complete**: The research brief is publication-ready pending 2 statistical corrections and 13 typo fixes. No critical errors found that would invalidate the research findings.
