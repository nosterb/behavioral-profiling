#!/usr/bin/env python3
"""
Extract and validate telemetry V3 JSON from all telemetry job outputs.
Saves extraction metadata back to job files.
"""

import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, 'src')
from judge_invoke import extract_telemetry_response


def process_telemetry_job(job_path: Path) -> dict:
    """
    Process a single telemetry job file.

    Returns:
        dict with statistics
    """
    print(f"\nProcessing: {job_path.name}")

    with open(job_path, 'r') as f:
        job_data = json.load(f)

    stats = {
        'total_models': 0,
        'successful_extractions': 0,
        'failed_extractions': 0,
        'missing_response_field': 0,
        'json_parse_failed': 0,
        'models_processed': []
    }

    modified = False

    for model in job_data.get('models', []):
        stats['total_models'] += 1
        display_name = model.get('display_name', 'unknown')
        response_text = model.get('response', '')

        if not response_text:
            print(f"  ⚠️  {display_name}: No response text")
            stats['failed_extractions'] += 1
            continue

        # Extract telemetry response
        result = extract_telemetry_response(response_text)

        # Store extraction metadata back to model
        model['telemetry_extraction'] = {
            'extracted_json': result['extracted_json'],
            'json_validation': result['json_validation'],
            'telemetry_metrics': result.get('telemetry_metrics'),
            'telemetry_stream': result.get('telemetry_stream')
        }
        modified = True

        # Track statistics
        validation = result['json_validation']

        if validation['parsed'] and validation['structure_valid'] and validation['has_response_field']:
            stats['successful_extractions'] += 1
            print(f"  ✅ {display_name}: Extracted successfully")

            # Store extracted response length
            stats['models_processed'].append({
                'model': display_name,
                'success': True,
                'response_length': len(result['extracted_response']),
                'has_metrics': validation['has_metrics'],
                'has_telemetry': validation['has_telemetry']
            })
        else:
            stats['failed_extractions'] += 1
            error = validation.get('error', 'unknown')

            if 'missing_response_field' in error:
                stats['missing_response_field'] += 1
            elif 'json_parse_failed' in error or 'json_extraction_failed' in error:
                stats['json_parse_failed'] += 1

            print(f"  ❌ {display_name}: {error}")

            stats['models_processed'].append({
                'model': display_name,
                'success': False,
                'error': error
            })

    # Save updated job file
    if modified:
        with open(job_path, 'w') as f:
            json.dump(job_data, f, indent=2)
        print(f"  💾 Saved extraction metadata to {job_path.name}")

    return stats


def main():
    # Find all telemetry V3 job files
    outputs_dir = Path('outputs/single_prompt_jobs')
    telemetry_dirs = list(outputs_dir.glob('baseline_telemetryV3_*'))

    if not telemetry_dirs:
        print("No telemetry V3 job directories found")
        return

    print(f"Found {len(telemetry_dirs)} telemetry V3 job directories")
    print("=" * 80)

    overall_stats = {
        'total_jobs': 0,
        'total_models': 0,
        'successful_extractions': 0,
        'failed_extractions': 0,
        'missing_response_field': 0,
        'json_parse_failed': 0,
        'error_types': Counter()
    }

    # Process each directory
    for telem_dir in sorted(telemetry_dirs):
        job_files = list(telem_dir.glob('*/*.json'))

        for job_file in job_files:
            overall_stats['total_jobs'] += 1
            stats = process_telemetry_job(job_file)

            overall_stats['total_models'] += stats['total_models']
            overall_stats['successful_extractions'] += stats['successful_extractions']
            overall_stats['failed_extractions'] += stats['failed_extractions']
            overall_stats['missing_response_field'] += stats['missing_response_field']
            overall_stats['json_parse_failed'] += stats['json_parse_failed']

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total jobs processed: {overall_stats['total_jobs']}")
    print(f"Total models: {overall_stats['total_models']}")
    print(f"Successful extractions: {overall_stats['successful_extractions']} ({100*overall_stats['successful_extractions']/max(overall_stats['total_models'],1):.1f}%)")
    print(f"Failed extractions: {overall_stats['failed_extractions']} ({100*overall_stats['failed_extractions']/max(overall_stats['total_models'],1):.1f}%)")

    if overall_stats['failed_extractions'] > 0:
        print("\nFailure breakdown:")
        print(f"  - Missing response field: {overall_stats['missing_response_field']}")
        print(f"  - JSON parse failed: {overall_stats['json_parse_failed']}")

    print("\n" + "=" * 80)

    # Write detailed report
    report_path = Path('outputs/behavioral_profiles/baseline/TELEMETRY_EXTRACTION_REPORT.txt')
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        f.write("# TELEMETRY V3 EXTRACTION REPORT\n\n")
        f.write(f"Date: {Path(job_file).stat().st_mtime}\n")
        f.write(f"Total jobs: {overall_stats['total_jobs']}\n")
        f.write(f"Total models: {overall_stats['total_models']}\n\n")
        f.write(f"Successful extractions: {overall_stats['successful_extractions']} ({100*overall_stats['successful_extractions']/max(overall_stats['total_models'],1):.1f}%)\n")
        f.write(f"Failed extractions: {overall_stats['failed_extractions']} ({100*overall_stats['failed_extractions']/max(overall_stats['total_models'],1):.1f}%)\n\n")

        if overall_stats['failed_extractions'] > 0:
            f.write("Failure breakdown:\n")
            f.write(f"  - Missing response field: {overall_stats['missing_response_field']}\n")
            f.write(f"  - JSON parse failed: {overall_stats['json_parse_failed']}\n")

    print(f"Detailed report written to: {report_path}")


if __name__ == '__main__':
    main()
