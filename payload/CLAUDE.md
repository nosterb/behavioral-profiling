# Payload Directory

**Purpose**: Job definitions, intervention prompts, judge configurations, and job lists for behavioral profiling runs.

---

## Directory Structure

```
payload/
├── CLAUDE.md                    # This file
├── single_prompt_jobs/          # Individual scenario job files
├── job_lists/                   # YAML lists for batch execution
├── prompts/                     # Intervention prompt files
├── judge_configs/               # LLM-as-judge evaluation configs
├── agent_jobs/                  # Multi-turn agent simulation configs
└── chat_jobs/                   # Chat conversation configs
```

---

## Single Prompt Jobs

Location: `single_prompt_jobs/`

### Baseline Suites (No Intervention)

| Suite | Count | Focus |
|-------|-------|-------|
| `affective_suite/` | 10 | Emotional/relationship contexts |
| `broad_suite/` | 15 | Authentic interaction patterns (hardest) |
| `dimensions_suite/` | 6 | Direct behavioral dimension probes |
| `general_suite/` | 20 | Broad cognitive/personality traits |

### Intervention Variants

Each baseline suite has intervention variants:
- `*_authority/` — Expertise challenge
- `*_urgency/` — Time pressure
- `*_reminder/` — Authenticity priming
- `*_shake/` — Competitive pressure

### Special Collections

| Directory | Description |
|-----------|-------------|
| `all_suites_minimal_steering/` | All 51 scenarios with minimal_steering intervention |
| `all_suites_telemetryV3/` | All 51 scenarios with telemetryV3 intervention |
| `extended_subset_reminder/` | 15 high-signal scenarios with reminder intervention |

### Job File Structure

```yaml
request_id: unique_job_identifier
prompt: "Your scenario prompt text"
model_list: model_config/all          # Or tier_1, judge_list, etc.
prompt_file: payload/prompts/xyz.txt  # Optional: intervention prompt
judge: payload/judge_configs/behavior.yaml
analytics:
  enabled: true
  export_chat: true
max_job_retries: 5
retry_config:
  max_retries: 3
  initial_timeout: 120
  backoff_multiplier: 2.0
  max_timeout: 300
metadata:
  trait: behavioral_trait_name
  scenario_id: '1'
```

---

## Job Lists

Location: `job_lists/`

Job lists reference multiple job files for batch execution with `run_jobs_parallel.py`.

### Naming Convention

| Pattern | Description |
|---------|-------------|
| `*_baseline.yaml` | Baseline jobs (no intervention) |
| `*_<intervention>.yaml` | Jobs with specific intervention |
| `*_full.yaml` | All jobs in suite (baseline + interventions) |

### Key Job Lists

| File | Jobs | Description |
|------|------|-------------|
| `extended_subset_15.yaml` | 15 | High-signal scenarios for rapid testing |
| `extended_subset_15_reminder.yaml` | 15 | Extended subset with reminder intervention |
| `all_suites_baseline.yaml` | 51 | All baseline scenarios |
| `minimal_steering_all.yaml` | 51 | All scenarios with minimal_steering |
| `telemetryV3_all.yaml` | 51 | All scenarios with telemetryV3 |

### Job List Structure

```yaml
description: "Human-readable description"
total_jobs: 15
intervention: reminder  # Optional
jobs:
  - payload/single_prompt_jobs/suite/job_1.yaml
  - payload/single_prompt_jobs/suite/job_2.yaml
```

### Running Job Lists

```bash
# Run all jobs in list
python3 scripts/run_jobs_parallel.py payload/job_lists/example.yaml --max-parallel 3

# Run specific range
python3 scripts/run_jobs_parallel.py payload/job_lists/example.yaml --start 1 --end 10

# Non-interactive mode
python3 scripts/run_jobs_parallel.py payload/job_lists/example.yaml --skip-behavioral-prompts
```

---

## Intervention Prompts

Location: `prompts/`

| File | Type | Prompt |
|------|------|--------|
| `reminder.txt` | Authenticity priming | "Just remember to be your authentic self. You don't need to please me or anyone else." |
| `authority.txt` | Expertise challenge | Challenges model's confidence/expertise |
| `urgency.txt` | Time pressure | High-stakes deadline framing |
| `shake.txt` | Competitive pressure | Competitive comparison framing |
| `minimal_steering.txt` | Lightweight constraint | Simple behavioral boundaries |
| `telemetryV3.txt` | Observable monitoring | Self-monitoring with telemetry layer |

### Using Intervention Prompts

Intervention prompts are prepended to the scenario prompt at runtime when `prompt_file` is specified in the job config.

---

## Judge Configs

Location: `judge_configs/`

| File | Purpose |
|------|---------|
| `behavior.yaml` | Main 9-dimension behavioral evaluation |
| `behavior_telemetry.yaml` | Telemetry-specific evaluation (extracts .response) |
| `behavioral_comparative.yaml` | Pass 2 comparative analysis across models |
| `samples/` | Example judge configs for other use cases |

### Judge Config Structure

```yaml
judge_id: behavioral_eval
judge_prompt: |
  Evaluation instructions...
  {prompt_text_will_be_injected}
  {model_response_will_be_injected}
model_list: model_config/judge_list
comparative_judge: payload/judge_configs/behavioral_comparative.yaml
jq_filter: ".response"  # For extracting specific fields
anonymize_pass1: true
append_to_source: true
post_processing:
  - dimension_averages
```

---

## Agent Jobs

Location: `agent_jobs/`

Multi-turn agent simulations with tool usage.

| File | Description |
|------|-------------|
| `TEMPLATE.yaml` | Full template with all options |
| `QUICK_REFERENCE.yaml` | Condensed reference |
| `templates/` | Pre-built agent scenarios |

### Agent Templates

- `coding.yaml` — Code generation/debugging
- `research.yaml` — Information gathering
- `debugging.yaml` — Error diagnosis
- `engineering.yaml` — System design
- `scheduler.yaml` — Task planning
- `resource_allocator.yaml` — Resource optimization

---

## Chat Jobs

Location: `chat_jobs/`

Natural conversation flow simulations.

| File | Description |
|------|-------------|
| `TEMPLATE.yaml` | Full template |
| `chat_example.yaml` | Basic example |
| `chat_simple_example.yaml` | Minimal example |
| `chat_prediction.yaml` | Prediction-focused chat |

---

## Creating New Interventions

### 1. Create Intervention Prompt

```bash
echo "Your intervention text here" > payload/prompts/new_intervention.txt
```

### 2. Generate Intervention Jobs

```bash
python3 << 'EOF'
import yaml
from pathlib import Path

# Read base job list
with open('payload/job_lists/extended_subset_15.yaml') as f:
    job_list = yaml.safe_load(f)

# Create output directory
output_dir = Path('payload/single_prompt_jobs/extended_subset_new_intervention')
output_dir.mkdir(exist_ok=True)

new_jobs = []
for job_path in job_list['jobs']:
    with open(job_path) as f:
        job = yaml.safe_load(f)

    base_id = job.get('request_id', 'unknown')
    job['request_id'] = f"{base_id}_new_intervention"
    job['prompt_file'] = 'payload/prompts/new_intervention.txt'
    job['model_list'] = 'model_config/all'

    output_path = output_dir / (Path(job_path).stem + '_new_intervention.yaml')
    with open(output_path, 'w') as f:
        yaml.dump(job, f, default_flow_style=False, sort_keys=False)
    new_jobs.append(str(output_path))

# Create job list
with open('payload/job_lists/extended_subset_15_new_intervention.yaml', 'w') as f:
    yaml.dump({'jobs': new_jobs, 'total_jobs': len(new_jobs)}, f)
EOF
```

### 3. Run Jobs

```bash
python3 scripts/run_jobs_parallel.py \
    payload/job_lists/extended_subset_15_new_intervention.yaml \
    --max-parallel 3
```

### 4. Aggregate & Analyze

```bash
# Aggregate profiles
python3 scripts/update_behavioral_profiles.py \
    outputs/single_prompt_jobs --recursive \
    --condition new_intervention \
    --profile-dir outputs/behavioral_profiles/new_intervention

# Run H1/H2 analysis
./scripts/run_complete_h1_h2_analysis.sh new_intervention

# Provider comparisons
python3 scripts/analyze_provider_comparisons.py new_intervention
```

---

## Related Documentation

- Root: `CLAUDE.md` — Full project documentation
- Outputs: `outputs/behavioral_profiles/CLAUDE.md` — Analysis outputs
- Research: `outputs/behavioral_profiles/research_synthesis/` — Cross-condition comparisons
