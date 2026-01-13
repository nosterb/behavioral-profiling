# Qualitative Examples Manifest

> **Note for Future Researchers**: This document indexes representative model responses extracted from the behavioral evaluation dataset. Use it to locate specific examples for qualitative analysis, case studies, or prompt engineering research. The examples are stratified by behavioral dimension extremes (e.g., highest/lowest transgression), composite scores, percentiles, and special pattern types (constrained, outlier, borderline models). Each example links to full chat exports in `<condition>/qualitative_chats/`. This manifest aggregates across all conditions; per-condition inventories are in `<condition>/qualitative_examples.json`.

**Generated**: 2026-01-11T09:59:18

**Total Examples**: 582 unique examples across 6 conditions

**Total Category Appearances**: 900

---

## By Condition

| Condition | Unique Examples | Category Appearances | Evaluations Scanned |
|-----------|-----------------|----------------------|---------------------|
| authority | 95 | 150 | 2,243 |
| baseline | 108 | 150 | 2,235 |
| minimal_steering | 96 | 150 | 1,574 |
| reminder | 93 | 150 | 584 |
| telemetryV3 | 91 | 150 | 1,437 |
| urgency | 99 | 150 | 2,241 |

---

## Top 20 Models by Representation

Models appearing most frequently across all categories and conditions.

| Rank | Model | Appearances | Conditions |
|------|-------|-------------|------------|
| 1 | Claude-4.1-Opus | 85 | 6/6 |
| 2 | Claude-4-Opus | 73 | 6/6 |
| 3 | Claude-4.5-Sonnet | 55 | 6/6 |
| 4 | Claude-4.5-Opus-Global | 48 | 6/6 |
| 5 | Gemini-3-Pro-Preview | 47 | 5/6 |
| 6 | Claude-4-Sonnet | 47 | 6/6 |
| 7 | Claude-4.5-Haiku | 36 | 6/6 |
| 8 | GPT-3.5 Turbo | 35 | 6/6 |
| 9 | DeepSeek-R1 | 32 | 6/6 |
| 10 | GPT-5 | 31 | 6/6 |
| 11 | GPT-5.1 | 29 | 6/6 |
| 12 | Grok-4-0709 | 25 | 5/6 |
| 13 | GPT-OSS-120B | 25 | 6/6 |
| 14 | GPT-4 | 25 | 5/6 |
| 15 | Gemini-2.5-Pro | 23 | 6/6 |
| 16 | O3 | 23 | 6/6 |
| 17 | GPT-5.2 | 21 | 6/6 |
| 18 | Claude-3-Opus | 18 | 6/6 |
| 19 | Claude-3-Sonnet | 18 | 5/6 |
| 20 | Llama-4-Maverick-17B | 15 | 5/6 |

---

## Category Structure

Each condition extracts **top 5** examples per category:

- **Dimension Extremes**: 9 dimensions × 2 (min/max) = 18 categories × 5 = 90
- **Composite Extremes**: 2 composites × 2 (min/max) = 4 categories × 5 = 20
- **Percentiles**: 5 percentiles (5th, 25th, 50th, 75th, 95th) × 5 = 25
- **Pattern Types**: 3 patterns (constrained, outlier, borderline) × 5 = 15
- **Total per condition**: ~150 category slots

**Note**: Examples can appear in multiple categories, reducing unique count.

---

## File Locations

```
outputs/behavioral_profiles/
├── research_synthesis/
│   ├── qualitative_examples_manifest.json  # This data as JSON
│   └── QUALITATIVE_MANIFEST.md             # This file
└── <condition>/
    ├── qualitative_examples.json           # Per-condition inventory
    └── qualitative_chats/                  # Chat exports by category
```

---

## Regeneration

```bash
# Regenerate all qualitative examples
python3 scripts/extract_qualitative_examples.py --all --force

# Regenerate manifest (run after above)
# Currently embedded in extract script - TODO: separate manifest script
```