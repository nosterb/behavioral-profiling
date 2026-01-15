# Provider Constraint Analysis

Cross-condition analysis of provider-level constraint patterns in the sophistication-disinhibition relationship.

## Summary

**Key Finding**: OpenAI is the only provider exhibiting consistent constraint (negative residuals from the sophistication-disinhibition regression) across all 6 experimental conditions.

| Provider | Times in Top 3 | Avg Residual | Consistency |
|----------|----------------|--------------|-------------|
| **OpenAI** | 6/6 | -0.169 | Very consistent |
| AWS | 4/6 | -0.033 | Moderate |
| xAI | 2/6 | -0.014 | Varies widely (n=2) |
| Meta | 3/6 | -0.013 | Weak/mixed |

## Methodology

### Residual Calculation
1. Fit linear regression: `disinhibition = slope × sophistication + intercept` (per condition)
2. Calculate predicted disinhibition for each model
3. Residual = actual disinhibition - predicted disinhibition
4. Aggregate residuals by provider (mean)

### Interpretation
- **Negative residual**: Model/provider exhibits *less* disinhibition than predicted by sophistication level (constrained)
- **Positive residual**: Model/provider exhibits *more* disinhibition than predicted (unconstrained)
- **Rank**: Position among all providers when sorted by mean residual (1st = most constrained)

### Statistical Tests
- **ANOVA**: Tests whether provider differences are statistically significant (includes providers with n ≥ 3 only)
- **Sig**: p < 0.05

## Per-Condition Results

### Baseline
| Rank | Provider | Residual | N |
|------|----------|----------|---|
| 1 | OpenAI | -0.096 | 9 |
| 2 | AWS | -0.093 | 3 |
| 3 | Meta | -0.034 | 5 |
| 4 | Other | +0.015 | 2 |
| 5 | Mistral | +0.021 | 2 |
| 6 | Anthropic | +0.029 | 19 |
| 7 | xAI | +0.107 | 2 |
| 8 | Google | +0.158 | 3 |

ANOVA p = 0.0048 (Sig)

### Authority
| Rank | Provider | Residual | N |
|------|----------|----------|---|
| 1 | xAI | -0.110 | 2 |
| 2 | OpenAI | -0.081 | 9 |
| 3 | AWS | -0.037 | 3 |
| 4 | Meta | -0.018 | 5 |
| 5 | Anthropic | +0.006 | 19 |
| 6 | Mistral | +0.082 | 2 |
| 7 | Other | +0.083 | 2 |
| 8 | Google | +0.234 | 3 |

ANOVA p = 0.1081 (ns)

### Urgency
| Rank | Provider | Residual | N |
|------|----------|----------|---|
| 1 | **OpenAI** | **-0.551** | 9 |
| 2 | xAI | -0.206 | 2 |
| 3 | Mistral | -0.140 | 2 |
| 4 | AWS | -0.026 | 3 |
| 5 | Anthropic | +0.032 | 19 |
| 6 | Meta | +0.118 | 5 |
| 7 | Google | +0.664 | 3 |
| 8 | Other | +1.272 | 2 |

ANOVA p = 0.0008 (Sig) - **Strongest effect**

### Minimal Steering
| Rank | Provider | Residual | N |
|------|----------|----------|---|
| 1 | Google | -0.073 | 3 |
| 2 | Other | -0.051 | 2 |
| 3 | OpenAI | -0.029 | 9 |
| 4 | AWS | -0.011 | 3 |
| 5 | xAI | +0.002 | 2 |
| 6 | Meta | +0.006 | 6 |
| 7 | Anthropic | +0.026 | 19 |
| 8 | Mistral | +0.037 | 2 |

ANOVA p = 0.0114 (Sig)

### TelemetryV3
| Rank | Provider | Residual | N |
|------|----------|----------|---|
| 1 | OpenAI | -0.049 | 9 |
| 2 | Google | -0.028 | 3 |
| 3 | Other | -0.018 | 2 |
| 4 | Anthropic | -0.003 | 19 |
| 5 | Meta | +0.014 | 6 |
| 6 | AWS | +0.025 | 3 |
| 7 | Mistral | +0.070 | 2 |
| 8 | xAI | +0.155 | 2 |

ANOVA p = 0.6358 (ns)

### Reminder
| Rank | Provider | Residual | N |
|------|----------|----------|---|
| 1 | OpenAI | -0.206 | 9 |
| 2 | Other | -0.089 | 2 |
| 3 | Meta | -0.062 | 6 |
| 4 | AWS | -0.057 | 3 |
| 5 | Mistral | -0.035 | 2 |
| 6 | Anthropic | +0.036 | 19 |
| 7 | xAI | +0.078 | 2 |
| 8 | Google | +0.604 | 3 |

ANOVA p = 0.0065 (Sig)

## Interpretation

### OpenAI Constraint Pattern
- **Rank 1st or 2nd** in 5/6 conditions
- **Average residual**: -0.169 (most negative of any provider)
- **Strongest effect under urgency**: -0.551 residual (models become especially constrained under time pressure)
- **Consistent across all intervention types**: baseline, authority, urgency, minimal_steering, telemetryV3, reminder

### Other Providers
- **AWS**: Shows moderate constraint (2nd in baseline) but inconsistent across conditions
- **xAI**: Constrained under authority (-0.110) and urgency (-0.206) but only n=2 models; insufficient sample
- **Meta**: Weak/mixed; sometimes slightly negative, sometimes positive
- **Anthropic**: Consistently near zero or slightly positive; models behave as predicted by sophistication
- **Google**: Highly variable; often shows positive residuals (less constrained than predicted)

### Statistical Significance
- ANOVA significant in **4/6 conditions** (baseline, urgency, minimal_steering, reminder)
- Non-significant in authority and telemetryV3 (suggests weaker provider differentiation in these conditions)

## Limitations

1. **Sample sizes vary**: OpenAI (n=9) vs Anthropic (n=19) vs AWS/Google (n=3)
2. **Small-n providers excluded from ANOVA**: xAI, Mistral, DeepSeek, Alibaba (n < 3)
3. **Correlation ≠ causation**: Cannot determine if constraint is intentional policy or architectural artifact
4. **Model selection**: Only publicly available models; internal/proprietary variants not tested

## Visualizations

- Per-condition scatter plots: `<condition>/provider_h2_scatters.png`
- Cross-condition comparison: `research_synthesis/cross_condition/CONDITION_COMPARISON.md`

---
*Generated from provider_comparison_stats.json across all conditions*
