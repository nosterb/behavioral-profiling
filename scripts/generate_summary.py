#!/usr/bin/env python3
"""
Generate text summary from existing agent job JSON report.

Usage:
    python generate_summary.py <path_to_json_report> [--detailed]
"""

import json
import sys
from pathlib import Path
from typing import Dict

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analytics import AnalyticsEngine


def generate_summary_from_json(json_path: Path, detailed: bool = True, output_dir: Path = None) -> Path:
    """Generate text summary from existing JSON report."""

    # Load the JSON report
    with open(json_path, 'r') as f:
        job_data = json.load(f)

    # Extract metadata
    request_id = job_data['job_metadata']['request_id']
    timestamp = job_data['job_metadata']['timestamp']

    # Determine output directory
    if output_dir is None:
        # Use default outputs/agent_jobs directory (relative to project root)
        project_root = Path(__file__).parent.parent
        output_dir = project_root / "outputs" / "agent_jobs"

    # Create summaries subdirectory
    summaries_dir = output_dir / "summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)

    # Check if analytics data exists in the JSON
    analytics_data = job_data.get('analytics')

    if not analytics_data:
        print("Warning: No analytics data found in JSON report.")
        print("The job may have been run with analytics disabled.")
        print("Attempting to regenerate analytics from raw data...")

        # Try to regenerate analytics
        analytics_config = {
            "enabled": True,
            "include": ["basic_metrics", "tool_analysis", "model_comparison"]
        }
        engine = AnalyticsEngine(analytics_config)
        analytics_data = engine.run_analytics(job_data)

        if not analytics_data:
            print("Error: Could not generate analytics from job data.")
            sys.exit(1)

    # Create analytics engine and format summary
    analytics_config = {
        "enabled": True,
        "include": list(analytics_data.keys()) if analytics_data else ["basic_metrics", "tool_analysis", "model_comparison"],
        "text_summary_detailed": detailed
    }
    engine = AnalyticsEngine(analytics_config)
    summary = engine.format_summary(analytics_data, detailed=detailed)

    # Add job metadata header
    header_lines = [
        "=" * 80,
        f"AGENT JOB SUMMARY: {request_id}",
        "=" * 80,
        f"Agent Profile: {job_data['job_metadata']['agent_profile']}",
        f"Timestamp: {timestamp}",
        "",
        "USER REQUEST:",
        "-" * 80,
        job_data['request']['user_request'].strip(),
        "-" * 80,
        ""
    ]

    full_summary = '\n'.join(header_lines) + '\n' + summary

    # Generate filename based on the JSON report filename with .md extension
    json_filename = json_path.stem  # e.g., "agent_job_engineering_job_001_20251120_105805"
    summary_filename = f"{json_filename}_summary.md"

    summary_path = summaries_dir / summary_filename

    # Write to file
    with open(summary_path, 'w') as f:
        f.write(full_summary)

    print(f"✓ Summary saved to: {summary_path}")
    print(f"  💡 Open in VS Code and press Cmd/Ctrl+Shift+V for formatted preview")
    return summary_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_summary_from_json.py <path_to_json_report> [--detailed]")
        print("\nOptions:")
        print("  --detailed    Include detailed per-model information (default: True)")
        print("  --concise     Exclude detailed per-model information")
        print("\nExample:")
        print("  python generate_summary_from_json.py outputs/agent_jobs/reports/agent_job_engineering_job_001_20251120_105805.json")
        print("  python generate_summary_from_json.py outputs/agent_jobs/reports/agent_job_*.json --concise")
        sys.exit(1)

    # Parse arguments
    json_path = Path(sys.argv[1])
    detailed = True  # Default to detailed

    if "--concise" in sys.argv:
        detailed = False
    elif "--detailed" in sys.argv:
        detailed = True

    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    if not json_path.suffix == '.json':
        print(f"Error: File must be a JSON file: {json_path}")
        sys.exit(1)

    try:
        generate_summary_from_json(json_path, detailed=detailed)
    except Exception as e:
        print(f"Error generating summary: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
