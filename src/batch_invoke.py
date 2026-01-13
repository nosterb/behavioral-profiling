#!/usr/bin/env python3
"""
Batch job script to invoke multiple models with the same payload.
Outputs a single consolidated JSON file per job containing all model results.

Can be invoked with:
1. YAML config file: python batch_invoke.py payload/single_prompt_jobs/config.yaml
2. Legacy mode: python batch_invoke.py payload_file.txt model_list

Output location: outputs/single_prompt_jobs/job_<payload>_<timestamp>.json
Individual text files can be enabled via SAVE_INDIVIDUAL_FILES flag.
"""

import sys
import json
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from model_providers import create_provider, ModelResponse, parse_model_config, EXTENDED_THINKING_MODELS

# Configuration - paths relative to project root (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent
PAYLOAD_DIR = PROJECT_ROOT / "payload"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "single_prompt_jobs"
MODEL_CONFIG_DIR = PROJECT_ROOT / "model_config"
DEFAULT_MODEL_LIST = "main"
REGION = "us-east-1"
SAVE_INDIVIDUAL_FILES = False  # Set to True to save individual .txt files per model


def load_batch_config(config_path: Path) -> Dict[str, Any]:
    """Load batch job configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_additional_prompt(prompt_file: Optional[str]) -> str:
    """Load optional additional prompt from file."""
    if not prompt_file:
        return ""

    prompt_path = Path(prompt_file)

    if not prompt_path.exists():
        raise ValueError(f"Prompt file not found: {prompt_file}")

    with open(prompt_path, 'r') as f:
        return f.read().strip()


def parse_models_from_config(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse model list from batch job config with extended thinking support.

    Returns:
        List of dicts with keys: provider, model_id, display_name, extended_thinking
    """
    models = []

    if 'models' in config:
        # Direct model list in config - can be strings or objects
        for model_entry in config['models']:
            model_config = parse_model_config(model_entry)
            model_id = model_config["model_id"]
            extended_thinking = model_config["extended_thinking"]
            display_name = model_config["display_name"]

            # Auto-generate display name if not provided
            if not display_name:
                display_name = model_id.split('.')[-1] if '.' in model_id else model_id

            models.append({
                "provider": "bedrock",
                "model_id": model_id,
                "display_name": display_name,
                "extended_thinking": extended_thinking
            })

    elif 'model_list' in config:
        # Reference to model list file (supports extended_thinking via |extended_thinking=true)
        list_path = Path(config['model_list'])
        models = parse_model_list(list_path)

    return models


def parse_model_list(list_path: Path) -> List[Dict[str, Any]]:
    """
    Parse model list file and return models marked with *.

    Format: *provider:model_id:display_name|extended_thinking=true

    Returns list of dicts with keys: provider, model_id, display_name, extended_thinking
    """
    models = []

    if not list_path.exists():
        print(f"Error: Model list not found: {list_path}")
        return models

    with open(list_path, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Check if model is marked for execution
            is_selected = line.startswith('*')
            if is_selected:
                line = line[1:]  # Remove the *
            else:
                continue  # Skip unselected models

            # Parse format: provider:model_id:display_name|extended_thinking=true
            # Note: model_id may contain colons (e.g., v1:0)
            # Strategy: provider is before first colon, display_name is after last colon,
            # everything in between is model_id
            first_colon = line.find(':')
            last_colon = line.rfind(':')

            if first_colon > 0 and last_colon > first_colon:
                provider = line[:first_colon].strip()
                display_name_part = line[last_colon+1:].strip()
                model_id = line[first_colon+1:last_colon].strip()

                # Parse options after pipe (e.g., |extended_thinking=true,reasoning_effort=high)
                extended_thinking = False
                reasoning_effort = "medium"  # Default reasoning effort
                if '|' in display_name_part:
                    parts = display_name_part.split('|', 1)
                    display_name = parts[0].strip()
                    options_str = parts[1].strip()

                    # Parse key=value pairs
                    for option in options_str.split(','):
                        option = option.strip()
                        if '=' in option:
                            key, value = option.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if key == 'extended_thinking':
                                extended_thinking = value.lower() == 'true'
                            elif key == 'reasoning_effort':
                                reasoning_effort = value  # low, medium, high
                else:
                    display_name = display_name_part

                # Auto-append " (Thinking)" to display name if extended thinking enabled
                if extended_thinking:
                    display_name = f"{display_name} (Thinking)"

                models.append({
                    "provider": provider,
                    "model_id": model_id,
                    "display_name": display_name,
                    "extended_thinking": extended_thinking,
                    "reasoning_effort": reasoning_effort
                })

    return models


def invoke_model(provider_type: str, model_id: str, display_name: str, prompt: str,
                 extended_thinking: bool = False, reasoning_effort: str = "medium") -> Dict[str, Any]:
    """
    Invoke a single model and return result metadata.

    Args:
        provider_type: Provider type (e.g., "bedrock", "openai", "grok", "gemini")
        model_id: Model identifier
        display_name: Display name for the model
        prompt: The prompt to send
        extended_thinking: Enable extended thinking (Claude 4+ only)
        reasoning_effort: Reasoning effort/thinking level (low/medium/high)
                         - OpenAI: Supports low/medium/high for reasoning models
                         - Grok 3: Supports low/high only ("medium" auto-maps to "high")
                         - Grok 4: Always reasoning, ignores this parameter
                         - Gemini: Supports low/medium/high as thinking_level
    """
    timestamp = datetime.now().isoformat()

    try:
        provider = create_provider(provider_type, model_id, display_name)

        # Use appropriate parameters based on provider
        if provider_type == "openai":
            response = provider.invoke(prompt, reasoning_effort=reasoning_effort)
        elif provider_type == "grok":
            response = provider.invoke(prompt, reasoning_effort=reasoning_effort)
        elif provider_type == "gemini":
            response = provider.invoke(prompt, thinking_level=reasoning_effort)
        else:
            response = provider.invoke(prompt, extended_thinking=extended_thinking)

        return {
            "model_id": model_id,
            "display_name": display_name,
            "provider": provider_type,
            "extended_thinking_enabled": extended_thinking,
            "reasoning_effort": reasoning_effort if provider_type in ["openai", "grok", "gemini"] else None,
            "success": response.success,
            "timestamp": timestamp,
            "region": REGION if provider_type == "bedrock" else None,
            "response": response.response_text,
            "thinking": response.thinking,
            "stop_reason": response.stop_reason,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.cost_usd,
            "error": response.error
        }

    except Exception as e:
        return {
            "model_id": model_id,
            "display_name": display_name,
            "provider": provider_type,
            "extended_thinking_enabled": extended_thinking,
            "reasoning_effort": reasoning_effort if provider_type in ["openai", "grok", "gemini"] else None,
            "success": False,
            "timestamp": timestamp,
            "region": REGION if provider_type == "bedrock" else None,
            "response": "",
            "thinking": None,
            "stop_reason": None,
            "input_tokens": None,
            "output_tokens": None,
            "cost_usd": None,
            "error": str(e)
        }


def save_individual_output(payload_name: str, model_result: Dict[str, Any], prompt: str) -> Path:
    """Save individual model output as text file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_id = model_result["model_id"]
    output_filename = f"{payload_name}_{timestamp}_{model_id}.txt"
    output_path = OUTPUT_DIR / output_filename

    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(f"PROMPT:\n{prompt}\n\n")
        f.write(f"{'='*80}\n\n")
        f.write(f"MODEL: {model_id}\n")
        f.write(f"DISPLAY NAME: {model_result['display_name']}\n")
        f.write(f"PROVIDER: {model_result['provider']}\n")
        f.write(f"TIMESTAMP: {model_result['timestamp']}\n")

        if model_result['region']:
            f.write(f"REGION: {model_result['region']}\n")

        f.write(f"SUCCESS: {model_result['success']}\n\n")
        f.write(f"{'='*80}\n\n")

        if model_result['success']:
            f.write(f"RESPONSE:\n{model_result['response']}\n\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"METADATA:\n")
            f.write(f"Stop reason: {model_result['stop_reason']}\n")
            f.write(f"Input tokens: {model_result['input_tokens']}\n")
            f.write(f"Output tokens: {model_result['output_tokens']}\n")
        else:
            f.write(f"ERROR:\n{model_result['error']}\n")

    return output_path


def save_job_output(payload_name: str, prompt: str, model_results: List[Dict[str, Any]], config: Dict[str, Any] = None) -> Path:
    """Save consolidated job output as JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_filename = f"job_{payload_name}_{timestamp}.json"

    # Determine output location based on metadata (if present)
    output_dir = OUTPUT_DIR
    if config and 'metadata' in config:
        metadata = config['metadata']
        if metadata.get('suite') and metadata.get('intervention'):
            # Organize by intervention_suite subdirectory
            intervention = metadata['intervention']
            suite = metadata['suite']
            output_dir = OUTPUT_DIR / f"{intervention}_{suite}"

    # Create job subdirectory
    job_dir = output_dir / f"job_{payload_name}_{timestamp}"
    job_dir.mkdir(parents=True, exist_ok=True)
    job_path = job_dir / job_filename

    # Calculate summary statistics
    total_models = len(model_results)
    successful = sum(1 for r in model_results if r['success'])
    failed = total_models - successful

    job_data = {
        "job_metadata": {
            "payload_name": payload_name,
            "timestamp": datetime.now().isoformat(),
            "total_models": total_models,
            "successful": successful,
            "failed": failed
        },
        "prompt": prompt,
        "models": model_results
    }

    with open(job_path, 'w') as f:
        json.dump(job_data, f, indent=2, ensure_ascii=False)

    return job_path


def print_summary(model_results: List[Dict[str, Any]]):
    """Print execution summary to console."""
    print(f"\n{'='*80}")
    print("BATCH JOB SUMMARY")
    print(f"{'='*80}\n")

    successful = [r for r in model_results if r['success']]
    failed = [r for r in model_results if not r['success']]

    print(f"Total models: {len(model_results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}\n")

    if successful:
        print("✓ Successful models:")
        for result in successful:
            tokens = f" ({result['input_tokens']}→{result['output_tokens']} tokens)" if result['input_tokens'] else ""
            cost = f" [${result['cost_usd']:.6f}]" if result.get('cost_usd') is not None else ""
            print(f"  - {result['display_name']}{tokens}{cost}")

    if failed:
        print("\n✗ Failed models:")
        for result in failed:
            print(f"  - {result['display_name']}: {result['error']}")

    print(f"\n{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Batch job script to invoke multiple models with the same payload',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # YAML config mode
  python batch_invoke.py payload/single_prompt_jobs/config.yaml
  python batch_invoke.py payload/single_prompt_jobs/config.yaml --output-dir outputs/custom_folder

  # Legacy mode
  python batch_invoke.py payload.txt model_list
        """
    )

    parser.add_argument('config', help='YAML config file or payload text file')
    parser.add_argument('model_list', nargs='?', help='Model list name (legacy mode only)')
    parser.add_argument('--output-dir', '-o', type=str,
                        help='Custom output directory (default: outputs/single_prompt_jobs)')
    parser.add_argument('--models', type=str,
                        help='Override model list from config file')
    parser.add_argument('--non-interactive', action='store_true',
                        help='Skip interactive prompts (for parallel execution)')

    args = parser.parse_args()

    # Set OUTPUT_DIR globally if specified
    global OUTPUT_DIR
    if args.output_dir:
        OUTPUT_DIR = Path(args.output_dir)
        print(f"Using custom output directory: {OUTPUT_DIR}")

    first_arg = Path(args.config)

    # Initialize config (will be None for legacy mode)
    config = None

    # Detect mode: YAML config or legacy text file
    if first_arg.suffix in ['.yaml', '.yml']:
        # YAML config mode
        config_path = first_arg

        if not config_path.exists():
            print(f"Error: Config file not found: {config_path}")
            sys.exit(1)

        print(f"Loading batch job config: {config_path}")
        config = load_batch_config(config_path)

        # Load prompt and optional additional prompt
        additional_prompt = load_additional_prompt(config.get('prompt_file'))
        base_prompt = config['prompt'].strip()

        # Combine prompts
        if additional_prompt:
            prompt = f"{additional_prompt}\n\n{base_prompt}"
        else:
            prompt = base_prompt

        # Parse models - allow command-line override
        if args.models:
            # Override with command-line model list
            model_list_path = Path(args.models)
            models = parse_model_list(model_list_path)
            print(f"Using model list from command line: {args.models}")
        else:
            models = parse_models_from_config(config)

        if not models:
            print("Error: No models specified in config")
            sys.exit(1)

        # Support both job_id (preferred) and request_id (fallback) for backwards compatibility
        job_id = config.get('job_id') or config.get('request_id', 'batch')
        print(f"Job ID: {job_id}")

    else:
        # Legacy mode: text file + model list
        payload_filename = args.config
        model_list_name = args.model_list if args.model_list else DEFAULT_MODEL_LIST

        payload_path = PAYLOAD_DIR / payload_filename
        model_list_path = MODEL_CONFIG_DIR / model_list_name

        # Validate inputs
        if not payload_path.exists():
            print(f"Error: Payload file not found: {payload_path}")
            sys.exit(1)

        if not model_list_path.exists():
            print(f"Error: Model list not found: {model_list_path}")
            sys.exit(1)

        # Read payload
        print(f"Reading payload from: {payload_path}")
        with open(payload_path, 'r') as f:
            prompt = f.read().strip()

        # Parse model list (supports extended_thinking via |extended_thinking=true)
        print(f"Loading model list: {model_list_path}")
        models = parse_model_list(model_list_path)

        if not models:
            print(f"No models marked with * in {model_list_name}")
            print("Edit the model list file and add * to the beginning of lines you want to execute")
            sys.exit(1)

        job_id = payload_path.stem

    print(f"Prompt length: {len(prompt)} characters")
    print(f"Found {len(models)} models marked for execution:\n")
    for model in models:
        print(f"  - {model['display_name']} ({model['provider']})")

    print(f"\n{'='*80}")
    print("STARTING BATCH JOB")
    print(f"{'='*80}\n")

    # Execute batch job
    model_results = []
    payload_name = job_id

    for i, model_config in enumerate(models, 1):
        provider = model_config["provider"]
        model_id = model_config["model_id"]
        display_name = model_config["display_name"]
        extended_thinking = model_config.get("extended_thinking", False)
        reasoning_effort = model_config.get("reasoning_effort", "medium")

        # Warn if extended thinking requested but not supported
        if extended_thinking and model_id not in EXTENDED_THINKING_MODELS:
            print(f"[{i}/{len(models)}] {display_name}...")
            print(f"  ⚠ Warning: {display_name} does not support extended thinking, ignoring flag")
            extended_thinking = False
        else:
            print(f"[{i}/{len(models)}] Invoking {display_name}...")

        result = invoke_model(provider, model_id, display_name, prompt, extended_thinking, reasoning_effort)
        model_results.append(result)

        if result['success']:
            tokens_str = f"({result['output_tokens']} tokens)"
            # Show cost if available
            if result.get('cost_usd') is not None:
                tokens_str += f" [${result['cost_usd']:.6f}]"
            print(f"  ✓ Success {tokens_str}")
            # Optionally save individual output file
            if SAVE_INDIVIDUAL_FILES:
                output_path = save_individual_output(payload_name, result, prompt)
                print(f"  → {output_path.name}")
        else:
            print(f"  ✗ Failed: {result['error']}")

        print()

    # Save consolidated job output
    print(f"Saving job results...")
    job_path = save_job_output(payload_name, prompt, model_results, config)
    print(f"  JSON Report → {job_path}")

    # Export chat if configured (YAML mode only)
    chat_path = None
    if first_arg.suffix in ['.yaml', '.yml'] and config.get('export_chat', False):
        from export_utils import export_batch_job_chat

        # Load the saved job data to include any metadata
        with open(job_path, 'r') as f:
            job_data = json.load(f)

        # Extract timestamp from job metadata or filename
        timestamp = job_data['job_metadata'].get('timestamp', datetime.now().strftime('%Y%m%d_%H%M%S'))
        # Convert ISO format to filename format if needed
        if 'T' in timestamp:
            timestamp = timestamp.replace('T', '_').replace(':', '').replace('-', '').split('.')[0]

        # Save chat to the job directory (parent of job_path)
        job_dir = job_path.parent
        chat_path = export_batch_job_chat(job_data, job_id, timestamp, job_dir)
        print(f"  Chat Export → {chat_path}")

    # Run judge evaluation if configured (YAML mode only)
    if first_arg.suffix in ['.yaml', '.yml'] and 'judge' in config:
        # Import here to avoid circular import
        from judge_invoke import run_judge_evaluation, parse_judge_models, parse_comparative_judge

        print(f"\n{'='*80}")
        print(f"RUNNING JUDGE EVALUATION")
        print(f"{'='*80}\n")

        # Load judge config from file if it's a string path, otherwise use inline dict
        judge_config_raw = config['judge']
        judge_config = None

        if isinstance(judge_config_raw, str):
            # Load from external file
            judge_config_path = Path(judge_config_raw)
            if not judge_config_path.exists():
                print(f"✗ Judge config file not found: {judge_config_raw}")
                print(f"Skipping judge evaluation...\n")
            else:
                print(f"Loading judge config from: {judge_config_raw}")
                with open(judge_config_path, 'r') as f:
                    judge_config = yaml.safe_load(f)
        else:
            # Use inline config
            judge_config = judge_config_raw

        # Only proceed if config was successfully loaded
        if judge_config:
            # Parse judge models
            judge_models = parse_judge_models(judge_config)

            # Parse comparative judge (optional)
            comparative_judge_config = parse_comparative_judge(judge_config)

            # Get judge configuration options
            judge_id = judge_config.get('judge_id', f"{job_id}_judge")
            judge_prompt = judge_config['judge_prompt']
            jq_filter = judge_config.get('jq_filter')
            append_to_source = judge_config.get('append_to_source', True)  # Default to True for chained jobs
            anonymize_pass1 = judge_config.get('anonymize_pass1', True)
            post_processing = judge_config.get('post_processing', [])

            # Get retry config from main job config (if available)
            retry_config = config.get('retry_config')

            try:
                # Run judge evaluation with retry config
                run_judge_evaluation(
                    source_job_path=str(job_path),
                    judge_id=judge_id,
                    judge_prompt=judge_prompt,
                    judge_models=judge_models,
                    jq_filter=jq_filter,
                    append_to_source=append_to_source,
                    comparative_judge_config=comparative_judge_config,
                    anonymize_pass1=anonymize_pass1,
                    retry_config=retry_config,
                    post_processing=post_processing
                )

                print(f"\n{'='*80}")
                print(f"JUDGE EVALUATION COMPLETE")
                print(f"{'='*80}\n")

                # Auto-update behavioral profiles if enabled
                update_profiles = judge_config.get('update_behavioral_profiles', True)
                if update_profiles:
                    try:
                        from behavioral_profile_manager import BehavioralProfileManager

                        master_dir = judge_config.get('behavioral_profile_dir', 'outputs/behavioral_profiles')
                        manager = BehavioralProfileManager(Path(master_dir))

                        job_id = config.get('job_id', job_path.stem)

                        print(f"{'='*80}")
                        print(f"UPDATING MASTER BEHAVIORAL PROFILES")
                        print(f"{'='*80}\n")

                        result = manager.add_job_evaluation(job_id, job_path, update_viz=True)

                        if result['status'] == 'success':
                            print(f"✓ Updated profiles for: {', '.join(result['models'])}")
                            print(f"  Master directory: {master_dir}")
                        elif result['status'] == 'skipped':
                            print(f"- {result['message']}")

                        print()

                    except Exception as e:
                        print(f"Warning: Failed to update behavioral profiles: {e}\n")

            except Exception as e:
                print(f"\n✗ Judge evaluation failed: {e}")
                print(f"Continuing with job completion...\n")

    # Print summary
    print_summary(model_results)

    print(f"Results saved to: {job_path}")

    # Post-job behavioral analysis prompt (if not already done via judge config)
    try:
        from behavioral_prompt_handler import (
            prompt_for_behavioral_analysis,
            run_behavioral_analysis,
            prompt_for_profile_update
        )

        # Check if we should prompt (interactive mode, no existing behavioral eval)
        interactive = not args.non_interactive
        chunking = prompt_for_behavioral_analysis(job_path, interactive=interactive)

        if chunking:
            # Run analysis and stage results
            staged_results_path = run_behavioral_analysis(
                job_path,
                chunking,
                framework_config=None,  # Use default
                staging_dir=None  # Use default
            )

            # Prompt to apply to master profiles
            prompt_for_profile_update(staged_results_path, interactive=interactive)

    except Exception as e:
        print(f"Warning: Behavioral analysis prompt failed: {e}\n")


if __name__ == "__main__":
    main()
