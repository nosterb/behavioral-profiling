#!/usr/bin/env python3
"""
Repair judge JSON evaluations using the proper json_validation structure.

This maintains:
- Original invalid JSON for posterity (original_invalid_response)
- Repair status tracking (repaired: true/false)
- Statistical exclusion flags (exclude_from_stats)
- Full audit trail
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from model_providers import create_provider, parse_model_config


def find_flagged_evaluations():
    """Find all judge evaluations that need repair."""
    json_files = list(Path('outputs/single_prompt_jobs').rglob('*.json'))
    flagged = []

    for f in json_files:
        try:
            with open(f) as fp:
                data = json.load(fp)

            if 'judge_evaluation' not in data:
                continue

            evals = data['judge_evaluation'].get('evaluations', [])

            for eval_idx, ev in enumerate(evals):
                model_name = ev.get('display_name', 'unknown')

                if 'pass1_judges' not in ev:
                    continue

                # Check each judge
                for judge_idx, judge in enumerate(ev.get('pass1_judges', [])):
                    # Skip if already has json_validation (already processed)
                    if 'json_validation' in judge:
                        continue

                    raw_eval = judge.get('raw_evaluation')
                    extracted = judge.get('extracted_json')

                    needs_repair = False
                    reason = None
                    repair_type = None

                    # Null raw_evaluation = system error
                    if raw_eval is None or raw_eval == '':
                        needs_repair = True
                        reason = 'null_raw_evaluation'
                        repair_type = 'system_error'
                    # Error in extracted_json
                    elif isinstance(extracted, dict) and 'error' in extracted:
                        needs_repair = True
                        reason = f"system_error: {extracted.get('error')}"
                        repair_type = 'system_error'
                    # Missing or malformed extracted_json
                    elif extracted is None or extracted == {} or 'scores' not in extracted:
                        needs_repair = True
                        reason = 'malformed_extraction'
                        repair_type = 'json_repair'

                    if needs_repair:
                        flagged.append({
                            'file': f,
                            'reason': reason,
                            'repair_type': repair_type,
                            'model': model_name,
                            'eval_idx': eval_idx,
                            'judge_idx': judge_idx,
                            'judge': judge,
                            'raw_evaluation': raw_eval,
                            'original_extracted_json': extracted
                        })

        except Exception as e:
            print(f"Error scanning {f}: {e}")

    return flagged


def extract_json_with_claude(raw_evaluation):
    """Use Claude 4.5 to extract JSON from raw evaluation text."""

    prompt = f"""Extract the JSON evaluation from this text. The JSON should have this exact structure:

{{
  "scores": {{
    "warmth": <number 1-10>,
    "formality": <number 1-10>,
    "hedging": <number 1-10>,
    "aggression": <number 1-10>,
    "transgression": <number 1-10>,
    "grandiosity": <number 1-10>,
    "tribalism": <number 1-10>,
    "depth": <number 1-10>,
    "authenticity": <number 1-10>
  }},
  "notable_quote": "...",
  "observations": "..."
}}

TEXT TO EXTRACT FROM:
{raw_evaluation}

Return ONLY the extracted JSON, wrapped in ```json``` code fence. If no valid JSON can be extracted, return an empty JSON object {{}}."""

    try:
        # Create Claude 4.5 Sonnet provider
        provider = create_provider(
            provider_type="bedrock",
            model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            display_name="Claude-4.5-Sonnet"
        )

        result = provider.invoke(prompt, max_tokens=4096, extended_thinking=False)

        response = result.response_text

        # Extract JSON from response
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            extracted_json = json.loads(json_match.group(1))

            # Validate structure
            if 'scores' in extracted_json and isinstance(extracted_json['scores'], dict):
                if len(extracted_json['scores']) == 9:
                    return {'success': True, 'extracted_json': extracted_json}

        return {'success': False, 'reason': 'no_valid_json'}

    except Exception as e:
        return {'success': False, 'reason': str(e)}


def repair_evaluation(flagged_item, job_data):
    """
    Repair a single judge evaluation using the json_validation structure.

    Structure added to judge:
    {
      "json_validation": {
        "original_valid": false,
        "repaired": true/false,
        "original_invalid_response": {
          "raw_text": "...",
          "extracted_json": ...,
          "extraction_failed": true,
          "flagged_for_repair": true
        },
        "exclude_from_stats": true/false,
        "repaired_at": "ISO timestamp",
        "repaired_by": "repair_judge_json.py"
      }
    }
    """

    eval_idx = flagged_item['eval_idx']
    judge_idx = flagged_item['judge_idx']
    repair_type = flagged_item['repair_type']

    evaluation = job_data['judge_evaluation']['evaluations'][eval_idx]
    judge = evaluation['pass1_judges'][judge_idx]

    # Preserve original invalid response
    original_invalid_response = {
        "raw_text": flagged_item['raw_evaluation'] or "",
        "extracted_json": flagged_item['original_extracted_json'],
        "extraction_failed": True,
        "flagged_for_repair": True
    }

    # Initialize json_validation structure
    json_validation = {
        "original_valid": False,
        "repaired": False,
        "original_invalid_response": original_invalid_response,
        "exclude_from_stats": False,
        "repaired_at": datetime.now().isoformat(),
        "repaired_by": "repair_judge_json.py"
    }

    if repair_type == 'system_error':
        # Cannot repair system errors - exclude from stats
        json_validation['exclude_from_stats'] = True
        judge['json_validation'] = json_validation
        return {'success': False, 'reason': 'system_error', 'action': 'flagged_excluded'}

    elif repair_type == 'json_repair':
        # Attempt to extract JSON from existing raw_evaluation
        raw_eval = flagged_item['raw_evaluation']

        if not raw_eval:
            # No raw evaluation to work with
            json_validation['exclude_from_stats'] = True
            judge['json_validation'] = json_validation
            return {'success': False, 'reason': 'no_raw_eval', 'action': 'flagged_excluded'}

        result = extract_json_with_claude(raw_eval)

        if result['success']:
            # Successful repair
            judge['extracted_json'] = result['extracted_json']
            json_validation['repaired'] = True
            json_validation['exclude_from_stats'] = False
            judge['json_validation'] = json_validation
            return {'success': True, 'action': 'json_extracted'}
        else:
            # Repair failed - exclude from stats
            json_validation['exclude_from_stats'] = True
            judge['json_validation'] = json_validation
            return {'success': False, 'reason': result.get('reason'), 'action': 'repair_failed_excluded'}

    return {'success': False, 'reason': 'unknown_repair_type'}


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Repair judge JSON evaluations with proper json_validation structure')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be repaired')
    parser.add_argument('--file', type=str, help='Repair specific file only')
    parser.add_argument('--flag-only', action='store_true', help='Only show flagged files, do not repair')
    args = parser.parse_args()

    print("=" * 80)
    print("JUDGE JSON REPAIR UTILITY")
    print("Using json_validation structure for proper audit trail")
    print("=" * 80)

    # Find flagged evaluations
    print("\nScanning for flagged evaluations...")
    flagged = find_flagged_evaluations()

    print(f"\nFound {len(flagged)} flagged evaluations")

    if not flagged:
        print("No repairs needed!")
        return

    # Filter by file if specified
    if args.file:
        flagged = [f for f in flagged if args.file in str(f['file'])]
        print(f"Filtered to {len(flagged)} evaluations in specified file")

    # Group by type
    by_type = {}
    for item in flagged:
        repair_type = item['repair_type']
        if repair_type not in by_type:
            by_type[repair_type] = []
        by_type[repair_type].append(item)

    # Show summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"JSON extraction repairs: {len(by_type.get('json_repair', []))}")
    print(f"System errors (will be excluded from stats): {len(by_type.get('system_error', []))}")

    # Show details
    print("\n" + "=" * 80)
    print("FLAGGED EVALUATIONS")
    print("=" * 80)

    for item in flagged:
        print(f"\n{item['file'].name}")
        print(f"  Model: {item['model']}")
        print(f"  Judge: {item['judge_idx'] + 1} ({item['judge']['judge_display_name']})")
        print(f"  Issue: {item['reason']}")
        print(f"  Action: {item['repair_type']}")

    if args.flag_only or args.dry_run:
        print("\n" + "=" * 80)
        if args.flag_only:
            print("[FLAG ONLY] No repairs will be performed")
        else:
            print("[DRY RUN] No changes will be made")
        return

    # Confirm
    print("\n" + "=" * 80)
    print(f"Ready to repair {len(flagged)} evaluations")
    print("This will add json_validation structure to preserve original data")
    response = input("Proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return

    # Process repairs
    print("\n" + "=" * 80)
    print("REPAIRING")
    print("=" * 80)

    repaired_count = 0
    excluded_count = 0
    failed_count = 0

    # Group by file
    files_to_repair = {}
    for item in flagged:
        file_path = item['file']
        if file_path not in files_to_repair:
            files_to_repair[file_path] = []
        files_to_repair[file_path].append(item)

    for file_path, items in files_to_repair.items():
        print(f"\n{file_path.name}")

        # Create backup FIRST (before loading into memory)
        backup_path = file_path.with_suffix('.json.backup_original')
        if not backup_path.exists():  # Only backup once
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"  📦 Created backup: {backup_path.name}")

        # Load file
        with open(file_path) as f:
            job_data = json.load(f)

        file_modified = False

        for item in items:
            model_name = item['model']
            judge_num = item['judge_idx'] + 1
            print(f"  {model_name} / Judge {judge_num}... ", end='', flush=True)

            result = repair_evaluation(item, job_data)

            if result.get('success'):
                print("✓ repaired")
                repaired_count += 1
                file_modified = True
            elif result.get('action') in ['flagged_excluded', 'repair_failed_excluded']:
                print(f"⚠ excluded from stats ({result.get('reason')})")
                excluded_count += 1
                file_modified = True
            else:
                print(f"✗ {result.get('reason')}")
                failed_count += 1

        # Save modified file
        if file_modified:
            with open(file_path, 'w') as f:
                json.dump(job_data, f, indent=2)

            print(f"  💾 Saved with json_validation structure")

    # Final summary
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Successfully repaired: {repaired_count}")
    print(f"Excluded from stats: {excluded_count}")
    print(f"Failed: {failed_count}")
    print(f"Total processed: {repaired_count + excluded_count + failed_count}")
    print("\nUse scripts/find_json_validation_repairs.py to view all repairs")


if __name__ == '__main__':
    main()
