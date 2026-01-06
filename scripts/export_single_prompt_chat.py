#!/usr/bin/env python3
"""
Export chat-style markdown from single_prompt_job JSON files (with or without judge evaluations).

Usage:
    # Single file
    python scripts/export_single_prompt_chat.py outputs/single_prompt_jobs/12_7_2025_personality_v3/job_behavioral_deference_checkpoint_20251207_115041.json

    # All files in a directory
    python scripts/export_single_prompt_chat.py outputs/single_prompt_jobs/12_7_2025_personality_v3/
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.export_utils import export_batch_job_chat


def export_single_prompt_job(json_path: Path) -> Path:
    """
    Export a single_prompt_job JSON file to chat format.

    Args:
        json_path: Path to single_prompt_job JSON file

    Returns:
        Path to created chat export file
    """
    # Load the JSON
    with open(json_path, 'r') as f:
        job_data = json.load(f)

    # Extract job_id and timestamp from job_metadata
    job_id = job_data['job_metadata']['payload_name']
    timestamp = job_data['job_metadata']['timestamp']

    # Determine output directory (same directory as the JSON file)
    output_dir = json_path.parent

    # Use the batch job export function (works for single_prompt_jobs too!)
    chat_path = export_batch_job_chat(job_data, job_id, timestamp, output_dir)

    return chat_path


def export_directory(directory: Path) -> list[Path]:
    """
    Export all single_prompt_job JSON files in a directory.

    Args:
        directory: Directory containing job_*.json files

    Returns:
        List of created chat export files
    """
    json_files = sorted(directory.glob("job_*.json"))

    if not json_files:
        print(f"No job_*.json files found in {directory}")
        return []

    print(f"Found {len(json_files)} job files to export...")

    exported = []
    for json_file in json_files:
        try:
            chat_path = export_single_prompt_job(json_file)
            exported.append(chat_path)
            print(f"✓ Exported: {json_file.name} -> {chat_path.name}")
        except Exception as e:
            print(f"✗ Failed to export {json_file.name}: {e}")

    return exported


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Error: Path not found: {input_path}")
        sys.exit(1)

    try:
        if input_path.is_file():
            # Single file export
            if not input_path.suffix == '.json':
                print(f"Error: File must be a JSON file: {input_path}")
                sys.exit(1)

            chat_path = export_single_prompt_job(input_path)
            print(f"\n✓ Chat exported to: {chat_path}")
            print(f"  💡 Open in VS Code and press Cmd/Ctrl+Shift+V for formatted preview")

        elif input_path.is_dir():
            # Directory export
            exported = export_directory(input_path)
            print(f"\n✓ Exported {len(exported)} files to {input_path / 'chats'}/")
            print(f"  💡 Open in VS Code and press Cmd/Ctrl+Shift+V for formatted preview")
        else:
            print(f"Error: Invalid path: {input_path}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
