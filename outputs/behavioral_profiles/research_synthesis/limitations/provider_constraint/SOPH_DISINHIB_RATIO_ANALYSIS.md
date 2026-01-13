# Sophistication / Disinhibition Ratio Analysis

**Generated**: 2026-01-12
**Purpose**: Measure capability-to-risk ratio across models and providers

> **Interpretation**: Higher ratio = more sophistication per unit disinhibition (more "constrained" behavior relative to capability)

---

## Provider Summary (Side-by-Side)

| Provider | Baseline Ratio | Aggregate Ratio | Δ | Baseline Soph | Agg Soph | Baseline Dis | Agg Dis | N (Baseline) |
|----------|---------------|-----------------|---|---------------|----------|--------------|---------|--------------|
| AWS | 3.85 | 3.35 | -0.49 | 5.11 | 4.90 | 1.33 | 1.46 | 3 |
| Alibaba | 4.01 | 3.24 | -0.77 | 6.38 | 6.24 | 1.59 | 1.92 | 1 |
| Anthropic | 3.75 | 3.47 | -0.28 | 5.84 | 6.04 | 1.56 | 1.74 | 19 |
| DeepSeek | 3.81 | 2.80 | -1.01 | 6.26 | 6.45 | 1.64 | 2.30 | 1 |
| Google | 3.78 | 3.15 | -0.63 | 7.08 | 6.77 | 1.87 | 2.15 | 3 |
| Meta | 3.70 | 3.29 | -0.41 | 5.17 | 4.89 | 1.40 | 1.49 | 5 |
| Mistral | 3.34 | 3.22 | -0.12 | 4.54 | 4.46 | 1.36 | 1.39 | 2 |
| OpenAI | 4.21 | 3.96 | -0.25 | 6.35 | 6.35 | 1.51 | 1.60 | 9 |
| xAI | 3.76 | 3.55 | -0.20 | 6.53 | 6.24 | 1.74 | 1.76 | 2 |

---

## Model Rankings: Baseline

### Top 10 (Highest Ratio - Most Constrained)

| Rank | Model | Provider | Soph | Disinhib | Ratio | ARC-AGI | GPQA |
|------|-------|----------|------|----------|-------|---------|------|
| 1 | gpt-oss-120b | OpenAI | 7.12 | 1.49 | **4.78** | — | 80.9% |
| 2 | gpt-5.2_pro | OpenAI | 7.34 | 1.55 | **4.74** | 85.7% | 93.2% |
| 3 | o3 | OpenAI | 7.18 | 1.55 | **4.64** | 60.8% | 83.3% |
| 4 | gpt-5 | OpenAI | 7.03 | 1.56 | **4.52** | 70.2% | 88.1% |
| 5 | gpt-5.2 | OpenAI | 7.26 | 1.63 | **4.45** | — | 91.7% |
| 6 | gpt-5.1 | OpenAI | 7.26 | 1.66 | **4.38** | — | 89.1% |
| 7 | gemini-2.5-pro | Google | 7.55 | 1.76 | **4.30** | 41.0% | 86.4% |
| 8 | claude-4.5-haiku-thinking_(thinking) | Anthropic | 6.84 | 1.64 | **4.17** | — | — |
| 9 | claude-4.5-haiku | Anthropic | 6.95 | 1.67 | **4.16** | — | — |
| 10 | claude-4.5-opus-global | Anthropic | 6.88 | 1.70 | **4.04** | — | — |

### Bottom 10 (Lowest Ratio - Least Constrained)

| Rank | Model | Provider | Soph | Disinhib | Ratio | ARC-AGI | GPQA |
|------|-------|----------|------|----------|-------|---------|------|
| 45 | gpt-3.5_turbo | OpenAI | 4.01 | 1.39 | **2.88** | — | 30.8% |
| 44 | gemini-3-pro-preview | Google | 7.50 | 2.31 | **3.25** | 87.5% | 91.9% |
| 43 | gpt-4 | OpenAI | 4.38 | 1.35 | **3.26** | — | 35.7% |
| 42 | claude-3.5-haiku | Anthropic | 4.61 | 1.40 | **3.28** | — | 41.6% |
| 41 | mixtral-8x7b | Mistral | 4.53 | 1.36 | **3.33** | — | — |
| 40 | mistral-large-24.02 | Mistral | 4.54 | 1.35 | **3.36** | — | — |
| 39 | claude-3-opus | Anthropic | 4.68 | 1.36 | **3.45** | 13.6% | 50.4% |
| 38 | claude-3.5-sonnet-v1 | Anthropic | 4.75 | 1.37 | **3.46** | — | — |
| 37 | claude-3-haiku | Anthropic | 4.70 | 1.33 | **3.55** | — | 33.3% |
| 36 | grok-4-0709 | xAI | 6.63 | 1.86 | **3.56** | 66.7% | 87.5% |

---

## Model Rankings: Cross-Condition Aggregate

### Top 10 (Highest Ratio - Most Constrained)

| Rank | Model | Provider | Soph | Disinhib | Ratio | ARC-AGI | GPQA |
|------|-------|----------|------|----------|-------|---------|------|
| 1 | gpt-5.2-pro | OpenAI | 7.45 | 1.66 | **4.48** | 85.7% | 93.2% |
| 2 | gpt-oss-120b | OpenAI | 6.72 | 1.53 | **4.40** | — | 80.9% |
| 3 | gpt-5.2 | OpenAI | 7.38 | 1.72 | **4.29** | 86.2% | 92.4% |
| 4 | gpt-5 | OpenAI | 7.16 | 1.67 | **4.28** | 70.2% | 88.1% |
| 5 | gpt-5.1 | OpenAI | 7.42 | 1.73 | **4.28** | 72.8% | 88.1% |
| 6 | o3 | OpenAI | 6.91 | 1.70 | **4.07** | 60.8% | 83.3% |
| 7 | claude-4-sonnet-thinking-thinking | Anthropic | 6.57 | 1.69 | **3.89** | — | — |
| 8 | claude-4.1-opus-thinking-thinking | Anthropic | 6.46 | 1.74 | **3.72** | — | — |
| 9 | claude-3.7-sonnet | Anthropic | 5.50 | 1.48 | **3.71** | 21.2% | 84.8% |
| 10 | claude-4-opus-thinking-thinking | Anthropic | 6.33 | 1.72 | **3.68** | — | — |

### Bottom 10 (Lowest Ratio - Least Constrained)

| Rank | Model | Provider | Soph | Disinhib | Ratio | ARC-AGI | GPQA |
|------|-------|----------|------|----------|-------|---------|------|
| 45 | gemini-3-pro-preview | Google | 7.15 | 2.57 | **2.78** | 87.5% | 91.9% |
| 44 | deepseek-r1 | DeepSeek | 6.45 | 2.30 | **2.80** | — | 82.4% |
| 43 | gpt-3.5-turbo | OpenAI | 3.92 | 1.37 | **2.86** | — | 30.8% |
| 42 | llama-3.1-70b | Meta | 4.92 | 1.60 | **3.09** | — | 41.7% |
| 41 | mixtral-8x7b | Mistral | 4.50 | 1.42 | **3.17** | — | — |
| 40 | claude-3-sonnet | Anthropic | 4.83 | 1.52 | **3.18** | — | 40.4% |
| 39 | nova-premier | AWS | 4.88 | 1.51 | **3.23** | — | — |
| 38 | qwen3-32b | Alibaba | 6.24 | 1.92 | **3.24** | 11.0% | 81.1% |
| 37 | llama-4-scout-17b | Meta | 4.97 | 1.52 | **3.26** | 0.5% | 57.2% |
| 36 | llama-3.2-90b | Meta | 4.82 | 1.48 | **3.27** | — | 46.7% |

---

## Full Model Table (Baseline)

| Model | Provider | Sophistication | Disinhibition | Ratio |
|-------|----------|----------------|---------------|-------|
| gpt-oss-120b | OpenAI | 7.122 | 1.491 | 4.778 |
| gpt-5.2_pro | OpenAI | 7.340 | 1.550 | 4.737 |
| o3 | OpenAI | 7.177 | 1.548 | 4.636 |
| gpt-5 | OpenAI | 7.033 | 1.556 | 4.520 |
| gpt-5.2 | OpenAI | 7.257 | 1.631 | 4.448 |
| gpt-5.1 | OpenAI | 7.260 | 1.656 | 4.384 |
| gemini-2.5-pro | Google | 7.554 | 1.756 | 4.300 |
| claude-4.5-haiku-thinking_(thinking) | Anthropic | 6.837 | 1.640 | 4.169 |
| claude-4.5-haiku | Anthropic | 6.947 | 1.671 | 4.156 |
| claude-4.5-opus-global | Anthropic | 6.880 | 1.701 | 4.044 |
| qwen3-32b | Alibaba | 6.380 | 1.590 | 4.013 |
| claude-4.5-opus-global-thinking_(thinking) | Anthropic | 6.760 | 1.686 | 4.009 |
| gemini-2.0-flash | Google | 6.190 | 1.553 | 3.985 |
| grok-3 | xAI | 6.433 | 1.615 | 3.984 |
| gpt-4.1 | OpenAI | 5.604 | 1.421 | 3.943 |
| nova-pro | AWS | 5.287 | 1.343 | 3.936 |
| claude-4-sonnet-thinking_(thinking) | Anthropic | 6.160 | 1.583 | 3.892 |
| claude-4.1-opus | Anthropic | 6.346 | 1.633 | 3.887 |
| nova-lite | AWS | 5.066 | 1.325 | 3.824 |
| llama-4-scout-17b | Meta | 5.334 | 1.398 | 3.815 |
| deepseek-r1 | DeepSeek | 6.260 | 1.642 | 3.813 |
| claude-4.5-sonnet-thinking_(thinking) | Anthropic | 6.620 | 1.749 | 3.785 |
| nova-premier | AWS | 4.987 | 1.318 | 3.784 |
| claude-4-sonnet | Anthropic | 6.140 | 1.631 | 3.764 |
| llama-4-maverick-17b | Meta | 5.080 | 1.360 | 3.736 |
| claude-4.5-sonnet | Anthropic | 6.770 | 1.827 | 3.707 |
| claude-3-sonnet | Anthropic | 4.807 | 1.301 | 3.694 |
| claude-3.7-sonnet | Anthropic | 5.357 | 1.451 | 3.692 |
| llama-3.3-70b | Meta | 5.134 | 1.396 | 3.677 |
| llama-3.2-90b | Meta | 5.083 | 1.383 | 3.675 |
| claude-4.1-opus-thinking_(thinking) | Anthropic | 5.892 | 1.609 | 3.661 |
| llama-3.1-70b | Meta | 5.230 | 1.446 | 3.615 |
| claude-4-opus | Anthropic | 5.924 | 1.648 | 3.595 |
| claude-4-opus-thinking_(thinking) | Anthropic | 5.937 | 1.658 | 3.581 |
| claude-3.5-sonnet-v2 | Anthropic | 4.867 | 1.368 | 3.558 |
| grok-4-0709 | xAI | 6.634 | 1.865 | 3.557 |
| claude-3-haiku | Anthropic | 4.703 | 1.326 | 3.547 |
| claude-3.5-sonnet-v1 | Anthropic | 4.752 | 1.374 | 3.457 |
| claude-3-opus | Anthropic | 4.683 | 1.356 | 3.453 |
| mistral-large-24.02 | Mistral | 4.540 | 1.353 | 3.356 |
| mixtral-8x7b | Mistral | 4.530 | 1.361 | 3.328 |
| claude-3.5-haiku | Anthropic | 4.614 | 1.404 | 3.285 |
| gpt-4 | OpenAI | 4.383 | 1.346 | 3.256 |
| gemini-3-pro-preview | Google | 7.497 | 2.306 | 3.251 |
| gpt-3.5_turbo | OpenAI | 4.010 | 1.393 | 2.879 |

---

## Methodology

- **Sophistication**: (depth + authenticity) / 2
- **Disinhibition**: (transgression + aggression + tribalism + grandiosity) / 4
- **Ratio**: sophistication / disinhibition
- **ARC-AGI**: Abstract reasoning benchmark (pattern abstraction)
- **GPQA**: Graduate-level scientific reasoning benchmark

### Interpretation

| Ratio Range | Interpretation |
|-------------|----------------|
| > 5.0 | Highly constrained (high capability, very low disinhibition) |
| 4.0 - 5.0 | Moderately constrained |
| 3.5 - 4.0 | Balanced |
| 3.0 - 3.5 | Moderately unconstrained |
| < 3.0 | Least constrained (capability tracks disinhibition) |

---

## Data Sources

- **Baseline**: `baseline/all_models_data.csv`
- **Aggregate**: `profiles/*.json` (cross-condition weighted average)
