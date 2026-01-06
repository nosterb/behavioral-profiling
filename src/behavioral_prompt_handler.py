#!/usr/bin/env python3
"""
Personality Analysis Prompt Handler

Unified module for prompting users about behavioral analysis across all job types.
Supports chunking strategies for long conversations and staged results.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime


class ChunkingStrategy:
    """Represents a chunking strategy for behavioral analysis."""

    def __init__(self, strategy_type: str, value: Optional[int] = None):
        """
        Initialize chunking strategy.

        Args:
            strategy_type: One of 'none', 'chunks', 'turns'
            value: Number of chunks or turns (required for 'chunks' and 'turns')
        """
        self.strategy_type = strategy_type
        self.value = value

    def __repr__(self):
        if self.strategy_type == 'none':
            return "n=1 (entire conversation)"
        elif self.strategy_type == 'chunks':
            return f"n={self.value} (split into {self.value} equal chunks)"
        elif self.strategy_type == 'turns':
            return f"n=turns:{self.value} (every {self.value} turns)"
        return f"ChunkingStrategy({self.strategy_type}, {self.value})"

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            'type': self.strategy_type,
            'value': self.value
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary."""
        return cls(data['type'], data.get('value'))


def load_framework_config(config_path: Optional[Path] = None) -> Dict:
    """
    Load personality framework configuration.

    Args:
        config_path: Path to framework config (default: outputs/behavioral_profiles/framework_config.yaml)

    Returns:
        Framework configuration dictionary
    """
    if config_path is None:
        config_path = Path("outputs/behavioral_profiles/framework_config.yaml")

    if not config_path.exists():
        # Return default config
        return {
            'framework_version': 'v1',
            'judge_config_path': 'payload/judge_configs/personality.yaml',
            'description': '9-dimension behavioral framework'
        }

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def check_if_behavioral_already_evaluated(job_data: Dict) -> bool:
    """
    Check if job already has behavioral evaluation from judge config.

    Args:
        job_data: Job data dictionary

    Returns:
        True if behavioral evaluation already exists
    """
    # Check for judge_evaluation (chained judge format)
    if 'judge_evaluation' in job_data:
        judge_meta = job_data['judge_evaluation'].get('judge_metadata', {})
        judge_id = judge_meta.get('judge_id', '')
        if 'personality' in judge_id.lower():
            return True

    # Check for judges (legacy format)
    if 'judges' in job_data:
        for judge in job_data['judges']:
            judge_id = judge.get('judge_id', '')
            if 'personality' in judge_id.lower():
                return True

    # Check for personality_evaluation section (from agent segmenter)
    if 'personality_evaluation' in job_data:
        return True

    return False


def get_job_info(job_path: Path) -> Dict[str, Any]:
    """
    Extract relevant info from job file for display.

    Args:
        job_path: Path to job JSON file

    Returns:
        Dictionary with job_type, model_count, turn_count, etc.
    """
    with open(job_path, 'r') as f:
        job_data = json.load(f)

    # Determine job type
    if 'conversation_log' in job_data.get('models', [{}])[0]:
        job_type = 'agent'
    elif 'simulation_type' in job_data.get('job_metadata', {}):
        sim_type = job_data['job_metadata']['simulation_type']
        job_type = sim_type  # 'agent' or 'chat'
    else:
        job_type = 'single_prompt'

    # Count models
    models = job_data.get('models', [])
    model_count = len(models)

    # Count turns (for agent/chat jobs)
    turn_count = 0
    if models and job_type in ['agent', 'chat']:
        conversation_log = models[0].get('conversation_log', [])
        # Count tool_simulator/tool_sim responses as turns
        turn_count = sum(1 for entry in conversation_log
                        if entry.get('role') in ['tool_simulator', 'tool_sim', 'user'])

    # Check if already evaluated
    already_evaluated = check_if_behavioral_already_evaluated(job_data)

    return {
        'job_type': job_type,
        'job_data': job_data,
        'model_count': model_count,
        'turn_count': turn_count,
        'already_evaluated': already_evaluated,
        'job_id': job_data.get('job_metadata', {}).get('job_id', job_path.stem)
    }


def prompt_for_behavioral_analysis(job_path: Path,
                                    interactive: bool = True,
                                    default_chunking: Optional[ChunkingStrategy] = None) -> Optional[ChunkingStrategy]:
    """
    Prompt user if they want to run behavioral analysis and choose chunking strategy.

    Args:
        job_path: Path to completed job file
        interactive: Whether to prompt user (if False, use default_chunking)
        default_chunking: Default chunking strategy if not interactive

    Returns:
        ChunkingStrategy if user wants analysis, None if declined
    """
    # Get job info
    job_info = get_job_info(job_path)

    # Skip if already evaluated with behavioral judge
    if job_info['already_evaluated']:
        if interactive:
            print(f"\n→ Job already has behavioral evaluation (skipping prompt)")
        return None

    # Non-interactive mode: use defaults
    if not interactive:
        if default_chunking is None:
            return ChunkingStrategy('none', None)  # n=1 by default
        return default_chunking

    # Interactive prompt
    print(f"\n{'='*80}")
    print(f"PERSONALITY ANALYSIS PROMPT")
    print(f"{'='*80}")
    print(f"Job: {job_path.name}")
    print(f"Type: {job_info['job_type']}")
    print(f"Models: {job_info['model_count']}")
    if job_info['turn_count'] > 0:
        print(f"Turns: {job_info['turn_count']}")
    print(f"{'='*80}\n")

    # Ask if user wants behavioral analysis
    while True:
        response = input("Run behavioral analysis? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            break
        elif response in ['n', 'no']:
            print("→ Skipping behavioral analysis")
            return None
        else:
            print("Please enter 'y' or 'n'")

    # For single-prompt jobs, only n=1 makes sense
    if job_info['job_type'] == 'single_prompt':
        print("\n→ Single-prompt job: using n=1 (entire response)")
        return ChunkingStrategy('none', None)

    # For agent/chat jobs, offer chunking options
    print("\nChunking Strategy:")
    print("  1. n=1 (entire conversation as one)")
    print("  2. n=N (split into N equal chunks)")
    print("  3. n=turns:X (every X turns)")
    print()

    while True:
        choice = input("Choose strategy [1-3, or press Enter for default n=1]: ").strip()

        # Default to n=1
        if not choice:
            print("→ Using default: n=1 (entire conversation)")
            return ChunkingStrategy('none', None)

        # Parse choice
        if choice == '1':
            return ChunkingStrategy('none', None)

        elif choice == '2':
            while True:
                try:
                    n = input("Number of chunks: ").strip()
                    n_int = int(n)
                    if n_int <= 0:
                        print("Please enter a positive number.")
                        continue
                    return ChunkingStrategy('chunks', n_int)
                except ValueError:
                    print("Please enter a valid number.")

        elif choice == '3':
            while True:
                try:
                    turns = input("Turns per segment: ").strip()
                    turns_int = int(turns)
                    if turns_int <= 0:
                        print("Please enter a positive number.")
                        continue
                    return ChunkingStrategy('turns', turns_int)
                except ValueError:
                    print("Please enter a valid number.")

        else:
            print("Please enter 1, 2, or 3")


def run_behavioral_analysis(job_path: Path,
                            chunking: ChunkingStrategy,
                            framework_config: Optional[Dict] = None,
                            staging_dir: Optional[Path] = None) -> Path:
    """
    Run behavioral analysis with specified chunking strategy.
    Results are staged in outputs/personality_staging/ for review.

    Args:
        job_path: Path to job file
        chunking: Chunking strategy to use
        framework_config: Framework configuration (default: load from file)
        staging_dir: Staging directory (default: outputs/personality_staging/)

    Returns:
        Path to staged results JSON file
    """
    # Load framework config
    if framework_config is None:
        framework_config = load_framework_config()

    # Set staging directory
    if staging_dir is None:
        staging_dir = Path("outputs/personality_staging")
    staging_dir.mkdir(parents=True, exist_ok=True)

    # Load job data
    with open(job_path, 'r') as f:
        job_data = json.load(f)

    job_info = get_job_info(job_path)
    job_type = job_info['job_type']

    print(f"\n{'='*80}")
    print(f"RUNNING PERSONALITY ANALYSIS")
    print(f"{'='*80}")
    print(f"Job: {job_path.name}")
    print(f"Strategy: {chunking}")
    print(f"Framework: {framework_config['framework_version']}")
    print(f"{'='*80}\n")

    # Route to appropriate handler based on job type and chunking
    if job_type == 'single_prompt' or chunking.strategy_type == 'none':
        # Single evaluation of entire job
        results = run_single_evaluation(job_path, framework_config)
    elif chunking.strategy_type == 'chunks':
        # Split into N equal chunks
        results = run_chunked_evaluation(job_path, chunking.value, framework_config)
    elif chunking.strategy_type == 'turns':
        # Use existing agent segmenter (every X turns)
        results = run_turn_based_evaluation(job_path, chunking.value, framework_config)
    else:
        raise ValueError(f"Unknown chunking strategy: {chunking.strategy_type}")

    # Create staged results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = job_info['job_id']
    staged_file = staging_dir / f"{job_id}_{timestamp}_personality.json"

    staged_data = {
        'job_id': job_id,
        'source_job_path': str(job_path),
        'timestamp': datetime.now().isoformat(),
        'framework_version': framework_config['framework_version'],
        'chunking_strategy': chunking.to_dict(),
        'results': results
    }

    with open(staged_file, 'w') as f:
        json.dump(staged_data, f, indent=2)

    print(f"\n✓ Behavioral analysis complete")
    print(f"  Staged results: {staged_file}")
    print()

    return staged_file


def run_single_evaluation(job_path: Path, framework_config: Dict) -> Dict:
    """
    Run behavioral evaluation on entire job (n=1).

    For single-prompt jobs: evaluates each model's response
    For agent/chat jobs: evaluates entire conversation per model

    Args:
        job_path: Path to job file
        framework_config: Framework configuration

    Returns:
        Evaluation results dictionary
    """
    from judge_invoke import run_judge_evaluation, parse_judge_models, parse_comparative_judge

    # Load judge config
    judge_config_path = Path(framework_config['judge_config_path'])
    with open(judge_config_path, 'r') as f:
        judge_config = yaml.safe_load(f)

    # Parse judge configuration
    judge_models = parse_judge_models(judge_config)
    comparative_judge_config = parse_comparative_judge(judge_config)

    judge_id = f"personality_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    judge_prompt = judge_config['judge_prompt']
    jq_filter = judge_config.get('jq_filter', '.response')
    anonymize_pass1 = judge_config.get('anonymize_pass1', True)
    post_processing = judge_config.get('post_processing', [])

    print(f"  Evaluating entire job with behavioral judge...")

    # Run full judge evaluation
    eval_result = run_judge_evaluation(
        source_job_path=str(job_path),
        judge_id=judge_id,
        judge_prompt=judge_prompt,
        judge_models=judge_models,
        jq_filter=jq_filter,
        append_to_source=False,  # Don't append yet (staging)
        comparative_judge_config=comparative_judge_config,
        anonymize_pass1=anonymize_pass1,
        retry_config=None,
        post_processing=post_processing
    )

    print(f"  ✓ Evaluation complete")

    return {
        'evaluation_type': 'single',
        'evaluation_result': eval_result
    }


def run_chunked_evaluation(job_path: Path, num_chunks: int, framework_config: Dict) -> Dict:
    """
    Split conversation into N equal chunks and evaluate each.

    Args:
        job_path: Path to job file
        num_chunks: Number of chunks to create
        framework_config: Framework configuration

    Returns:
        Evaluation results with aggregated scores
    """
    # Load job data
    with open(job_path, 'r') as f:
        job_data = json.load(f)

    from judge_invoke import run_judge_evaluation, parse_judge_models, parse_comparative_judge
    import tempfile

    # Load judge config
    judge_config_path = Path(framework_config['judge_config_path'])
    with open(judge_config_path, 'r') as f:
        judge_config = yaml.safe_load(f)

    judge_models = parse_judge_models(judge_config)
    comparative_judge_config = parse_comparative_judge(judge_config)
    judge_prompt = judge_config['judge_prompt']
    anonymize_pass1 = judge_config.get('anonymize_pass1', True)
    post_processing = judge_config.get('post_processing', [])

    # Create temp directory for chunk evaluations
    temp_dir = Path(tempfile.mkdtemp(prefix='personality_chunks_'))

    try:
        all_model_results = []

        # Process each model
        for model_result in job_data.get('models', []):
            display_name = model_result.get('display_name', 'Unknown')
            conversation_log = model_result.get('conversation_log', [])

            if not conversation_log:
                print(f"  ⚠ {display_name}: No conversation log, skipping")
                continue

            print(f"\n  Processing {display_name}...")

            # Split into chunks
            chunk_size = len(conversation_log) // num_chunks
            chunks = []
            for i in range(num_chunks):
                start = i * chunk_size
                end = start + chunk_size if i < num_chunks - 1 else len(conversation_log)
                chunks.append(conversation_log[start:end])

            print(f"    Split into {len(chunks)} chunks")

            # Evaluate each chunk
            chunk_evaluations = []
            for chunk_num, chunk in enumerate(chunks, 1):
                print(f"    Evaluating chunk {chunk_num}/{len(chunks)}...")

                # Format chunk as text
                chunk_text = format_conversation_chunk(chunk, chunk_num, len(chunks))

                # Create temp job file for this chunk
                temp_job = create_temp_job_file(
                    chunk_text,
                    display_name,
                    chunk_num,
                    len(chunks),
                    temp_dir
                )

                # Evaluate chunk
                try:
                    judge_id = f"behavioral_chunk_{chunk_num}"
                    eval_result = run_judge_evaluation(
                        source_job_path=str(temp_job),
                        judge_id=judge_id,
                        judge_prompt=judge_prompt,
                        judge_models=judge_models,
                        jq_filter='.response',
                        append_to_source=False,
                        comparative_judge_config=comparative_judge_config,
                        anonymize_pass1=anonymize_pass1,
                        retry_config=None,
                        post_processing=post_processing
                    )

                    # Extract scores
                    scores = extract_scores_from_eval(eval_result)
                    chunk_evaluations.append({
                        'chunk_num': chunk_num,
                        'scores': scores
                    })
                    print(f"      ✓ Chunk {chunk_num} complete")

                except Exception as e:
                    print(f"      ✗ Error: {e}")
                    chunk_evaluations.append({
                        'chunk_num': chunk_num,
                        'error': str(e)
                    })

            # Aggregate scores across chunks
            aggregated_scores = aggregate_chunk_scores(chunk_evaluations)

            all_model_results.append({
                'model': display_name,
                'total_chunks': len(chunks),
                'chunk_evaluations': chunk_evaluations,
                'aggregated_scores': aggregated_scores
            })

            print(f"    Aggregated scores: {aggregated_scores}")

        return {
            'evaluation_type': 'chunked',
            'num_chunks': num_chunks,
            'model_results': all_model_results
        }

    finally:
        # Clean up temp directory
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def run_turn_based_evaluation(job_path: Path, turns_per_segment: int, framework_config: Dict) -> Dict:
    """
    Use existing agent_personality_segmenter for turn-based evaluation.

    Args:
        job_path: Path to job file
        turns_per_segment: Number of turns per segment
        framework_config: Framework configuration

    Returns:
        Evaluation results
    """
    from agent_behavioral_segmenter import create_personality_judge_jobs

    judge_config_path = Path(framework_config['judge_config_path'])

    print(f"  Using turn-based segmentation ({turns_per_segment} turns per segment)...")

    results = create_personality_judge_jobs(
        job_path,
        turns_per_segment,
        judge_config_path
    )

    return {
        'evaluation_type': 'turn_based',
        'turns_per_segment': turns_per_segment,
        'model_results': results
    }


def format_conversation_chunk(chunk: List[Dict], chunk_num: int, total_chunks: int) -> str:
    """
    Format conversation chunk as text for evaluation.

    Args:
        chunk: List of conversation log entries
        chunk_num: Current chunk number
        total_chunks: Total number of chunks

    Returns:
        Formatted text
    """
    lines = [
        f"=== Conversation Chunk {chunk_num}/{total_chunks} ===",
        ""
    ]

    for i, entry in enumerate(chunk, 1):
        role = entry.get('role', 'unknown')
        content = entry.get('content', '')

        if role == 'agent':
            lines.append(f"[AGENT OUTPUT]")
        elif role in ['tool_sim', 'tool_simulator']:
            lines.append(f"[TOOL RESPONSE]")
        elif role == 'user':
            lines.append(f"[USER MESSAGE]")
        else:
            lines.append(f"[{role.upper()}]")

        lines.append("")
        lines.append(content)
        lines.append("")
        lines.append("-" * 80)
        lines.append("")

    return '\n'.join(lines)


def create_temp_job_file(chunk_text: str, model_name: str,
                        chunk_num: int, total_chunks: int,
                        temp_dir: Path) -> Path:
    """
    Create temporary job file for chunk evaluation.

    Args:
        chunk_text: Formatted chunk text
        model_name: Model being evaluated
        chunk_num: Current chunk number
        total_chunks: Total number of chunks
        temp_dir: Temporary directory

    Returns:
        Path to created temp file
    """
    temp_job_data = {
        'job_metadata': {
            'job_id': f'chunk_{chunk_num}_{model_name}',
            'timestamp': datetime.now().isoformat(),
            'chunk_info': {
                'chunk_num': chunk_num,
                'total_chunks': total_chunks,
                'model': model_name
            }
        },
        'prompt': f'(Conversation chunk {chunk_num}/{total_chunks})',
        'models': [{
            'model_id': model_name,
            'display_name': model_name,
            'response': chunk_text,
            'success': True
        }]
    }

    temp_path = temp_dir / f'chunk_{chunk_num}_{model_name.replace(" ", "_")}.json'
    with open(temp_path, 'w') as f:
        json.dump(temp_job_data, f, indent=2)

    return temp_path


def extract_scores_from_eval(eval_result: Dict) -> Dict[str, float]:
    """
    Extract personality scores from judge evaluation result.

    Args:
        eval_result: Judge evaluation result

    Returns:
        Dictionary of dimension -> score
    """
    # Try final_averaged_scores at top level first
    if 'final_averaged_scores' in eval_result:
        scores = eval_result['final_averaged_scores'].get('scores', {})
        if scores:
            return scores

    # Try evaluations array (standard judge format)
    if 'evaluations' in eval_result and eval_result['evaluations']:
        first_eval = eval_result['evaluations'][0]

        # Check for final_averaged_scores in evaluation
        if 'final_averaged_scores' in first_eval:
            scores = first_eval['final_averaged_scores'].get('scores', {})
            if scores:
                return scores

        # Fallback to direct scores field
        if 'scores' in first_eval:
            scores = first_eval['scores']
            if scores:
                return scores

    return {}


def aggregate_chunk_scores(chunk_evaluations: List[Dict]) -> Dict[str, float]:
    """
    Aggregate personality scores across chunks (simple average).

    Args:
        chunk_evaluations: List of chunk evaluation results

    Returns:
        Aggregated scores
    """
    dimension_scores = {}

    for chunk_eval in chunk_evaluations:
        if 'error' in chunk_eval:
            continue

        scores = chunk_eval.get('scores', {})
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


def prompt_for_profile_update(staged_results_path: Path,
                              interactive: bool = True) -> Optional[Dict]:
    """
    Prompt user if they want to apply staged results to master behavioral profiles.

    Args:
        staged_results_path: Path to staged results JSON
        interactive: Whether to prompt user

    Returns:
        Update result dictionary, or None if declined
    """
    # Load staged results
    with open(staged_results_path, 'r') as f:
        staged_data = json.load(f)

    # Non-interactive mode: auto-apply
    if not interactive:
        return apply_to_master_profiles(staged_results_path)

    # Show summary
    print(f"\n{'='*80}")
    print(f"APPLY TO MASTER PERSONALITY PROFILES")
    print(f"{'='*80}")
    print(f"Job ID: {staged_data['job_id']}")
    print(f"Framework: {staged_data['framework_version']}")
    print(f"Staged file: {staged_results_path.name}")

    # Count models
    results = staged_data['results']
    if 'model_results' in results:
        model_count = len(results['model_results'])
        models = [r['model'] for r in results['model_results']]
    elif 'evaluation_result' in results:
        # Single evaluation
        eval_result = results['evaluation_result']
        evals = eval_result.get('evaluations', [])
        model_count = len(evals)
        models = [e.get('display_name', 'Unknown') for e in evals]
    else:
        model_count = 0
        models = []

    print(f"Models: {model_count}")
    for model in models:
        print(f"  - {model}")
    print(f"{'='*80}\n")

    # Ask user
    while True:
        response = input("Apply to master profiles? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return apply_to_master_profiles(staged_results_path)
        elif response in ['n', 'no']:
            print("→ Results remain staged (not applied)")
            return None
        else:
            print("Please enter 'y' or 'n'")


def apply_to_master_profiles(staged_results_path: Path) -> Dict:
    """
    Apply staged personality results to master profiles.

    Args:
        staged_results_path: Path to staged results JSON

    Returns:
        Update result dictionary
    """
    from behavioral_profile_manager import BehavioralProfileManager

    # Load staged data
    with open(staged_results_path, 'r') as f:
        staged_data = json.load(f)

    # First, append results to source job file
    source_job_path = Path(staged_data['source_job_path'])
    append_staged_results_to_job(staged_results_path, source_job_path)

    # Initialize profile manager
    master_dir = Path("outputs/behavioral_profiles")
    manager = BehavioralProfileManager(master_dir)

    print(f"\n{'='*80}")
    print(f"UPDATING MASTER PROFILES")
    print(f"{'='*80}\n")

    # Add to profiles
    job_id = staged_data['job_id']
    result = manager.add_job_evaluation(job_id, source_job_path, update_viz=True)

    if result['status'] == 'success':
        print(f"✓ Updated profiles for: {', '.join(result['models'])}")
        print(f"  Master directory: {master_dir}")
    else:
        print(f"⚠ {result['message']}")

    print()

    return result


def append_staged_results_to_job(staged_results_path: Path, job_path: Path):
    """
    Append staged personality results to source job file.

    Args:
        staged_results_path: Path to staged results
        job_path: Path to source job file
    """
    # Load both files
    with open(staged_results_path, 'r') as f:
        staged_data = json.load(f)

    with open(job_path, 'r') as f:
        job_data = json.load(f)

    # Create behavioral evaluation section
    personality_section = {
        'evaluation_type': 'personality_analysis',
        'timestamp': staged_data['timestamp'],
        'framework_version': staged_data['framework_version'],
        'chunking_strategy': staged_data['chunking_strategy'],
        'staged_results_file': str(staged_results_path),
        'results': staged_data['results']
    }

    # Append to job data
    if 'personality_evaluation' not in job_data:
        job_data['personality_evaluation'] = personality_section
    else:
        # Update existing
        job_data['personality_evaluation'].update(personality_section)

    # Write back
    with open(job_path, 'w') as f:
        json.dump(job_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Results appended to {job_path.name}")
