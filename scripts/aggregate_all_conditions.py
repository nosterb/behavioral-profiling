#!/usr/bin/env python3
"""
Aggregate behavioral profiles from ALL conditions into root profiles directory.

This ensures outputs/behavioral_profiles/visualizations/ shows the true average
across ALL data processed (baseline, authority, urgency, minimal_steering,
telemetryV3, reminder).

Usage:
    python3 scripts/aggregate_all_conditions.py
    python3 scripts/aggregate_all_conditions.py --dry-run
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

BASE_DIR = Path("outputs/behavioral_profiles")
CONDITIONS = ["baseline", "authority", "urgency", "minimal_steering", "telemetryV3", "reminder"]


def load_condition_profiles(condition: str) -> dict:
    """Load all profiles from a condition directory."""
    profiles_dir = BASE_DIR / condition / "profiles"
    if not profiles_dir.exists():
        print(f"  Warning: {condition}/profiles/ not found, skipping")
        return {}

    profiles = {}
    for profile_file in profiles_dir.glob("*.json"):
        with open(profile_file) as f:
            data = json.load(f)
        model_name = data.get("model_name", profile_file.stem)
        profiles[model_name] = data

    return profiles


def aggregate_profiles(all_condition_profiles: dict) -> dict:
    """
    Aggregate profiles across all conditions.

    For each model, combines scores from all conditions using weighted average
    based on evaluation count.
    """
    # Structure: model -> dimension -> {sum, count}
    aggregated = defaultdict(lambda: defaultdict(lambda: {"sum": 0.0, "count": 0}))
    model_conditions = defaultdict(list)  # Track which conditions each model appears in

    for condition, profiles in all_condition_profiles.items():
        for model_name, profile in profiles.items():
            model_conditions[model_name].append(condition)
            dimensions = profile.get("dimensions", {})

            for dim_name, dim_data in dimensions.items():
                if isinstance(dim_data, dict):
                    dim_sum = dim_data.get("sum", 0)
                    dim_count = dim_data.get("count", 0)
                else:
                    # Handle legacy format where dimension is just a score
                    dim_sum = dim_data
                    dim_count = 1

                aggregated[model_name][dim_name]["sum"] += dim_sum
                aggregated[model_name][dim_name]["count"] += dim_count

    # Convert to final profile format
    final_profiles = {}
    for model_name, dimensions in aggregated.items():
        profile = {
            "model_name": model_name,
            "dimensions": {},
            "last_updated": datetime.now().isoformat(),
            "total_evaluations": 0,
            "conditions_included": model_conditions[model_name]
        }

        total_evals = 0
        for dim_name, dim_data in dimensions.items():
            count = dim_data["count"]
            avg = dim_data["sum"] / count if count > 0 else 0
            profile["dimensions"][dim_name] = {
                "sum": dim_data["sum"],
                "count": count,
                "average": avg
            }
            total_evals = max(total_evals, count)

        profile["total_evaluations"] = total_evals
        final_profiles[model_name] = profile

    return final_profiles


def save_aggregated_profiles(profiles: dict, dry_run: bool = False):
    """Save aggregated profiles to root profiles directory."""
    profiles_dir = BASE_DIR / "profiles"

    if not dry_run:
        profiles_dir.mkdir(parents=True, exist_ok=True)

        # Clear existing profiles
        for existing in profiles_dir.glob("*.json"):
            existing.unlink()

    for model_name, profile in profiles.items():
        # Create safe filename
        safe_name = model_name.lower().replace(" ", "-").replace("(", "").replace(")", "")
        file_path = profiles_dir / f"{safe_name}.json"

        if dry_run:
            print(f"  Would write: {file_path.name}")
        else:
            with open(file_path, "w") as f:
                json.dump(profile, f, indent=2)

    return len(profiles)


def save_aggregation_history(all_condition_profiles: dict, profiles: dict, dry_run: bool = False):
    """Save aggregation metadata to history directory."""
    history_dir = BASE_DIR / "history"

    if not dry_run:
        history_dir.mkdir(parents=True, exist_ok=True)

    # Create contributions summary
    contributions = {
        "aggregation_type": "cross_condition_aggregate",
        "generated": datetime.now().isoformat(),
        "conditions_included": list(all_condition_profiles.keys()),
        "condition_stats": {},
        "summary_statistics": {
            "total_models": len(profiles),
            "total_conditions": len(all_condition_profiles),
        }
    }

    for condition, cond_profiles in all_condition_profiles.items():
        contributions["condition_stats"][condition] = {
            "models": len(cond_profiles),
            "sample_evals": next(iter(cond_profiles.values()), {}).get("total_evaluations", 0) if cond_profiles else 0
        }

    if dry_run:
        print(f"\n  Aggregation summary:")
        print(f"    Conditions: {contributions['conditions_included']}")
        print(f"    Total models: {contributions['summary_statistics']['total_models']}")
    else:
        with open(history_dir / "contributions.json", "w") as f:
            json.dump(contributions, f, indent=2)

        # Also save to updates log
        log_file = history_dir / "updates_log.json"
        log = []
        if log_file.exists():
            with open(log_file) as f:
                log = json.load(f)

        log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "aggregate_all_conditions",
            "conditions": list(all_condition_profiles.keys()),
            "models_updated": list(profiles.keys())
        })

        with open(log_file, "w") as f:
            json.dump(log, f, indent=2)

    return contributions


def regenerate_visualizations(dry_run: bool = False):
    """Regenerate visualizations from aggregated profiles."""
    if dry_run:
        print("\n  Would regenerate visualizations/")
        return

    try:
        from behavioral_profile_manager import BehavioralProfileManager

        manager = BehavioralProfileManager(str(BASE_DIR))
        manager._generate_visualizations()
        print("\n  Regenerated visualizations/")
    except Exception as e:
        print(f"\n  Warning: Failed to regenerate visualizations: {e}")
        print("  Run manually: python3 -c \"from src.behavioral_profile_manager import BehavioralProfileManager; BehavioralProfileManager('outputs/behavioral_profiles')._generate_visualizations()\"")


def main():
    parser = argparse.ArgumentParser(description="Aggregate all condition profiles into root directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args()

    print("=" * 70)
    print("Aggregating All Condition Profiles")
    print("=" * 70)

    if args.dry_run:
        print("\n[DRY RUN - No changes will be made]\n")

    # Load profiles from all conditions
    print("\nLoading condition profiles:")
    all_condition_profiles = {}
    for condition in CONDITIONS:
        profiles = load_condition_profiles(condition)
        if profiles:
            all_condition_profiles[condition] = profiles
            print(f"  {condition}: {len(profiles)} models")

    if not all_condition_profiles:
        print("\nError: No condition profiles found!")
        sys.exit(1)

    # Aggregate
    print("\nAggregating across conditions...")
    aggregated = aggregate_profiles(all_condition_profiles)
    print(f"  Combined: {len(aggregated)} unique models")

    # Show sample
    sample_model = next(iter(aggregated.values()))
    sample_evals = sample_model.get("total_evaluations", 0)
    sample_conditions = len(sample_model.get("conditions_included", []))
    print(f"  Sample model: {sample_evals} total evaluations from {sample_conditions} conditions")

    # Save profiles
    print("\nSaving aggregated profiles:")
    n_saved = save_aggregated_profiles(aggregated, args.dry_run)
    if not args.dry_run:
        print(f"  Saved {n_saved} profiles to profiles/")

    # Save history
    print("\nSaving aggregation history:")
    save_aggregation_history(all_condition_profiles, aggregated, args.dry_run)
    if not args.dry_run:
        print("  Saved contributions.json and updates_log.json")

    # Regenerate visualizations
    print("\nRegenerating visualizations:")
    regenerate_visualizations(args.dry_run)

    print("\n" + "=" * 70)
    if args.dry_run:
        print("DRY RUN COMPLETE - No changes made")
        print("Run without --dry-run to apply changes")
    else:
        print("AGGREGATION COMPLETE")
        print(f"  profiles/: {n_saved} models (all conditions combined)")
        print(f"  visualizations/: Updated spider charts and heatmaps")
        print(f"  history/: Aggregation metadata saved")
    print("=" * 70)


if __name__ == "__main__":
    main()
