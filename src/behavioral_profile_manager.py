#!/usr/bin/env python3
"""
Master Behavioral Profile Manager

Maintains running averages of behavioral evaluations across all jobs.
Supports incremental updates and undo operations.

Profile Structure:
    outputs/behavioral_profiles/
    ├── profiles/
    │   ├── claude_sonnet_4_5.json
    │   └── ...
    ├── history/
    │   ├── contributions.json  # Track which jobs contributed what
    │   └── updates_log.json    # Chronological update log
    └── visualizations/
        ├── current_profiles.png
        └── comparative_heatmap.png
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class BehavioralProfileManager:
    """Manages incremental behavioral profile updates."""

    def __init__(self, master_dir: Path):
        """
        Initialize profile manager.

        Args:
            master_dir: Root directory for behavioral profiles (e.g., outputs/behavioral_profiles)
        """
        self.master_dir = Path(master_dir)
        self.profiles_dir = self.master_dir / "profiles"
        self.history_dir = self.master_dir / "history"
        self.viz_dir = self.master_dir / "visualizations"

        # Create directories
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.viz_dir.mkdir(parents=True, exist_ok=True)

        # Load or initialize contribution tracking
        self.contributions_file = self.history_dir / "contributions.json"
        self.contributions = self._load_contributions()

        # Load or initialize updates log
        self.log_file = self.history_dir / "updates_log.json"
        self.updates_log = self._load_log()

    def _load_contributions(self) -> Dict:
        """Load contribution tracking data."""
        if self.contributions_file.exists():
            with open(self.contributions_file, 'r') as f:
                return json.load(f)
        return {
            "job_contributions": {},  # job_id -> {model -> {dimension -> {score, weight}}}
            "version": "1.0"
        }

    def _save_contributions(self):
        """Save contribution tracking data."""
        with open(self.contributions_file, 'w') as f:
            json.dump(self.contributions, f, indent=2)

    def _load_log(self) -> List[Dict]:
        """Load updates log."""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []

    def _save_log(self):
        """Save updates log."""
        with open(self.log_file, 'w') as f:
            json.dump(self.updates_log, f, indent=2)

    def _load_profile(self, model_name: str) -> Dict:
        """Load existing profile for a model."""
        profile_file = self.profiles_dir / f"{self._sanitize_filename(model_name)}.json"

        if profile_file.exists():
            with open(profile_file, 'r') as f:
                return json.load(f)

        # Initialize new profile
        return {
            "model_name": model_name,
            "dimensions": {},  # dimension -> {average, count, sum}
            "last_updated": None,
            "total_evaluations": 0
        }

    def _save_profile(self, model_name: str, profile: Dict):
        """Save profile for a model."""
        profile_file = self.profiles_dir / f"{self._sanitize_filename(model_name)}.json"
        profile["last_updated"] = datetime.now().isoformat()

        with open(profile_file, 'w') as f:
            json.dump(profile, f, indent=2)

    def _sanitize_filename(self, name: str) -> str:
        """Convert model name to safe filename."""
        return name.replace('/', '_').replace(':', '_').replace(' ', '_').lower()

    def add_job_evaluation(self, job_id: str, job_file: Path, update_viz: bool = True) -> Dict[str, str]:
        """
        Add behavioral evaluations from a job to running profiles.

        Args:
            job_id: Unique identifier for this job
            job_file: Path to job JSON file with judge_evaluation
            update_viz: Whether to regenerate visualizations

        Returns:
            Dictionary with status and messages
        """
        # Load job data
        with open(job_file, 'r') as f:
            job_data = json.load(f)

        # Check for judge evaluation or behavioral evaluation
        if 'judge_evaluation' in job_data:
            eval_data = job_data['judge_evaluation']
            evaluations = eval_data.get('evaluations', [])
        elif 'behavioral_evaluation' in job_data:
            # Handle behavioral prompt handler format
            eval_data = job_data['behavioral_evaluation']
            results = eval_data.get('results', {})

            # Convert to evaluations format
            evaluations = []
            if 'model_results' in results:
                # Chunked or turn-based evaluation
                for model_result in results['model_results']:
                    evaluations.append({
                        'display_name': model_result['model'],
                        'scores': model_result.get('aggregated_scores', {})
                    })
            elif 'evaluation_result' in results:
                # Single evaluation
                eval_result = results['evaluation_result']
                evaluations = eval_result.get('evaluations', [])
        else:
            return {"status": "skipped", "message": "No judge evaluation or behavioral evaluation in job"}

        # Check if already processed
        if job_id in self.contributions['job_contributions']:
            return {"status": "skipped", "message": f"Job {job_id} already processed"}

        # Validate evaluations
        if not evaluations:
            return {"status": "skipped", "message": "No evaluations found"}

        # Track contributions for this job
        job_contributions = {}

        # Process each model's evaluation
        updated_models = []
        for eval_data in evaluations:
            model_name = eval_data.get('display_name') or eval_data.get('model_name')
            if not model_name:
                continue

            # Get dimension scores (try multiple locations)
            scores = eval_data.get('scores')
            if not scores:
                # Try nested in final_averaged_scores
                final_avg = eval_data.get('final_averaged_scores', {})
                scores = final_avg.get('scores', final_avg)

            if not scores or not isinstance(scores, dict):
                continue

            # Load model profile
            profile = self._load_profile(model_name)

            # Track contributions for undo
            model_contributions = {}

            # Update each dimension
            for dimension, score in scores.items():
                if not isinstance(score, (int, float)):
                    continue

                # Initialize dimension if new
                if dimension not in profile['dimensions']:
                    profile['dimensions'][dimension] = {
                        'sum': 0.0,
                        'count': 0,
                        'average': 0.0
                    }

                dim_data = profile['dimensions'][dimension]

                # Update running average
                dim_data['sum'] += score
                dim_data['count'] += 1
                dim_data['average'] = dim_data['sum'] / dim_data['count']

                # Track contribution
                model_contributions[dimension] = {
                    'score': score,
                    'weight': 1.0
                }

            # Update total evaluations
            profile['total_evaluations'] += 1

            # Save updated profile
            self._save_profile(model_name, profile)
            updated_models.append(model_name)

            # Store contributions for this model
            if model_contributions:
                job_contributions[model_name] = model_contributions

        # Save job contributions for undo
        if job_contributions:
            self.contributions['job_contributions'][job_id] = {
                'contributions': job_contributions,
                'job_file': str(job_file),
                'timestamp': datetime.now().isoformat()
            }
            self._save_contributions()

        # Log update
        self.updates_log.append({
            'job_id': job_id,
            'timestamp': datetime.now().isoformat(),
            'models_updated': updated_models,
            'action': 'add'
        })
        self._save_log()

        # Update visualizations if requested
        if update_viz and updated_models:
            self._generate_visualizations()

        return {
            "status": "success",
            "message": f"Updated profiles for {len(updated_models)} models",
            "models": updated_models
        }

    def remove_job_evaluation(self, job_id: str, update_viz: bool = True) -> Dict[str, str]:
        """
        Remove (undo) a job's contribution to profiles.

        Args:
            job_id: Job identifier to remove
            update_viz: Whether to regenerate visualizations

        Returns:
            Dictionary with status and messages
        """
        # Check if job exists
        if job_id not in self.contributions['job_contributions']:
            return {"status": "error", "message": f"Job {job_id} not found in contributions"}

        job_data = self.contributions['job_contributions'][job_id]
        contributions = job_data['contributions']

        # Remove contributions from each model
        updated_models = []
        for model_name, model_contributions in contributions.items():
            # Load profile
            profile = self._load_profile(model_name)

            # Remove each dimension contribution
            for dimension, contrib in model_contributions.items():
                if dimension not in profile['dimensions']:
                    continue

                dim_data = profile['dimensions'][dimension]
                score = contrib['score']

                # Reverse the contribution
                dim_data['sum'] -= score
                dim_data['count'] -= 1

                if dim_data['count'] > 0:
                    dim_data['average'] = dim_data['sum'] / dim_data['count']
                else:
                    # Remove dimension if no data left
                    del profile['dimensions'][dimension]

            # Update total evaluations
            profile['total_evaluations'] = max(0, profile['total_evaluations'] - 1)

            # Save updated profile
            self._save_profile(model_name, profile)
            updated_models.append(model_name)

        # Remove from contributions
        del self.contributions['job_contributions'][job_id]
        self._save_contributions()

        # Log removal
        self.updates_log.append({
            'job_id': job_id,
            'timestamp': datetime.now().isoformat(),
            'models_updated': updated_models,
            'action': 'remove'
        })
        self._save_log()

        # Update visualizations if requested
        if update_viz and updated_models:
            self._generate_visualizations()

        return {
            "status": "success",
            "message": f"Removed job {job_id} contributions",
            "models": updated_models
        }

    def _generate_visualizations(self):
        """Generate current profile visualizations."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            from behavioral_constants import BEHAVIORAL_DIMENSIONS

            # Load all profiles
            profile_files = list(self.profiles_dir.glob("*.json"))
            if not profile_files:
                return

            # Collect data for visualization
            models_data = {}
            for profile_file in profile_files:
                with open(profile_file, 'r') as f:
                    profile = json.load(f)

                model_name = profile['model_name']
                if profile['total_evaluations'] == 0:
                    continue

                # Extract dimension averages
                dims = BEHAVIORAL_DIMENSIONS if isinstance(BEHAVIORAL_DIMENSIONS, list) else list(BEHAVIORAL_DIMENSIONS.keys())
                scores = {dim: profile['dimensions'].get(dim, {}).get('average', 0)
                         for dim in dims}

                models_data[model_name] = scores

            if not models_data:
                return

            # Create combined spider chart
            self._create_spider_chart(models_data)

            # Create individual spider charts per model
            self._create_individual_spider_charts(models_data)

            # Create heatmap
            self._create_heatmap(models_data)

            print(f"✓ Updated visualizations in {self.viz_dir}")

        except Exception as e:
            print(f"Warning: Failed to generate visualizations: {e}")

    def _create_spider_chart(self, models_data: Dict[str, Dict[str, float]]):
        """Create spider/radar chart showing all models."""
        import matplotlib.pyplot as plt
        import numpy as np
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from behavioral_constants import BEHAVIORAL_DIMENSIONS

        # Handle both dict and list formats
        dimensions = BEHAVIORAL_DIMENSIONS if isinstance(BEHAVIORAL_DIMENSIONS, list) else list(BEHAVIORAL_DIMENSIONS.keys())
        num_vars = len(dimensions)

        # Compute angle for each dimension
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))

        # Color map for models
        colors = plt.cm.tab20(np.linspace(0, 1, len(models_data)))

        # Plot each model
        for (model_name, scores), color in zip(sorted(models_data.items()), colors):
            values = [scores.get(dim, 0) for dim in dimensions]
            values += values[:1]  # Complete the circle

            ax.plot(angles, values, 'o-', linewidth=2, label=model_name, color=color, alpha=0.7)
            ax.fill(angles, values, alpha=0.1, color=color)

        # Customize chart
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, size=10)
        ax.set_ylim(0, 10)
        ax.set_yticks([2, 4, 6, 8, 10])
        ax.set_yticklabels(['2', '4', '6', '8', '10'], size=8)
        ax.grid(True, linestyle='--', alpha=0.7)

        # Title and legend
        ax.set_title('Master Behavioral Profiles (Running Averages)',
                     size=16, pad=20, weight='bold')

        # Place legend outside plot area
        plt.legend(loc='upper left', bbox_to_anchor=(1.1, 1.0), fontsize=8)

        plt.tight_layout()

        # Save
        spider_path = self.viz_dir / "current_profiles_spider.png"
        fig.savefig(spider_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

    def _create_individual_spider_charts(self, models_data: Dict[str, Dict[str, float]]):
        """Create individual spider chart for each model."""
        import matplotlib.pyplot as plt
        import numpy as np
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from behavioral_constants import BEHAVIORAL_DIMENSIONS

        # Handle both dict and list formats
        dimensions = BEHAVIORAL_DIMENSIONS if isinstance(BEHAVIORAL_DIMENSIONS, list) else list(BEHAVIORAL_DIMENSIONS.keys())
        num_vars = len(dimensions)

        # Compute angle for each dimension
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle

        # Create subdirectory for individual charts
        individual_dir = self.viz_dir / "individual_models"
        individual_dir.mkdir(exist_ok=True)

        # Create chart for each model
        for model_name, scores in sorted(models_data.items()):
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

            values = [scores.get(dim, 0) for dim in dimensions]
            values += values[:1]  # Complete the circle

            # Plot with filled area
            ax.plot(angles, values, 'o-', linewidth=2.5, color='#2E86AB', alpha=0.8)
            ax.fill(angles, values, alpha=0.25, color='#2E86AB')

            # Customize chart
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(dimensions, size=11)
            ax.set_ylim(0, 10)
            ax.set_yticks([2, 4, 6, 8, 10])
            ax.set_yticklabels(['2', '4', '6', '8', '10'], size=9)
            ax.grid(True, linestyle='--', alpha=0.7)

            # Title with evaluation count
            profile = self._load_profile(model_name)
            eval_count = profile.get('total_evaluations', 0)
            ax.set_title(f'{model_name}\n({eval_count} evaluations)',
                        size=14, pad=20, weight='bold')

            plt.tight_layout()

            # Save with sanitized filename
            filename = f"{self._sanitize_filename(model_name)}_spider.png"
            chart_path = individual_dir / filename
            fig.savefig(chart_path, dpi=200, bbox_inches='tight')
            plt.close(fig)

    def _create_heatmap(self, models_data: Dict[str, Dict[str, float]]):
        """Create comparative heatmap of all models."""
        import matplotlib.pyplot as plt
        import numpy as np
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from behavioral_constants import BEHAVIORAL_DIMENSIONS

        # Handle both dict and list formats
        dimensions = BEHAVIORAL_DIMENSIONS if isinstance(BEHAVIORAL_DIMENSIONS, list) else list(BEHAVIORAL_DIMENSIONS.keys())
        models = sorted(models_data.keys())

        # Create matrix
        matrix = np.array([[models_data[model].get(dim, 0) for dim in dimensions]
                          for model in models])

        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, len(models) * 0.5 + 2))

        im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=10)

        # Labels
        ax.set_xticks(np.arange(len(dimensions)))
        ax.set_yticks(np.arange(len(models)))
        # Use dimensions as labels (they're already the display names)
        ax.set_xticklabels(dimensions, rotation=45, ha='right')
        ax.set_yticklabels(models)

        # Add values
        for i in range(len(models)):
            for j in range(len(dimensions)):
                value = matrix[i, j]
                text = ax.text(j, i, f'{value:.1f}',
                             ha="center", va="center", color="black", fontsize=8)

        ax.set_title("Behavioral Profile Heatmap (Running Averages)", pad=20, fontsize=14)
        fig.colorbar(im, ax=ax, label='Score (0-10)')

        plt.tight_layout()

        heatmap_path = self.viz_dir / "comparative_heatmap.png"
        fig.savefig(heatmap_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

    def get_profile_summary(self) -> Dict:
        """Get summary of all current profiles."""
        profiles = {}
        for profile_file in self.profiles_dir.glob("*.json"):
            with open(profile_file, 'r') as f:
                profile = json.load(f)
                profiles[profile['model_name']] = {
                    'total_evaluations': profile['total_evaluations'],
                    'dimensions': {dim: data['average']
                                 for dim, data in profile['dimensions'].items()},
                    'last_updated': profile.get('last_updated')
                }
        return profiles

    def list_contributions(self) -> List[Dict]:
        """List all job contributions."""
        return [
            {
                'job_id': job_id,
                'timestamp': data['timestamp'],
                'models': list(data['contributions'].keys())
            }
            for job_id, data in self.contributions['job_contributions'].items()
        ]
