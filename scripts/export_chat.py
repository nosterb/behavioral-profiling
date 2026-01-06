#!/usr/bin/env python3
"""
Export chat from existing agent job JSON report.

Usage:
    python export_chat.py <path_to_json_report>
"""

import json
import sys
from pathlib import Path
from typing import Dict


def format_conversation_content(content: str) -> str:
    """Format conversation content for vertical readability.

    Attempts to parse JSON and format it in a human-readable way.
    Falls back to original content if not valid JSON.
    """
    try:
        # Try to parse as JSON
        data = json.loads(content)
        # Pretty print with indentation
        return json.dumps(data, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        # Not JSON or malformed, return as-is
        return content


def export_chat_from_json(json_path: Path, output_dir: Path = None) -> Path:
    """Generate chat export from existing JSON report."""

    # Load the JSON report
    with open(json_path, 'r') as f:
        job_data = json.load(f)

    # Extract request_id and timestamp from job_metadata
    request_id = job_data['job_metadata']['request_id']
    timestamp = job_data['job_metadata']['timestamp']

    # Determine output directory
    if output_dir is None:
        # Use default outputs/agent_jobs directory (relative to project root)
        project_root = Path(__file__).parent.parent
        output_dir = project_root / "outputs" / "agent_jobs"

    # Create chats subdirectory
    chats_dir = output_dir / "chats"
    chats_dir.mkdir(parents=True, exist_ok=True)

    lines = []

    # Header
    lines.extend([
        "=" * 80,
        f"AGENT CONVERSATION EXPORT: {request_id}",
        "=" * 80,
        f"Agent Profile: {job_data['job_metadata']['agent_profile']}",
        f"Timestamp: {job_data['job_metadata']['timestamp']}",
        f"Total Models: {job_data['job_metadata']['total_models']}",
        "",
        "USER REQUEST:",
        "-" * 80,
        job_data['request']['user_request'].strip(),
        "-" * 80,
        ""
    ])

    # Process each model's conversation
    for model_result in job_data['models']:
        display_name = model_result.get('display_name', 'Unknown')
        model_id = model_result.get('model_id', 'Unknown')
        extended_thinking = model_result.get('extended_thinking_enabled', False)

        lines.extend([
            "",
            "=" * 80,
            f"MODEL: {display_name}",
            "=" * 80,
            f"Model ID: {model_id}",
            f"Extended Thinking: {'Enabled' if extended_thinking else 'Disabled'}",
            f"Total Turns: {model_result.get('total_turns', 0)}",
            f"Completion Reason: {model_result.get('completion_reason', 'Unknown')}",
            ""
        ])

        # Check for errors
        if model_result.get('error'):
            lines.extend([
                "ERROR:",
                "-" * 80,
                model_result['error'],
                "-" * 80,
                ""
            ])
            continue

        # Export conversation log
        conversation_log = model_result.get('conversation_log', [])

        if not conversation_log:
            lines.append("(No conversation log available)\n")
            continue

        for entry in conversation_log:
            turn = entry.get('turn', '?')
            role = entry.get('role', 'unknown')
            content = entry.get('content', '')
            thinking = entry.get('thinking', None)

            # Format role header
            if role == 'agent':
                role_header = f"TURN {turn} - AGENT"
            elif role == 'tool_simulator':
                role_header = f"TURN {turn} - TOOL SIMULATOR"
            else:
                role_header = f"TURN {turn} - {role.upper()}"

            lines.extend([
                "-" * 80,
                role_header,
                "-" * 80
            ])

            # Include thinking if present and extended_thinking was enabled
            if thinking and extended_thinking:
                lines.extend([
                    "",
                    "[EXTENDED THINKING]",
                    thinking.strip(),
                    ""
                ])

            # Parse and format JSON content for better readability
            formatted_content = format_conversation_content(content)
            lines.extend([
                formatted_content,
                ""
            ])

    # Footer
    lines.extend([
        "",
        "=" * 80,
        "END OF CONVERSATION EXPORT",
        "=" * 80,
        ""
    ])

    # Generate filename based on the JSON report filename with .md extension
    # Extract timestamp from original filename if possible
    json_filename = json_path.stem  # e.g., "agent_job_engineering_job_001_20251120_105805"
    chat_filename = f"{json_filename}_chat.md"

    chat_path = chats_dir / chat_filename

    # Write to file
    with open(chat_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"✓ Chat exported to: {chat_path}")
    print(f"  💡 Open in VS Code and press Cmd/Ctrl+Shift+V for formatted preview")
    return chat_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python export_chat_from_json.py <path_to_json_report>")
        print("\nExample:")
        print("  python export_chat_from_json.py outputs/agent_jobs/reports/agent_job_engineering_job_001_20251120_105805.json")
        sys.exit(1)

    json_path = Path(sys.argv[1])

    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    if not json_path.suffix == '.json':
        print(f"Error: File must be a JSON file: {json_path}")
        sys.exit(1)

    try:
        export_chat_from_json(json_path)
    except Exception as e:
        print(f"Error exporting chat: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
