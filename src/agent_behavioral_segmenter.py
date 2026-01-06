#!/usr/bin/env python3
"""
Agent Chat Segmentation for Behavioral Evaluation

Splits long agent conversations into N-turn chunks for behavioral judging.
Each chunk contains N complete turns (agent output + tool response pairs).
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


def segment_conversation(conversation_log: List[Dict], turns_per_segment: int) -> List[List[Dict]]:
    """
    Split conversation log into segments of N turns.

    Each turn consists of:
    1. Agent output (role: agent)
    2. Tool response (role: tool_sim)

    Args:
        conversation_log: Full conversation log from agent job
        turns_per_segment: Number of turns per segment

    Returns:
        List of conversation segments (each segment is a list of log entries)
    """
    if turns_per_segment <= 0:
        raise ValueError("turns_per_segment must be > 0")

    segments = []
    current_segment = []
    turn_count = 0

    for entry in conversation_log:
        current_segment.append(entry)

        # Count a turn when we see a tool_simulator response (completes the agent->tool pair)
        role = entry.get('role', '')
        if role == 'tool_simulator' or role == 'tool_sim':
            turn_count += 1

            # Check if we've reached the segment size
            if turn_count >= turns_per_segment:
                segments.append(current_segment)
                current_segment = []
                turn_count = 0

    # Add remaining entries as final segment (if any)
    if current_segment:
        segments.append(current_segment)

    return segments


def format_segment_as_text(segment: List[Dict], segment_num: int, total_segments: int) -> str:
    """
    Format a conversation segment as human-readable text for judge evaluation.

    Args:
        segment: List of conversation log entries
        segment_num: Current segment number (1-indexed)
        total_segments: Total number of segments

    Returns:
        Formatted text suitable for behavioral judge
    """
    lines = [
        f"=== Conversation Segment {segment_num}/{total_segments} ===",
        ""
    ]

    for i, entry in enumerate(segment, 1):
        role = entry.get('role', 'unknown')
        content = entry.get('content', '')
        timestamp = entry.get('timestamp', '')

        if role == 'agent':
            lines.append(f"[AGENT OUTPUT {i}]")
        elif role == 'tool_sim':
            lines.append(f"[TOOL RESPONSE {i}]")
        else:
            lines.append(f"[{role.upper()} {i}]")

        if timestamp:
            lines.append(f"Timestamp: {timestamp}")

        lines.append("")
        lines.append(content)
        lines.append("")
        lines.append("-" * 80)
        lines.append("")

    return '\n'.join(lines)


def prompt_user_for_segmentation() -> Optional[int]:
    """
    Ask user if they want to process agent job for behavioral evaluation.

    Returns:
        Number of turns per segment, or None if user declines
    """
    print(f"\n{'='*80}")
    print("BEHAVIORAL SEGMENTATION PROMPT")
    print(f"{'='*80}\n")

    # Ask if user wants personality processing
    while True:
        response = input("Would you like to process this agent job for behavioral evaluation? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            break
        elif response in ['n', 'no']:
            print("Skipping behavioral segmentation.")
            return None
        else:
            print("Please enter 'y' or 'n'")

    # Ask for turns per segment
    while True:
        try:
            turns = input("\nHow many turns per segment? (1 turn = 1 agent output + 1 tool response): ").strip()
            turns_int = int(turns)
            if turns_int <= 0:
                print("Please enter a positive number.")
                continue
            return turns_int
        except ValueError:
            print("Please enter a valid number.")


def create_behavioral_judge_jobs(agent_job_path: Path, turns_per_segment: int,
                                   judge_config_path: Path) -> List[Dict[str, Any]]:
    """
    Create behavioral judge evaluation jobs for each model in the agent job.
    Uses FULL judge pipeline as configured in personality.yaml.

    Args:
        agent_job_path: Path to agent job JSON file
        turns_per_segment: Number of turns per segment
        judge_config_path: Path to behavioral judge config

    Returns:
        List of judge evaluation results per model
    """
    import tempfile

    # Load agent job data
    with open(agent_job_path, 'r') as f:
        agent_job = json.load(f)

    # Load judge config
    with open(judge_config_path, 'r') as f:
        judge_config = yaml.safe_load(f)

    # Create temporary directory for segment job files
    temp_dir = Path(tempfile.mkdtemp(prefix='behavioral_segments_'))

    try:
        results = []

        # Process each model's conversation
        for model_result in agent_job.get('models', []):
            display_name = model_result.get('display_name', 'Unknown')
            conversation_log = model_result.get('conversation_log', [])

            if not conversation_log:
                print(f"  ⚠ {display_name}: No conversation log found, skipping")
                continue

            print(f"\n  Processing {display_name}...")

            # Segment the conversation
            segments = segment_conversation(conversation_log, turns_per_segment)
            print(f"    Split into {len(segments)} segment(s)")

            # Evaluate each segment with FULL judge pipeline
            segment_evaluations = []
            for seg_num, segment in enumerate(segments, 1):
                print(f"    Evaluating segment {seg_num}/{len(segments)}...")

                # Format segment as text
                segment_text = format_segment_as_text(segment, seg_num, len(segments))

                # Run FULL judge evaluation on this segment
                try:
                    segment_eval = evaluate_segment_behavioral(
                        segment_text,
                        display_name,
                        judge_config,
                        seg_num,
                        len(segments),
                        temp_dir
                    )
                    segment_evaluations.append(segment_eval)
                    print(f"      ✓ Segment {seg_num} complete")
                except Exception as e:
                    print(f"      ✗ Error: {e}")
                    segment_evaluations.append({
                        'segment_num': seg_num,
                        'error': str(e)
                    })

            # Aggregate scores across segments (simple average)
            aggregated_scores = aggregate_behavioral_scores(segment_evaluations)

            results.append({
                'model': display_name,
                'total_segments': len(segments),
                'turns_per_segment': turns_per_segment,
                'segment_evaluations': segment_evaluations,
                'aggregated_scores': aggregated_scores
            })

            print(f"    Aggregated scores: {aggregated_scores}")

        return results

    finally:
        # Clean up temp directory
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def evaluate_segment_behavioral(segment_text: str, model_name: str,
                                  judge_config: Dict, segment_num: int,
                                  total_segments: int,
                                  temp_job_dir: Path) -> Dict[str, Any]:
    """
    Run FULL behavioral judge evaluation on a single conversation segment.
    Uses the complete judge pipeline: all judges, post-processing, comparative, etc.

    Args:
        segment_text: Formatted segment text
        model_name: Name of model being evaluated
        judge_config: Judge configuration (personality.yaml contents)
        segment_num: Current segment number
        total_segments: Total number of segments
        temp_job_dir: Temporary directory for segment job files

    Returns:
        Evaluation results with scores from full judge pipeline
    """
    from judge_invoke import run_judge_evaluation, parse_judge_models, parse_comparative_judge
    import tempfile

    # Create a temporary "job file" for this segment that looks like a single-prompt job
    # This allows run_judge_evaluation to process it normally
    temp_job_data = {
        'job_metadata': {
            'job_id': f'segment_{segment_num}_{model_name}',
            'timestamp': datetime.now().isoformat(),
            'segment_info': {
                'segment_num': segment_num,
                'total_segments': total_segments,
                'model_being_evaluated': model_name
            }
        },
        'prompt': f'(Agent conversation segment {segment_num}/{total_segments})',
        'models': [{
            'model_id': model_name,
            'display_name': model_name,
            'response': segment_text,
            'success': True
        }]
    }

    # Save temporary job file
    temp_job_path = temp_job_dir / f'segment_{segment_num}_{model_name.replace(" ", "_")}.json'
    with open(temp_job_path, 'w') as f:
        json.dump(temp_job_data, f, indent=2)

    # Parse judge configuration (same as batch_invoke.py does)
    judge_models = parse_judge_models(judge_config)
    comparative_judge_config = parse_comparative_judge(judge_config)

    # Get judge configuration options
    judge_id = judge_config.get('judge_id', f'segment_{segment_num}_judge')
    judge_prompt = judge_config['judge_prompt']
    jq_filter = judge_config.get('jq_filter', '.response')  # Extract response field
    append_to_source = False  # Don't append to temp file
    anonymize_pass1 = judge_config.get('anonymize_pass1', True)
    post_processing = judge_config.get('post_processing', [])

    # Add segmentation context to judge prompt
    context = f"\nNOTE: This is segment {segment_num} of {total_segments} from a multi-turn agent conversation.\n\n"
    judge_prompt_with_context = context + judge_prompt

    try:
        # Run FULL judge evaluation (all judges, post-processing, comparative)
        eval_result = run_judge_evaluation(
            source_job_path=str(temp_job_path),
            judge_id=judge_id,
            judge_prompt=judge_prompt_with_context,
            judge_models=judge_models,
            jq_filter=jq_filter,
            append_to_source=append_to_source,
            comparative_judge_config=comparative_judge_config,
            anonymize_pass1=anonymize_pass1,
            retry_config=None,
            post_processing=post_processing
        )

        # Extract final averaged scores (after post-processing)
        scores = {}
        if 'final_averaged_scores' in eval_result:
            scores = eval_result['final_averaged_scores'].get('scores', {})
        elif 'evaluations' in eval_result and eval_result['evaluations']:
            # Extract from first evaluation (there should only be one for segments)
            first_eval = eval_result['evaluations'][0]
            if 'final_averaged_scores' in first_eval:
                scores = first_eval['final_averaged_scores'].get('scores', {})
            elif 'scores' in first_eval:
                scores = first_eval['scores']

        return {
            'segment_num': segment_num,
            'scores': scores,
            'full_evaluation': eval_result,  # Include complete evaluation results
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        raise RuntimeError(f"Segment evaluation failed: {str(e)}")
    finally:
        # Clean up temp file
        if temp_job_path.exists():
            temp_job_path.unlink()


def aggregate_behavioral_scores(segment_evaluations: List[Dict]) -> Dict[str, float]:
    """
    Aggregate personality scores across all segments (simple average).

    Args:
        segment_evaluations: List of evaluation results per segment

    Returns:
        Aggregated scores (dimension -> average score)
    """
    # Collect all scores by dimension
    dimension_scores = {}

    for eval_result in segment_evaluations:
        if 'error' in eval_result:
            continue  # Skip failed segments

        scores = eval_result.get('scores', {})
        for dimension, score in scores.items():
            if dimension not in dimension_scores:
                dimension_scores[dimension] = []
            dimension_scores[dimension].append(score)

    # Calculate averages
    aggregated = {}
    for dimension, score_list in dimension_scores.items():
        if score_list:
            aggregated[dimension] = round(sum(score_list) / len(score_list), 2)

    return aggregated


def append_behavioral_results_to_job(agent_job_path: Path, behavioral_results: List[Dict]) -> None:
    """
    Append behavioral evaluation results back to the source agent job file.

    Args:
        agent_job_path: Path to agent job JSON file
        behavioral_results: Personality evaluation results per model
    """
    # Load existing job data
    with open(agent_job_path, 'r') as f:
        job_data = json.load(f)

    # Create behavioral evaluation section
    behavioral_section = {
        'evaluation_type': 'behavioral_segmentation',
        'timestamp': datetime.now().isoformat(),
        'results_by_model': {}
    }

    for result in behavioral_results:
        model_name = result['model']
        behavioral_section['results_by_model'][model_name] = {
            'total_segments': result['total_segments'],
            'turns_per_segment': result['turns_per_segment'],
            'aggregated_scores': result['aggregated_scores'],
            'segment_evaluations': result['segment_evaluations']
        }

    # Append to job data
    if 'behavioral_evaluation' not in job_data:
        job_data['behavioral_evaluation'] = behavioral_section
    else:
        # Merge with existing (shouldn't happen, but handle it)
        job_data['behavioral_evaluation'].update(behavioral_section)

    # Write back to file
    with open(agent_job_path, 'w') as f:
        json.dump(job_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Personality evaluation results appended to {agent_job_path.name}")


def run_agent_behavioral_segmentation(agent_job_path: Path,
                                        turns_per_segment: Optional[int] = None,
                                        judge_config_path: Optional[Path] = None,
                                        interactive: bool = True) -> bool:
    """
    Main entry point for agent behavioral segmentation.

    Args:
        agent_job_path: Path to completed agent job JSON
        turns_per_segment: Number of turns per segment (None = prompt user)
        judge_config_path: Path to behavioral judge config (default: payload/judge_configs/behavior.yaml)
        interactive: Whether to prompt user (default: True)

    Returns:
        True if segmentation was performed, False if skipped
    """
    # Set default judge config
    if judge_config_path is None:
        judge_config_path = Path("payload/judge_configs/behavior.yaml")

    if not judge_config_path.exists():
        print(f"✗ Personality judge config not found: {judge_config_path}")
        return False

    # Prompt user if interactive and turns not specified
    if interactive and turns_per_segment is None:
        turns_per_segment = prompt_user_for_segmentation()
        if turns_per_segment is None:
            return False  # User declined

    # If still None after prompting, default to 3 turns
    if turns_per_segment is None:
        turns_per_segment = 3
        print(f"Using default: {turns_per_segment} turns per segment")

    print(f"\n{'='*80}")
    print(f"RUNNING BEHAVIORAL SEGMENTATION")
    print(f"{'='*80}")
    print(f"Agent Job: {agent_job_path.name}")
    print(f"Turns per segment: {turns_per_segment}")
    print(f"Judge Config: {judge_config_path}")
    print(f"{'='*80}\n")

    # Create and run behavioral judge jobs
    try:
        results = create_behavioral_judge_jobs(
            agent_job_path,
            turns_per_segment,
            judge_config_path
        )

        # Append results to source job
        append_behavioral_results_to_job(agent_job_path, results)

        print(f"\n{'='*80}")
        print(f"BEHAVIORAL SEGMENTATION COMPLETE")
        print(f"{'='*80}\n")

        return True

    except Exception as e:
        print(f"\n✗ Personality segmentation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
