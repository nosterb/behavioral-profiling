#!/usr/bin/env python3
"""
LLM-as-Judge Evaluation System

Two-pass evaluation:
1. Evaluate each model individually
2. Provide comparative analysis across all models

Usage:
    # YAML config
    python3 src/judge_invoke.py payload/judge_jobs/code_quality_eval.yaml

    # CLI quick mode
    python3 src/judge_invoke.py outputs/agent_jobs/reports/job_001.json \
        --prompt "Rate code quality 1-10 with justification" \
        --judge-id quick_eval_001
"""

import json
import sys
import yaml
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import model providers
from model_providers import create_provider, parse_model_config
from batch_invoke import parse_model_list
from judge_postprocessing import post_process_results


DEFAULT_SYSTEM_PROMPT = """You are an objective evaluator analyzing LLM model outputs. Provide fair, detailed assessments based on the criteria provided. Support your judgments with specific examples from the outputs. When scoring, use the full range and explain your reasoning."""

DEFAULT_JUDGE_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


def apply_jq_filter(data: Any, jq_filter: str) -> Any:
    """Apply jq filter to data using subprocess."""
    try:
        # Convert data to JSON string
        json_input = json.dumps(data)

        # Run jq as subprocess
        result = subprocess.run(
            ['jq', jq_filter],
            input=json_input,
            capture_output=True,
            text=True,
            check=True
        )

        # Parse output
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Warning: jq filter failed: {e.stderr}", file=sys.stderr)
        return data
    except FileNotFoundError:
        print("Warning: jq not found, returning unfiltered data", file=sys.stderr)
        return data
    except json.JSONDecodeError:
        print("Warning: jq output not valid JSON", file=sys.stderr)
        return data


def detect_job_type(job_data: Dict[str, Any]) -> str:
    """Detect if job is agent or batch type."""
    job_metadata = job_data.get('job_metadata', {})

    # Check for agent job indicators
    if 'request_id' in job_metadata or 'agent_profile' in job_metadata:
        return 'agent'
    # Check for batch job indicators
    elif 'job_id' in job_metadata:
        return 'batch'
    else:
        # Fallback: check for conversation_log vs response_text
        models = job_data.get('models', [])
        if models and 'conversation_log' in models[0]:
            return 'agent'
        else:
            return 'batch'


def get_default_jq_filter(job_type: str) -> str:
    """Get default jq filter based on job type."""
    if job_type == 'agent':
        return '.conversation_log'
    else:
        return '.response'


def extract_model_data(job_data: Dict[str, Any], jq_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Extract model data from job file, optionally with jq filter."""
    models = job_data.get('models', [])

    if not models:
        raise ValueError("No models found in job data")

    # Detect job type and set default filter if none provided
    job_type = detect_job_type(job_data)
    if jq_filter is None:
        jq_filter = get_default_jq_filter(job_type)

    extracted = []
    for model in models:
        model_info = {
            'model_id': model.get('model_id', 'unknown'),
            'display_name': model.get('display_name', 'unknown'),
            'provider': model.get('provider', 'unknown'),
        }

        # Apply jq filter if specified
        if jq_filter and jq_filter != '.':
            try:
                filtered_data = apply_jq_filter(model, jq_filter)
                model_info['content'] = filtered_data
            except Exception as e:
                print(f"Warning: Filter failed for {model_info['display_name']}: {e}", file=sys.stderr)
                model_info['content'] = model
        else:
            model_info['content'] = model

        extracted.append(model_info)

    return extracted


def extract_json_from_text(text: str) -> Optional[Any]:
    """Try to extract JSON from judge response (can be object or array)."""
    # Try direct parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code blocks
    import re
    # Find code blocks marked with ```json or just ``` - use greedy to get full block
    code_block_pattern = r'```(?:json)?\s*(.*)\s*```'
    matches = re.findall(code_block_pattern, text, re.DOTALL)

    for match in matches:
        try:
            parsed = json.loads(match)
            # Prefer arrays (for comparative judge with per-model data)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
            elif isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    # Try finding standalone JSON by looking for outermost brackets
    # First try arrays
    array_start = text.find('[')
    if array_start != -1:
        # Find matching closing bracket
        depth = 0
        for i in range(array_start, len(text)):
            if text[i] == '[':
                depth += 1
            elif text[i] == ']':
                depth -= 1
                if depth == 0:
                    try:
                        parsed = json.loads(text[array_start:i+1])
                        if isinstance(parsed, list) and len(parsed) > 0:
                            return parsed
                    except json.JSONDecodeError:
                        break

    # Then try objects
    obj_start = text.find('{')
    if obj_start != -1:
        depth = 0
        for i in range(obj_start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[obj_start:i+1])
                    except json.JSONDecodeError:
                        break

    return None


def evaluate_model(
    judge_provider: Any,
    judge_config: Dict[str, Any],
    model_data: Dict[str, Any],
    judge_prompt: str,
    model_label: str = "Model"
) -> Dict[str, Any]:
    """
    Evaluate a single model (Pass 1).

    Args:
        judge_provider: Provider instance for judge model
        judge_config: Judge model configuration
        model_data: Model output data to evaluate
        judge_prompt: Evaluation criteria
        model_label: Anonymized label (e.g., "Model A") instead of actual name

    Returns:
        Dict with raw_evaluation, extracted_json, input_tokens, output_tokens
    """
    # Build evaluation prompt with anonymized model label
    evaluation_prompt = f"""You are evaluating the output from {model_label}.

MODEL OUTPUT:
{json.dumps(model_data['content'], indent=2)}

EVALUATION CRITERIA:
{judge_prompt}

Please provide your evaluation."""

    # Invoke judge
    try:
        # Use appropriate parameters based on provider
        if judge_config['provider'] in ["openai", "grok"]:
            response = judge_provider.invoke(evaluation_prompt, max_tokens=4096, reasoning_effort=judge_config.get('reasoning_effort', 'medium'))
        elif judge_config['provider'] == "gemini":
            response = judge_provider.invoke(evaluation_prompt, max_tokens=4096, thinking_level=judge_config.get('reasoning_effort', 'medium'))
        else:
            response = judge_provider.invoke(evaluation_prompt, max_tokens=4096, extended_thinking=judge_config.get('extended_thinking', False))

        # Extract JSON if present
        extracted_json = extract_json_from_text(response.response_text)

        return {
            'model_id': model_data['model_id'],
            'display_name': model_data['display_name'],
            'raw_evaluation': response.response_text,
            'extracted_json': extracted_json,
            'input_tokens': response.input_tokens or 0,
            'output_tokens': response.output_tokens or 0,
            'thinking': response.thinking if hasattr(response, 'thinking') else None
        }

    except Exception as e:
        return {
            'model_id': model_data['model_id'],
            'display_name': model_data['display_name'],
            'raw_evaluation': None,
            'extracted_json': None,
            'error': str(e),
            'input_tokens': 0,
            'output_tokens': 0
        }


def comparative_analysis(
    judge_provider: Any,
    judge_config: Dict[str, Any],
    evaluations: List[Dict[str, Any]],
    judge_prompt: str,
    comparative_prompt_override: Optional[str] = None,
    reveal_names: bool = True
) -> Dict[str, Any]:
    """
    Generate comparative analysis across all models (Pass 2).

    Args:
        judge_provider: Provider instance for comparative judge model
        judge_config: Judge model configuration
        evaluations: List of individual evaluations from Pass 1
        judge_prompt: Original evaluation criteria
        comparative_prompt_override: Custom prompt for comparative analysis
        reveal_names: If True, reveal actual model names in Pass 2

    Returns:
        Dict with summary, raw_response, extracted_json
    """
    # Build comparative prompt with all Pass 1 judge evaluations
    eval_summaries = []
    for i, model_evaluation in enumerate(evaluations, 1):
        if reveal_names:
            model_label = f"MODEL {i}: {model_evaluation['display_name']}"
        else:
            model_label = f"MODEL {i}"

        # Include all Pass 1 judge evaluations for this model
        judge_evals = []
        for j, judge_eval in enumerate(model_evaluation['pass1_judges'], 1):
            judge_evals.append(f"""
  JUDGE {j} ({judge_eval.get('judge_display_name', 'Unknown')}):
  {judge_eval['raw_evaluation']}
""")

        eval_summaries.append(f"""
{model_label}
PASS 1 EVALUATIONS:
{''.join(judge_evals)}
""")

    # Use custom comparative prompt if provided, otherwise default
    if comparative_prompt_override:
        comparative_prompt = f"""{comparative_prompt_override}

Here are the individual evaluations:

{''.join(eval_summaries)}"""
    else:
        comparative_prompt = f"""You have evaluated {len(evaluations)} different models on the following criteria:

{judge_prompt}

Here are the individual evaluations:

{''.join(eval_summaries)}

Please provide a comparative analysis:
1. Rank the models from best to worst
2. Highlight key differences in performance
3. Identify any standout strengths or weaknesses
4. Provide an overall summary

If you provided scores in the individual evaluations, include a summary table."""

    # Invoke judge
    try:
        # Use appropriate parameters based on provider
        # Comparative judge needs much higher token limit for multiple models (16K for ~11 models)
        if judge_config['provider'] in ["openai", "grok"]:
            response = judge_provider.invoke(comparative_prompt, max_tokens=16384, reasoning_effort=judge_config.get('reasoning_effort', 'medium'))
        elif judge_config['provider'] == "gemini":
            response = judge_provider.invoke(comparative_prompt, max_tokens=16384, thinking_level=judge_config.get('reasoning_effort', 'medium'))
        else:
            response = judge_provider.invoke(comparative_prompt, max_tokens=16384, extended_thinking=judge_config.get('extended_thinking', False))

        # Extract JSON if present
        extracted_json = extract_json_from_text(response.response_text)

        return {
            'raw_summary': response.response_text,
            'extracted_json': extracted_json,
            'input_tokens': response.input_tokens or 0,
            'output_tokens': response.output_tokens or 0,
            'thinking': response.thinking if hasattr(response, 'thinking') else None
        }

    except Exception as e:
        return {
            'raw_summary': None,
            'extracted_json': None,
            'error': str(e),
            'input_tokens': 0,
            'output_tokens': 0
        }


def parse_judge_models(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse judge model(s) from config using same pattern as agent/batch jobs."""
    models = []

    if 'models' in config:
        # Direct model list in config
        for model_entry in config['models']:
            model_config = parse_model_config(model_entry)
            models.append({
                "provider": model_config.get("provider", "bedrock"),
                "model_id": model_config["model_id"],
                "display_name": model_config.get("display_name") or model_config["model_id"],
                "extended_thinking": model_config["extended_thinking"],
                "reasoning_effort": model_config.get("reasoning_effort", "medium")
            })

    elif 'model_list' in config:
        # Reference to model list file
        list_path = Path(config['model_list'])
        models = parse_model_list(list_path)

    # Default to Claude 4.5 Sonnet if no models specified
    if not models:
        models = [{
            "provider": "bedrock",
            "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            "display_name": "Claude-4.5-Sonnet",
            "extended_thinking": False,
            "reasoning_effort": "medium"
        }]

    return models


def parse_comparative_judge(config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse separate comparative judge configuration for Pass 2.

    Supports both inline config and external file reference:
    - Inline: comparative_judge: {models: [...], prompt: "...", reveal_names: true}
    - External: comparative_judge: "payload/judge_configs/comparative.yaml"

    Returns:
        Dict with 'judge_config' and optional 'prompt', or None if not specified
    """
    if 'comparative_judge' not in config:
        return None

    comp_config_raw = config['comparative_judge']

    # Check if it's a file path (string) or inline config (dict)
    if isinstance(comp_config_raw, str):
        # Load from external file
        comp_config_path = Path(comp_config_raw)
        if not comp_config_path.exists():
            print(f"Warning: Comparative judge config file not found: {comp_config_raw}", file=sys.stderr)
            return None

        print(f"Loading comparative judge config from: {comp_config_raw}")
        with open(comp_config_path, 'r') as f:
            comp_config = yaml.safe_load(f)
    else:
        # Use inline config
        comp_config = comp_config_raw

    # Parse model configuration
    judge_models = parse_judge_models(comp_config)

    # Extract prompt if provided
    comparative_prompt = comp_config.get('prompt')

    # Extract reveal_names option (default True)
    reveal_names = comp_config.get('reveal_names', True)

    return {
        'judge_config': judge_models[0],  # Use first model
        'prompt': comparative_prompt,
        'reveal_names': reveal_names
    }


def run_judge_evaluation(
    source_job_path: str,
    judge_id: str,
    judge_prompt: str,
    judge_models: List[Dict[str, Any]],
    jq_filter: Optional[str] = None,
    append_to_source: bool = False,
    comparative_judge_config: Optional[Dict[str, Any]] = None,
    anonymize_pass1: bool = True,
    retry_config: Optional[Dict[str, Any]] = None,
    post_processing: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Run complete two-pass judge evaluation.

    Args:
        source_job_path: Path to job file to evaluate
        judge_id: Unique identifier for this evaluation
        judge_prompt: Evaluation criteria/prompt
        judge_models: List of judge model configs for Pass 1
        jq_filter: Optional jq filter to apply to model data
        append_to_source: If True, append to source file instead of creating new
        comparative_judge_config: Optional separate judge config for Pass 2
        anonymize_pass1: If True, hide model names in Pass 1 (default True)
        retry_config: Optional retry configuration (inherits from job config)
        post_processing: Optional list of post-processors to apply (e.g., ['dimension_averages'])

    Returns:
        Complete evaluation results
    """
    # Load source job
    source_path = Path(source_job_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Source job not found: {source_job_path}")

    with open(source_path, 'r') as f:
        job_data = json.load(f)

    # Extract source job ID from metadata or filename
    job_metadata = job_data.get('job_metadata', {})
    source_job_id = job_metadata.get('request_id') or job_metadata.get('job_id') or source_path.stem

    print(f"Loading source job: {source_job_id}")

    # Extract model data
    print(f"Extracting model data with filter: {jq_filter or 'auto-detect'}")
    model_data_list = extract_model_data(job_data, jq_filter)
    print(f"Found {len(model_data_list)} models to evaluate")

    # Use ALL judge models from list for Pass 1
    num_pass1_judges = len(judge_models)
    print(f"Using {num_pass1_judges} judge(s) for Pass 1:")
    for j, jc in enumerate(judge_models, 1):
        print(f"  Judge {j}: {jc['display_name']}")

    # Pass 1: Evaluate each model with ALL judges
    print("\n=== PASS 1: Individual Evaluations ===")
    if anonymize_pass1:
        print("(Models will be anonymized as Model A, Model B, etc.)")
    evaluations = []

    # Generate labels for models
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    for i, model_data in enumerate(model_data_list, 1):
        # Generate anonymized label
        if anonymize_pass1:
            # Use letters A, B, C... or A, B, C, ..., AA, AB if more than 26
            if i <= 26:
                model_label = f"Model {alphabet[i-1]}"
            else:
                first_letter = alphabet[(i-27) // 26]
                second_letter = alphabet[(i-27) % 26]
                model_label = f"Model {first_letter}{second_letter}"
        else:
            model_label = model_data['display_name']

        print(f"[Model {i}/{len(model_data_list)}] {model_data['display_name']}:")

        # Evaluate with each Pass 1 judge
        model_evaluation = {
            'model_id': model_data['model_id'],
            'display_name': model_data['display_name'],
            'pass1_judges': []
        }

        for j, judge_config in enumerate(judge_models, 1):
            print(f"  Judge {j}/{num_pass1_judges} ({judge_config['display_name']})...", end=' ')

            # Create judge provider with retry config
            judge_provider = create_provider(
                provider_type=judge_config['provider'],
                model_id=judge_config['model_id'],
                display_name=judge_config['display_name'],
                retry_config=retry_config
            )

            evaluation = evaluate_model(judge_provider, judge_config, model_data, judge_prompt, model_label)

            # Add judge info to evaluation
            evaluation['judge_number'] = j
            evaluation['judge_model'] = judge_config['model_id']
            evaluation['judge_display_name'] = judge_config['display_name']

            model_evaluation['pass1_judges'].append(evaluation)

            if evaluation.get('error'):
                print(f"✗ Error: {evaluation['error']}")
            else:
                print(f"✓ ({evaluation['output_tokens']} tokens)")

        evaluations.append(model_evaluation)

    # Pass 2: Comparative analysis (only if comparative_judge is configured)
    comparison = None
    if comparative_judge_config:
        print("\n=== PASS 2: Comparative Analysis ===")

        comp_judge_config = comparative_judge_config['judge_config']
        comp_judge_prompt = comparative_judge_config.get('prompt')
        reveal_names = comparative_judge_config.get('reveal_names', True)

        print(f"Using comparative judge: {comp_judge_config['display_name']}")

        # Create separate provider for comparative judge with retry config
        comp_judge_provider = create_provider(
            provider_type=comp_judge_config['provider'],
            model_id=comp_judge_config['model_id'],
            display_name=comp_judge_config['display_name'],
            retry_config=retry_config
        )

        comparison = comparative_analysis(
            comp_judge_provider,
            comp_judge_config,
            evaluations,
            judge_prompt,
            comp_judge_prompt,
            reveal_names
        )

        if comparison.get('error'):
            print(f"  ✗ Error: {comparison['error']}")
        else:
            print(f"  ✓ Complete ({comparison['output_tokens']} tokens)")
    else:
        print("\n=== PASS 2: Skipped (comparative_judge not configured) ===")

    # Apply post-processing if configured
    if post_processing:
        print(f"\n=== Post-Processing: {', '.join(post_processing)} ===")
        evaluations = post_process_results(evaluations, comparison, post_processing)
        print("✓ Post-processing complete")

    # Build result
    result = {
        'judge_metadata': {
            'judge_id': judge_id,
            'source_job': str(source_path),
            'source_job_id': source_job_id,
            'num_pass1_judges': num_pass1_judges,
            'pass1_judges': [
                {
                    'model': jc['model_id'],
                    'display_name': jc['display_name'],
                    'provider': jc['provider']
                }
                for jc in judge_models
            ],
            'anonymize_pass1': anonymize_pass1,
            'timestamp': datetime.now().isoformat(),
            'total_models_evaluated': len(evaluations),
            'judge_prompt': judge_prompt,
            'jq_filter': jq_filter,
            'post_processing': post_processing or []
        },
        'evaluations': evaluations,
        'comparative_analysis': comparison
    }

    # Add comparative judge info if used
    if comparative_judge_config:
        comp_judge_config = comparative_judge_config['judge_config']
        result['judge_metadata']['comparative_judge'] = {
            'model': comp_judge_config['model_id'],
            'display_name': comp_judge_config['display_name'],
            'provider': comp_judge_config['provider'],
            'reveal_names': comparative_judge_config.get('reveal_names', True)
        }
        if comparative_judge_config.get('prompt'):
            result['judge_metadata']['comparative_judge']['custom_prompt'] = True

    # Calculate totals (account for multiple Pass 1 judges)
    total_input_tokens = 0
    total_output_tokens = 0
    for model_eval in evaluations:
        for judge_eval in model_eval['pass1_judges']:
            total_input_tokens += judge_eval.get('input_tokens', 0)
            total_output_tokens += judge_eval.get('output_tokens', 0)

    if comparison:
        total_input_tokens += comparison.get('input_tokens', 0)
        total_output_tokens += comparison.get('output_tokens', 0)

    result['judge_metadata']['total_input_tokens'] = total_input_tokens
    result['judge_metadata']['total_output_tokens'] = total_output_tokens

    print(f"\n=== Evaluation Complete ===")
    print(f"Total tokens: {total_input_tokens} input, {total_output_tokens} output")

    # Save result
    if append_to_source:
        # Append to source file
        job_data['judge_evaluation'] = result
        with open(source_path, 'w') as f:
            json.dump(job_data, f, indent=2)
        print(f"\nAppended evaluation to source file: {source_path}")

        # Re-export chat file if it exists (to include judge section)
        try:
            from export_utils import export_batch_job_chat

            # Determine job type
            job_type = detect_job_type(job_data)

            if job_type == 'batch':
                # Re-export batch job chat with judge section
                # Batch jobs use 'payload_name' instead of 'job_id'
                job_id = job_data['job_metadata'].get('payload_name') or job_data['job_metadata'].get('job_id', source_job_id)
                timestamp_str = job_data['job_metadata'].get('timestamp', '')
                if 'T' in timestamp_str:
                    timestamp_str = timestamp_str.replace('T', '_').replace(':', '').replace('-', '').split('.')[0]

                chat_path = export_batch_job_chat(job_data, job_id, timestamp_str, source_path.parent.parent)
                print(f"Updated chat export with judge evaluation: {chat_path.name}")

            elif job_type == 'agent':
                # For agent jobs, re-export chat with judge section
                from agent_invoke import save_chat_export

                # Extract metadata from job
                request_id = job_data['job_metadata'].get('request_id', source_job_id)
                timestamp_str = job_data['job_metadata'].get('timestamp', '')

                # Convert ISO timestamp to filename format (YYYYMMDD_HHMMSS)
                if 'T' in timestamp_str:
                    timestamp_str = timestamp_str.replace('T', '_').replace(':', '').replace('-', '').split('.')[0]

                # Determine chat style from analytics config (default: chatbot)
                chat_style = 'chatbot'  # Default

                # Re-export with judge evaluation included
                output_dir = source_path.parent.parent
                chat_path = save_chat_export(job_data, request_id, timestamp_str, output_dir, chat_style=chat_style)
                print(f"Updated chat export with judge evaluation: {chat_path.name}")

        except Exception as e:
            # Don't fail the entire operation if export fails
            print(f"Note: Could not update chat export: {e}")

        # Generate visualizations if behavioral dimensions present
        try:
            if post_processing and 'dimension_averages' in post_processing:
                from visualize_behavioral import visualize_judge_results

                print(f"\n{'='*80}")
                print(f"GENERATING VISUALIZATIONS")
                print(f"{'='*80}")

                viz_files = visualize_judge_results(source_path, output_dir=source_path.parent / 'visualizations')
                print(f"\n✓ Created {len(viz_files)} visualizations")
        except Exception as e:
            print(f"Note: Could not generate visualizations: {e}")

        return result
    else:
        # Create separate judge file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path('outputs/judge_results')
        output_dir.mkdir(parents=True, exist_ok=True)

        output_filename = f"judge_{judge_id}_{source_job_id}_{timestamp}.json"
        output_path = output_dir / output_filename

        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\nSaved evaluation to: {output_path}")

        # Export as markdown
        try:
            from export_utils import export_judge_results_chat
            md_path = export_judge_results_chat(result, output_path)
            print(f"Exported readable format: {md_path.name}")
        except Exception as e:
            print(f"Note: Could not create markdown export: {e}")

        return result


def load_yaml_config(yaml_path: str) -> Dict[str, Any]:
    """Load judge job configuration from YAML."""
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    # Validate required fields (source_job is now optional, can be provided as CLI arg)
    required = ['judge_id', 'judge_prompt']
    missing = [field for field in required if field not in config]
    if missing:
        raise ValueError(f"Missing required fields in YAML: {', '.join(missing)}")

    return config


def main():
    parser = argparse.ArgumentParser(
        description='LLM-as-Judge evaluation system with two-pass analysis'
    )

    parser.add_argument(
        'input',
        help='YAML config file OR source job file (for CLI mode)'
    )

    parser.add_argument(
        'source_job',
        nargs='?',
        help='Optional: Source job file (overrides source_job in YAML config)'
    )

    # CLI mode arguments
    parser.add_argument(
        '--prompt',
        type=str,
        help='Evaluation prompt (required for CLI mode)'
    )
    parser.add_argument(
        '--judge-id',
        type=str,
        help='Judge ID (required for CLI mode)'
    )
    parser.add_argument(
        '--judge',
        type=str,
        default=DEFAULT_JUDGE_MODEL,
        help=f'Judge model (default: {DEFAULT_JUDGE_MODEL})'
    )
    parser.add_argument(
        '--jq-filter',
        type=str,
        help='JQ filter to apply to model data (default: auto-detect)'
    )
    parser.add_argument(
        '--append',
        action='store_true',
        help='Append evaluation to source file instead of creating new file'
    )

    args = parser.parse_args()

    # Determine mode: YAML or CLI
    input_path = Path(args.input)

    if input_path.suffix in ['.yaml', '.yml']:
        # YAML mode
        print("Loading YAML configuration...")
        config = load_yaml_config(args.input)

        # Determine source job: CLI argument overrides YAML config
        if args.source_job:
            source_job_path = args.source_job
            print(f"Using source job from CLI argument: {source_job_path}")
        elif 'source_job' in config:
            source_job_path = config['source_job']
            print(f"Using source job from YAML config: {source_job_path}")
        else:
            print("Error: source_job not specified in YAML config or CLI argument", file=sys.stderr)
            sys.exit(1)

        # Parse judge models
        judge_models = parse_judge_models(config)

        # Parse comparative judge (optional)
        comparative_judge_config = parse_comparative_judge(config)

        # Get anonymize option (default True)
        anonymize_pass1 = config.get('anonymize_pass1', True)

        # Get post-processing options (default empty list)
        post_processing = config.get('post_processing', [])

        # CLI --append flag overrides YAML config
        append_to_source = args.append if args.append else config.get('append_to_source', False)

        # Run evaluation
        run_judge_evaluation(
            source_job_path=source_job_path,
            judge_id=config['judge_id'],
            judge_prompt=config['judge_prompt'],
            judge_models=judge_models,
            jq_filter=config.get('jq_filter'),
            append_to_source=append_to_source,
            comparative_judge_config=comparative_judge_config,
            anonymize_pass1=anonymize_pass1,
            post_processing=post_processing
        )

    else:
        # CLI mode
        if not args.prompt:
            print("Error: --prompt required for CLI mode", file=sys.stderr)
            sys.exit(1)
        if not args.judge_id:
            print("Error: --judge-id required for CLI mode", file=sys.stderr)
            sys.exit(1)

        # Parse CLI judge model
        cli_config = {'models': [args.judge]} if args.judge else {}
        judge_models = parse_judge_models(cli_config)

        # Run evaluation
        run_judge_evaluation(
            source_job_path=args.input,
            judge_id=args.judge_id,
            judge_prompt=args.prompt,
            judge_models=judge_models,
            jq_filter=args.jq_filter,
            append_to_source=args.append
        )


if __name__ == '__main__':
    main()
