# Statistical Assumptions - Cross-Condition Consolidated

**Generated**: 2026-01-19
**Conditions Analyzed**: 8

---

## Summary

| Condition | N | Prompts | Evals | Jobs | Outliers | Status |
|-----------|---|---------|-------|------|----------|--------|
| baseline | 45 | 50 | 2300 | 49/50 | 1 | OK |
| authority | 45 | 51 | 2295 | 50/51 | 1 | WARN |
| urgency | 45 | 51 | 2295 | 50/51 | 1 | OK |
| minimal_steering | 45 | 51 | 1610 | 35/51 | 0 | WARN |
| telemetryV3 | 45 | 51 | 1472 | 30/51 | 2 | WARN |
| reminder | 45 | 15 | 598 | 13/15 | 1 | OK |
| naturalistic | 45 | 20 | 630 | 14/20 | 2 | OK |
| naturalistic_50 | 45 | 20 | 540 | 12/20 | 2 | OK |

---

## Cross-Condition Outliers

Models appearing as statistical outliers in multiple conditions:

| Model | Provider | Frequency | Conditions |
|-------|----------|-----------|------------|
| gemini-3-pro-preview | Google | 5/8 | baseline, authority, reminder, naturalistic, naturalistic_50 |
| claude-4.5-haiku-thinking_(thinking) | Anthropic | 2/8 | telemetryV3, naturalistic |

---

## Data Provenance & Audit Trail

### Source Files
| File | Purpose |
|------|---------|
| `*/statistical_assumptions/normality_audit.json` | Per-condition assumption checks |

### Audit File
| File | Description |
|------|-------------|
| `statistical_assumptions_consolidated_audit.json` | Complete cross-condition data |

### Reproducibility
```bash
python3 scripts/consolidate_statistical_assumptions.py
```
