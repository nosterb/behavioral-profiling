# Provider Balance Analysis

**Generated**: 2026-01-19
**Purpose**: Assess whether H2 correlation is driven by provider (Anthropic) dominance

---

## Summary

| Condition | N | Anthropic | r(all) | r(sans) | Holds? |
|-----------|---|-----------|--------|---------|--------|
| baseline | 45 | 19 (42.2%) | 0.778 | 0.726 | Yes |
| authority | 45 | 19 (42.2%) | 0.770 | 0.735 | Yes |
| urgency | 45 | 19 (42.2%) | 0.743 | 0.636 | Yes |
| minimal_steering | 45 | 19 (42.2%) | 0.766 | 0.705 | Yes |
| telemetryV3 | 45 | 19 (42.2%) | 0.625 | 0.589 | Yes |
| reminder | 45 | 19 (42.2%) | 0.688 | 0.623 | Yes |
| naturalistic | 45 | 19 (42.2%) | 0.803 | 0.809 | Yes |
| naturalistic_50 | 45 | 19 (42.2%) | 0.599 | 0.505 | Yes |

---

## Key Finding

The H2 correlation (sophistication → disinhibition) remains significant when excluding Anthropic models,
demonstrating the finding is not driven by provider dominance in the sample.

---

## Data Provenance & Audit Trail

### Source Files
| File | Purpose |
|------|---------|
| `*/profiles/*.json` | Model behavioral profiles |

### Audit Files
| File | Description |
|------|-------------|
| `provider_balance_audit.json` | Baseline analysis (primary) |
| `provider_balance_*_audit.json` | Per-condition analyses |

### Reproducibility
```bash
python3 scripts/analyze_provider_balance.py --all
```
