#!/usr/bin/env python3
"""
Analysis Orchestrator - Run configured analyses on study data.

This script reads an analysis configuration file and executes all enabled
analysis modules in order. Supports personality studies, behavioral intervention studies,
and custom analysis workflows.

Usage:
    # Run all configured analyses
    python3 scripts/run_analysis.py analysis_configs/personality_study_v4.yaml

    # Run specific analyses only
    python3 scripts/run_analysis.py analysis_configs/personality_study_v4.yaml \
        --only chat_export,similarity_analysis

    # Dry run (show what would be executed)
    python3 scripts/run_analysis.py analysis_configs/personality_study_v4.yaml --dry-run

Configuration format:
    study_name: personality_study_v4
    data_directory: outputs/single_prompt_jobs/12_7_2025_personality_v4

    analyses:
      - type: chat_export
        enabled: true
        options:
          style: chatbot

      - type: per_job_visualizations
        enabled: true
        options:
          chart_types: [spider, heatmap]
"""

import sys
import yaml
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


# Map analysis types to their implementation scripts
ANALYSIS_MODULES = {
    # Universal modules
    'chat_export': {
        'script': 'scripts/export_single_prompt_chat.py',
        'description': 'Export jobs to human-readable markdown',
        'args_template': ['{data_directory}']
    },

    # Personality modules
    'per_job_visualizations': {
        'script': 'src/visualize_personality.py',
        'description': 'Generate per-job spider charts and heatmaps',
        'args_template': ['{data_directory}']
    },
    'cross_job_aggregation': {
        'script': 'src/aggregate_personality.py',
        'description': 'Aggregate scores across all jobs',
        'args_template': ['{data_directory}']
    },
    'intervention_grouping': {
        'script': 'scripts/visualize_by_intervention.py',
        'description': 'Group jobs by intervention type',
        'args_template': ['{data_directory}']
    },
    'average_profile': {
        'script': 'scripts/visualize_average_personality.py',
        'description': 'Compute universal AI personality pattern',
        'args_template': ['{data_directory}']
    },
    'similarity_analysis': {
        'script': 'scripts/analyze_profile_similarity.py',
        'description': 'Statistical similarity between models',
        'args_template': ['{data_directory}']
    },
    'calculation_trace': {
        'script': 'scripts/trace_personality_math.py',
        'description': 'Verify calculation correctness',
        'args_template': ['{data_directory}']
    },

    # Awareness modules
    'tool_usage_analysis': {
        'script': 'scripts/analyze_tool_usage.py',
        'description': 'Analyze tool invocation patterns',
        'args_template': ['{data_directory}']
    },

    # Placeholder modules (not yet implemented)
    'data_export': {
        'script': None,
        'description': 'Export data in multiple formats (NOT YET IMPLEMENTED)',
        'args_template': []
    },
    'statistical_summary': {
        'script': None,
        'description': 'Generate statistical summary report (NOT YET IMPLEMENTED)',
        'args_template': []
    },
    'comparative_report': {
        'script': None,
        'description': 'Generate executive summary (NOT YET IMPLEMENTED)',
        'args_template': []
    },
    'turn_count_analysis': {
        'script': None,
        'description': 'Analyze conversation turn counts (NOT YET IMPLEMENTED)',
        'args_template': []
    },
    'checkpoint_urgency': {
        'script': None,
        'description': 'Analyze checkpoint awareness indicators (NOT YET IMPLEMENTED)',
        'args_template': []
    },
    'telemetry_authority': {
        'script': None,
        'description': 'Analyze telemetry awareness indicators (NOT YET IMPLEMENTED)',
        'args_template': []
    },
    'intervention_comparison': {
        'script': None,
        'description': 'Statistical comparison across interventions (NOT YET IMPLEMENTED)',
        'args_template': []
    },
    'custom_script': {
        'script': None,  # Provided in config
        'description': 'Run custom analysis script',
        'args_template': []
    }
}


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load and validate analysis configuration."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Validate required fields
    if 'study_name' not in config:
        raise ValueError("Config missing required field: study_name")
    if 'data_directory' not in config:
        raise ValueError("Config missing required field: data_directory")
    if 'analyses' not in config:
        raise ValueError("Config missing required field: analyses")

    return config


def format_args(args_template: List[str], config: Dict[str, Any], options: Dict[str, Any]) -> List[str]:
    """Format argument template with config values."""
    formatted = []

    for arg in args_template:
        # Replace placeholders
        formatted_arg = arg.format(
            data_directory=config.get('data_directory', ''),
            study_name=config.get('study_name', ''),
            output_directory=config.get('data_directory', '')
        )
        formatted.append(formatted_arg)

    return formatted


def run_analysis(
    analysis_type: str,
    config: Dict[str, Any],
    options: Dict[str, Any],
    dry_run: bool = False
) -> bool:
    """
    Run a single analysis module.

    Returns:
        True if successful, False if failed
    """
    module_info = ANALYSIS_MODULES.get(analysis_type)

    if not module_info:
        print(f"  ✗ Unknown analysis type: {analysis_type}")
        return False

    script = module_info['script']

    # Check if module is implemented
    if script is None:
        if analysis_type == 'custom_script':
            script = options.get('script')
            if not script:
                print(f"  ✗ Custom script not specified in options")
                return False
        else:
            print(f"  ⚠ {analysis_type}: {module_info['description']}")
            return True  # Don't fail on unimplemented modules

    # Check if script exists
    script_path = Path(script)
    if not script_path.exists():
        print(f"  ✗ Script not found: {script}")
        return False

    # Build command
    if analysis_type == 'custom_script':
        # Custom script with user-provided args
        cmd = ['python3', script]
        custom_args = options.get('args', [])
        for arg in custom_args:
            formatted_arg = arg.format(
                data_directory=config.get('data_directory', ''),
                output_directory=config.get('data_directory', '')
            )
            cmd.append(formatted_arg)
    else:
        # Standard module
        args = format_args(module_info['args_template'], config, options)
        cmd = ['python3', script] + args

    if dry_run:
        print(f"  [DRY RUN] Would execute: {' '.join(cmd)}")
        return True

    # Execute
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  ✓ {module_info['description']}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed: {module_info['description']}")
        print(f"    Error: {e.stderr[:200]}")
        return False

    except Exception as e:
        print(f"  ✗ Unexpected error: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Run configured analyses on study data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        'config',
        type=Path,
        help='Path to analysis configuration file (YAML)'
    )
    parser.add_argument(
        '--only',
        type=str,
        help='Run only these analyses (comma-separated, e.g., chat_export,similarity_analysis)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be executed without running'
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

    # Parse --only filter
    only_analyses = None
    if args.only:
        only_analyses = set(a.strip() for a in args.only.split(','))

    # Print header
    print(f"{'='*80}")
    print(f"Analysis Pipeline: {config['study_name']}")
    print(f"{'='*80}")
    print(f"Data directory: {config['data_directory']}")
    print(f"Configuration: {args.config}")
    if args.dry_run:
        print(f"Mode: DRY RUN (no changes will be made)")
    print(f"{'='*80}\n")

    # Validate data directory exists
    data_dir = Path(config['data_directory'])
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        sys.exit(1)

    # Run analyses in order
    analyses = config.get('analyses', [])
    total = len(analyses)
    enabled_count = sum(1 for a in analyses if a.get('enabled', True))

    if only_analyses:
        enabled_count = sum(1 for a in analyses if a.get('type') in only_analyses and a.get('enabled', True))

    print(f"Total analyses configured: {total}")
    print(f"Enabled analyses: {enabled_count}\n")

    successful = 0
    failed = 0
    skipped = 0

    for i, analysis_config in enumerate(analyses, 1):
        analysis_type = analysis_config.get('type')
        enabled = analysis_config.get('enabled', True)
        options = analysis_config.get('options', {})

        # Check if filtered
        if only_analyses and analysis_type not in only_analyses:
            continue

        print(f"[{i}/{total}] {analysis_type}")

        if not enabled:
            print(f"  ⊘ Disabled (set enabled: true to run)")
            skipped += 1
            continue

        # Run analysis
        success = run_analysis(analysis_type, config, options, args.dry_run)

        if success:
            successful += 1
        else:
            failed += 1

        print()  # Blank line between analyses

    # Summary
    print(f"{'='*80}")
    print(f"Analysis Pipeline Complete")
    print(f"{'='*80}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"{'='*80}")

    if args.dry_run:
        print("\nThis was a dry run. No analyses were actually executed.")

    # Exit with error code if any failed
    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
