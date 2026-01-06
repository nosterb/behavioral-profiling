#!/usr/bin/env python3
"""
Export utilities for creating human-readable outputs from job results.
Supports batch jobs, agent jobs, and judge evaluations.
"""

import json
import textwrap
from pathlib import Path
from typing import Dict, Any, Optional


def wrap_text(text: str, width: int = 100, preserve_newlines: bool = True) -> str:
    """Wrap text to specified width while optionally preserving newlines."""
    if preserve_newlines:
        lines = text.split('\n')
        wrapped_lines = []
        for line in lines:
            if len(line) <= width:
                wrapped_lines.append(line)
            else:
                wrapped = textwrap.fill(line, width=width, break_long_words=False, break_on_hyphens=False)
                wrapped_lines.append(wrapped)
        return '\n'.join(wrapped_lines)
    else:
        return textwrap.fill(text, width=width, break_long_words=False, break_on_hyphens=False)


def export_batch_job_chat(job_data: Dict[str, Any], job_id: str, timestamp: str, output_dir: Path) -> Path:
    """
    Export batch job results to human-readable Markdown format.

    Args:
        job_data: Complete job data dictionary
        job_id: Job identifier
        timestamp: Job timestamp
        output_dir: Output directory (outputs/single_prompt_jobs/)

    Returns:
        Path to created chat export file
    """
    # Create chats subdirectory
    chats_dir = output_dir / "chats"
    chats_dir.mkdir(parents=True, exist_ok=True)

    lines = []

    # Header
    lines.extend([
        f"# Batch Job Export: {job_id}",
        "",
        f"**Timestamp:** {job_data['job_metadata']['timestamp']}  ",
        f"**Total Models:** {job_data['job_metadata']['total_models']}  ",
        f"**Successful:** {job_data['job_metadata']['successful']}  ",
        f"**Failed:** {job_data['job_metadata']['failed']}  ",
        "",
        "## Prompt",
        "",
        "```",
        wrap_text(job_data['prompt'].strip()),
        "```",
        "",
        "---",
        ""
    ])

    # Process each model's response
    for model_result in job_data['models']:
        display_name = model_result.get('display_name', 'Unknown')
        model_id = model_result.get('model_id', 'Unknown')
        provider = model_result.get('provider', 'unknown')
        extended_thinking = model_result.get('extended_thinking_enabled', False)
        success = model_result.get('success', False)

        lines.extend([
            "",
            f"## Model: {display_name}",
            "",
            f"**Model ID:** `{model_id}`  ",
            f"**Provider:** {provider}  ",
            f"**Extended Thinking:** {'✓ Enabled' if extended_thinking else '✗ Disabled'}  ",
            f"**Status:** {'✓ Success' if success else '✗ Failed'}  ",
        ])

        # Add token counts if available
        if model_result.get('input_tokens'):
            lines.append(f"**Input Tokens:** {model_result['input_tokens']}  ")
        if model_result.get('output_tokens'):
            lines.append(f"**Output Tokens:** {model_result['output_tokens']}  ")

        # Add cost if available (OpenAI, Grok, Gemini)
        if model_result.get('cost_usd') is not None:
            lines.append(f"**Cost:** ${model_result['cost_usd']:.6f}  ")

        # Add stop reason
        if model_result.get('stop_reason'):
            lines.append(f"**Stop Reason:** {model_result['stop_reason']}  ")

        lines.append("")

        # Check for errors
        if model_result.get('error'):
            lines.extend([
                "### ❌ Error",
                "",
                "```",
                wrap_text(model_result['error'], width=100),
                "```",
                "",
                "---",
                ""
            ])
            continue

        # Show thinking if present
        thinking = model_result.get('thinking')
        if thinking:
            lines.extend([
                "### 💭 Extended Thinking",
                "",
                "```",
                wrap_text(thinking, width=100),
                "```",
                ""
            ])

        # Show response
        response = model_result.get('response')
        if response:
            lines.extend([
                "### 📝 Response",
                "",
                wrap_text(response, width=100),
                "",
                "---",
                ""
            ])
        else:
            lines.extend([
                "*(No response available)*",
                "",
                "---",
                ""
            ])

    # Add judge evaluation if present
    if 'judge_evaluation' in job_data:
        lines.extend(format_judge_section(job_data['judge_evaluation']))

    # Write to file
    filename = f"job_{job_id}_{timestamp}_chat.md"
    output_path = chats_dir / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return output_path


def export_judge_results_chat(judge_data: Dict[str, Any], output_path: Path) -> Path:
    """
    Export standalone judge results to human-readable Markdown format.

    Args:
        judge_data: Complete judge evaluation data
        output_path: Path to save the export (will change extension to .md)

    Returns:
        Path to created chat export file
    """
    # Create markdown file alongside JSON
    md_path = output_path.with_suffix('.md')

    lines = []

    judge_meta = judge_data.get('judge_metadata', {})

    # Header
    lines.extend([
        f"# Judge Evaluation: {judge_meta.get('judge_id', 'Unknown')}",
        "",
        f"**Source Job:** {judge_meta.get('source_job_id', 'Unknown')}  ",
        f"**Judge Model:** {judge_meta.get('judge_display_name', 'Unknown')}  ",
        f"**Judge Provider:** {judge_meta.get('judge_provider', 'unknown')}  ",
        f"**Timestamp:** {judge_meta.get('timestamp', 'Unknown')}  ",
        f"**Models Evaluated:** {judge_meta.get('total_models_evaluated', 0)}  ",
        f"**Anonymize Pass 1:** {'✓ Yes' if judge_meta.get('anonymize_pass1', True) else '✗ No'}  ",
        "",
        "## Evaluation Criteria",
        "",
        "```",
        wrap_text(judge_meta.get('judge_prompt', 'No prompt available'), width=100),
        "```",
        "",
        "---",
        ""
    ])

    # Add formatted judge section
    lines.extend(format_judge_section(judge_data, include_header=False))

    # Write to file
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return md_path


def format_judge_section(judge_data: Dict[str, Any], include_header: bool = True) -> list:
    """
    Format judge evaluation data as Markdown lines.
    Can be used for appended judge sections or standalone exports.

    Args:
        judge_data: Judge evaluation data (can be full judge_data or just judge_evaluation section)
        include_header: Whether to include the main header

    Returns:
        List of markdown lines
    """
    lines = []

    # Handle both full judge data and judge_evaluation section
    if 'judge_metadata' in judge_data:
        judge_meta = judge_data['judge_metadata']
        evaluations = judge_data.get('evaluations', [])
        comparative = judge_data.get('comparative_analysis', {})
    else:
        # Assume it's a judge_evaluation section from appended data
        judge_meta = judge_data.get('judge_metadata', {})
        evaluations = judge_data.get('evaluations', [])
        comparative = judge_data.get('comparative_analysis', {})

    if include_header:
        lines.extend([
            "",
            "# 🏛️ Judge Evaluation",
            "",
            f"**Judge ID:** {judge_meta.get('judge_id', 'Unknown')}  ",
            f"**Judge Model:** {judge_meta.get('judge_display_name', 'Unknown')}  ",
            f"**Models Evaluated:** {judge_meta.get('total_models_evaluated', 0)}  ",
            ""
        ])

    # Pass 1: Individual Evaluations
    lines.extend([
        "",
        "## Pass 1: Individual Evaluations",
        ""
    ])

    if judge_meta.get('anonymize_pass1'):
        lines.append("*(Models were anonymized as Model A, Model B, etc. to reduce bias)*  ")
        lines.append("")

    for i, evaluation in enumerate(evaluations, 1):
        display_name = evaluation.get('display_name', 'Unknown')

        lines.extend([
            f"### Model {i}: {display_name}",
            ""
        ])

        # Show error if present
        if evaluation.get('error'):
            lines.extend([
                "**Status:** ✗ Error  ",
                "",
                "```",
                evaluation['error'],
                "```",
                ""
            ])
            continue

        # Show token usage
        lines.extend([
            f"**Input Tokens:** {evaluation.get('input_tokens', 0)}  ",
            f"**Output Tokens:** {evaluation.get('output_tokens', 0)}  ",
            ""
        ])

        # Show individual judge evaluations if multiple judges used (Pass 1)
        pass1_judges = evaluation.get('pass1_judges', [])
        if pass1_judges:
            lines.extend([
                f"**Pass 1 Judges:** {len(pass1_judges)}  ",
                ""
            ])

            for j, judge_eval in enumerate(pass1_judges, 1):
                judge_name = judge_eval.get('judge_display_name', f'Judge {j}')
                lines.extend([
                    f"#### Judge {j}: {judge_name}",
                    ""
                ])

                # Show scores from this judge
                extracted_json = judge_eval.get('extracted_json')
                if extracted_json and isinstance(extracted_json, dict) and 'scores' in extracted_json:
                    lines.extend([
                        "**Scores:**",
                        "```json",
                        json.dumps(extracted_json['scores'], indent=2),
                        "```",
                        ""
                    ])

                # Show thinking if present
                if judge_eval.get('thinking'):
                    lines.extend([
                        "<details>",
                        "<summary>💭 Extended Thinking</summary>",
                        "",
                        "```",
                        wrap_text(judge_eval['thinking'], width=100),
                        "```",
                        "</details>",
                        ""
                    ])

                # Show evaluation
                lines.extend([
                    "**Evaluation:**",
                    "",
                    wrap_text(judge_eval.get('raw_evaluation', 'No evaluation available'), width=100),
                    ""
                ])

            # Show final averaged scores if available (from post-processing)
            final_scores = evaluation.get('final_averaged_scores')
            if final_scores and 'scores' in final_scores:
                lines.extend([
                    "#### 📊 Final Averaged Scores",
                    "",
                    f"*(Averaged across {final_scores.get('num_judges', 0)} judges)*  ",
                    "",
                    "```json",
                    json.dumps(final_scores['scores'], indent=2),
                    "```",
                    ""
                ])

        else:
            # Legacy single-judge format
            extracted_json = evaluation.get('extracted_json')
            if extracted_json and isinstance(extracted_json, dict):
                if 'scores' in extracted_json:
                    lines.extend([
                        "**Scores:**",
                        "```json",
                        json.dumps(extracted_json['scores'], indent=2),
                        "```",
                        ""
                    ])

                if 'overall_score' in extracted_json:
                    lines.append(f"**Overall Score:** {extracted_json['overall_score']}/10  ")
                    lines.append("")

            # Show full evaluation
            lines.extend([
                "**Full Evaluation:**",
                "",
                wrap_text(evaluation.get('raw_evaluation', 'No evaluation available'), width=100),
                ""
            ])

        lines.extend([
            "---",
            ""
        ])

    # Pass 2: Comparative Analysis
    if comparative:
        lines.extend([
            "",
            "## Pass 2: Comparative Analysis",
            ""
        ])

        comp_judge = judge_meta.get('comparative_judge')
        if comp_judge:
            lines.extend([
                f"**Comparative Judge:** {comp_judge.get('display_name', 'Unknown')}  ",
                f"**Reveal Names:** {'✓ Yes' if comp_judge.get('reveal_names', True) else '✗ No'}  ",
                ""
            ])

        # Show token usage
        lines.extend([
            f"**Input Tokens:** {comparative.get('input_tokens', 0)}  ",
            f"**Output Tokens:** {comparative.get('output_tokens', 0)}  ",
            ""
        ])

        # Show comparative summary
        lines.extend([
            "### Comparative Summary",
            "",
            wrap_text(comparative.get('raw_summary', 'No summary available'), width=100),
            ""
        ])

        # Show extracted JSON if available
        extracted_json = comparative.get('extracted_json')
        if extracted_json:
            lines.extend([
                "### Structured Comparison",
                "",
                "```json",
                json.dumps(extracted_json, indent=2),
                "```",
                ""
            ])

    # Summary
    lines.extend([
        "---",
        "",
        "## Summary",
        "",
        f"**Total Input Tokens:** {judge_meta.get('total_input_tokens', 0)}  ",
        f"**Total Output Tokens:** {judge_meta.get('total_output_tokens', 0)}  ",
        ""
    ])

    return lines
