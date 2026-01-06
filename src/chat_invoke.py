#!/usr/bin/env python3
"""
Chat simulation orchestrator - manages natural conversation simulations.

Simulates chat conversations where:
1. LLM acts as assistant responding to user messages
2. Another LLM simulates user responses
3. Loop continues until either side signals completion (STOP)
4. Full conversation logged for analysis
"""

import yaml
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from model_providers import EXTENDED_THINKING_MODELS
from analytics import AnalyticsEngine, add_analytics_to_job
from chat_simulation import ChatSimulation
from judge_invoke import run_judge_evaluation, parse_judge_models, parse_comparative_judge


def load_config(config_path: str) -> Dict:
    """Load YAML configuration file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def parse_models(config: Dict) -> List[Dict]:
    """Parse model list from config.

    Supports:
    - Direct models list: ["provider:model_id:display_name|options", ...]
    - model_list file reference

    Returns list of model configs with: provider, model_id, display_name, extended_thinking, reasoning_effort
    """
    # Import here to avoid circular dependency
    from agent_invoke import parse_models as agent_parse_models
    return agent_parse_models(config)


def save_job_data(job_data: Dict, output_dir: Path, request_id: str) -> Path:
    """Save job data to JSON file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir.mkdir(parents=True, exist_ok=True)

    job_filename = f"chat_job_{request_id}_{timestamp}.json"
    job_path = output_dir / job_filename

    with open(job_path, 'w') as f:
        json.dump(job_data, f, indent=2, ensure_ascii=False)

    return job_path


def export_chat_if_enabled(config: Dict, job_data: Dict, job_path: Path) -> Optional[Path]:
    """Export chat to markdown if enabled in config."""
    analytics_config = config.get('analytics', {})

    if not analytics_config.get('export_chat', False):
        return None

    try:
        from agent_invoke import save_chat_export

        # Extract request_id and timestamp from job_path
        # Format: chat_job_{request_id}_{timestamp}.json
        filename = job_path.stem  # Remove .json
        parts = filename.split('_')
        timestamp = parts[-1] if len(parts) >= 2 else datetime.now().strftime('%Y%m%d_%H%M%S')
        request_id = '_'.join(parts[2:-1]) if len(parts) >= 3 else 'unknown'

        chat_style = analytics_config.get('chat_style', 'chatbot')
        output_dir = job_path.parent.parent  # Go from reports/ to outputs/chat_jobs/

        chat_path = save_chat_export(job_data, request_id, timestamp, output_dir, chat_style=chat_style)
        return chat_path
    except Exception as e:
        print(f"Warning: Chat export failed: {e}")
        return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Run chat simulation jobs')
    parser.add_argument('config_file', help='Path to chat job YAML config')
    parser.add_argument('--output-dir', '-o', help='Custom output directory')
    parser.add_argument('--models', help='Override model list file')

    args = parser.parse_args()

    # Load configuration
    print(f"\nLoading configuration: {args.config_file}")
    config = load_config(args.config_file)

    # Determine output directory
    if args.output_dir:
        base_output_dir = Path(args.output_dir)
    else:
        base_output_dir = Path("outputs/chat_jobs")

    reports_dir = base_output_dir / "reports"

    # Parse models
    if args.models:
        config['model_list'] = args.models

    model_configs = parse_models(config)

    if not model_configs:
        print("Error: No models configured")
        sys.exit(1)

    request_id = config.get('request_id', 'chat_001')
    user_request = config.get('user_request', '')
    max_turns = config.get('max_turns', 10)

    # Display job info
    print(f"\n{'='*80}")
    print(f"CHAT SIMULATION JOB")
    print(f"{'='*80}")
    print(f"Request ID: {request_id}")
    print(f"User Request: {user_request[:100]}{'...' if len(user_request) > 100 else ''}")
    print(f"Max Turns: {max_turns}")
    print(f"Models: {len(model_configs)}")
    for i, model_config in enumerate(model_configs, 1):
        print(f"  {i}. {model_config['display_name']}")
    print(f"{'='*80}\n")

    # Track timing
    job_start_time = datetime.now()

    # Run simulation for each model
    model_results = []
    successful_count = 0
    failed_count = 0

    for i, model_config in enumerate(model_configs, 1):
        model_id = model_config['model_id']
        display_name = model_config['display_name']
        provider = model_config.get('provider', 'bedrock')
        extended_thinking = model_config.get('extended_thinking', False)
        reasoning_effort = model_config.get('reasoning_effort', 'medium')

        print(f"[{i}/{len(model_configs)}] Running chat with {display_name}...")

        try:
            # Get retry config
            retry_config = config.get('retry_config', {
                "max_retries": 3,
                "initial_timeout": 120,
                "backoff_multiplier": 2.0,
                "max_timeout": 300
            })

            # Create and run simulation
            simulation = ChatSimulation(
                config, model_id, display_name, extended_thinking,
                retry_config, provider, reasoning_effort
            )

            result = simulation.run()

            # Print completion
            cost_str = ""
            if result.get('total_cost_usd'):
                cost_str = f" [Total: ${result['total_cost_usd']:.6f}]"

            print(f"  ✓ Completed in {result['total_turns']} turns ({result['completion_reason']}){cost_str}")

            model_results.append(result)
            successful_count += 1

        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")

            # Add error result
            model_results.append({
                'model_id': model_id,
                'display_name': display_name,
                'provider': provider,
                'success': False,
                'error': str(e),
                'total_turns': 0,
                'completion_reason': 'ERROR',
                'conversation_log': []
            })
            failed_count += 1

    # Create job data structure
    job_end_time = datetime.now()
    job_duration = (job_end_time - job_start_time).total_seconds()
    timestamp = job_start_time.strftime('%Y%m%d_%H%M%S')

    job_data = {
        'job_metadata': {
            'request_id': request_id,
            'simulation_type': 'chat',
            'timestamp': job_start_time.isoformat(),
            'total_models': len(model_configs),
            'successful': successful_count,
            'failed': failed_count,
            'max_turns': max_turns,
            'duration_seconds': job_duration
        },
        'user_request': user_request,
        'models': model_results
    }

    # Add analytics if enabled
    analytics_config = config.get('analytics', {})
    if analytics_config.get('enabled', True):
        print(f"\nRunning analytics...")
        add_analytics_to_job(job_data, analytics_config)

    # Save job data
    print(f"\nSaving job results...")
    job_path = save_job_data(job_data, reports_dir, request_id)
    saved_job_data = job_data

    # Export text summary if enabled
    text_summary_path = None
    if analytics_config.get('save_text_summary', False):
        try:
            from agent_invoke import save_text_summary
            text_summary_path = save_text_summary(job_data, request_id, timestamp, base_output_dir, analytics_config)
            print(f"  Text summary: {text_summary_path}")
        except Exception as e:
            print(f"  Warning: Text summary export failed: {e}")

    # Export chat if enabled
    chat_path = export_chat_if_enabled(config, job_data, job_path)
    if chat_path:
        print(f"  Chat export: {chat_path}")

    # Run judge evaluation if configured (chained judge)
    if 'judge' in config:
        print(f"\n{'='*80}")
        print(f"RUNNING JUDGE EVALUATION")
        print(f"{'='*80}\n")

        # Load judge config
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
            judge_id = judge_config.get('judge_id', f"{request_id}_judge")
            judge_prompt = judge_config['judge_prompt']
            jq_filter = judge_config.get('jq_filter')
            append_to_source = judge_config.get('append_to_source', True)
            anonymize_pass1 = judge_config.get('judge_anonymize_pass1', True)

            # Get retry config
            retry_config = config.get('retry_config')

            try:
                # Run judge evaluation
                run_judge_evaluation(
                    source_job_path=str(job_path),
                    judge_id=judge_id,
                    judge_prompt=judge_prompt,
                    judge_models=judge_models,
                    jq_filter=jq_filter,
                    append_to_source=append_to_source,
                    comparative_judge_config=comparative_judge_config,
                    anonymize_pass1=anonymize_pass1,
                    retry_config=retry_config
                )

                print(f"\n{'='*80}")
                print(f"JUDGE EVALUATION COMPLETE")
                print(f"{'='*80}\n")

                # Reload job data if appended
                if append_to_source:
                    with open(job_path, 'r') as f:
                        saved_job_data = json.load(f)

                    # Re-export chat with judge results
                    if chat_path:
                        print(f"Updating chat export with judge evaluation...")
                        chat_path = export_chat_if_enabled(config, saved_job_data, job_path)

            except Exception as e:
                print(f"\n✗ Judge evaluation failed: {e}")
                print(f"Continuing with job completion...\n")

    # Display analytics summary if available
    if 'analytics' in saved_job_data:
        engine = AnalyticsEngine(analytics_config)
        print(f"\n{engine.format_summary(saved_job_data['analytics'])}")

    # Final summary
    print(f"\nResults saved to:")
    print(f"  JSON: {job_path}")
    if text_summary_path:
        print(f"  Text: {text_summary_path}")
    if chat_path:
        print(f"  Chat: {chat_path}")
    print(f"\nJob Duration: {job_duration:.2f} seconds")
    print(f"{'='*80}\n")

    # Post-job behavioral analysis prompt (if not already done via judge config)
    try:
        from behavioral_prompt_handler import (
            prompt_for_behavioral_analysis,
            run_behavioral_analysis,
            prompt_for_profile_update
        )

        # Check if we should prompt (interactive mode, no existing personality eval)
        chunking = prompt_for_behavioral_analysis(job_path, interactive=True)

        if chunking:
            # Run analysis and stage results
            staged_results_path = run_behavioral_analysis(
                job_path,
                chunking,
                framework_config=None,  # Use default
                staging_dir=None  # Use default
            )

            # Prompt to apply to master profiles
            prompt_for_profile_update(staged_results_path, interactive=True)

    except Exception as e:
        print(f"Warning: Behavioral analysis prompt failed: {e}\n")


if __name__ == "__main__":
    main()
