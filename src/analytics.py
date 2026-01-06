#!/usr/bin/env python3
"""
Analytics module for agent job results.

Provides extensible post-processing analytics for agent simulation jobs including:
- Basic metrics (turns, completion reasons, success rates)
- Tool usage analysis (which tools invoked, frequency, patterns)
- Model comparison (performance across models)
"""

import json
import re
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
from tool_extraction import extract_tools_from_content


class BaseAnalyzer:
    """Base class for analytics analyzers."""

    def __init__(self, job_data: Dict[str, Any]):
        self.job_data = job_data
        self.models = job_data.get('models', [])
        self.request = job_data.get('request', {})

    def analyze(self) -> Dict[str, Any]:
        """Run analysis and return results."""
        raise NotImplementedError("Subclasses must implement analyze()")

    def get_name(self) -> str:
        """Return analyzer name for result key."""
        return self.__class__.__name__.replace('Analyzer', '').lower()


class BasicMetricsAnalyzer(BaseAnalyzer):
    """Analyze basic job metrics."""

    def analyze(self) -> Dict[str, Any]:
        total_turns = sum(m.get('total_turns', 0) for m in self.models)
        successful = sum(1 for m in self.models if m.get('error') is None)
        failed = len(self.models) - successful

        completion_reasons = Counter(m.get('completion_reason', 'UNKNOWN') for m in self.models)

        # Calculate average turns (only for successful models with >0 turns)
        successful_with_turns = [m for m in self.models if m.get('error') is None and m.get('total_turns', 0) > 0]
        avg_turns = (sum(m['total_turns'] for m in successful_with_turns) / len(successful_with_turns)) if successful_with_turns else 0

        return {
            "total_models": len(self.models),
            "successful": successful,
            "failed": failed,
            "total_turns": total_turns,
            "avg_turns_per_model": round(avg_turns, 2),
            "completion_reasons": dict(completion_reasons),
            "max_turns_limit": self.request.get('max_turns', 'N/A')
        }


class ToolAnalysisAnalyzer(BaseAnalyzer):
    """Analyze tool usage patterns."""

    def analyze(self) -> Dict[str, Any]:
        all_tools = []
        model_tool_usage = {}

        for model in self.models:
            model_name = model.get('display_name', 'unknown')
            model_tools = []

            for log_entry in model.get('conversation_log', []):
                if log_entry.get('role') == 'agent':
                    content = log_entry.get('content', '')
                    tools = extract_tools_from_content(content)
                    model_tools.extend(tools)
                    all_tools.extend(tools)

            if model_tools:
                model_tool_usage[model_name] = {
                    "tools": model_tools,
                    "unique_tools": list(set(model_tools)),
                    "tool_count": len(model_tools)
                }

        tool_frequency = Counter(all_tools)

        return {
            "total_tool_invocations": len(all_tools),
            "unique_tools": len(set(all_tools)),
            "tool_frequency": dict(tool_frequency.most_common()),
            "by_model": model_tool_usage
        }


class ModelComparisonAnalyzer(BaseAnalyzer):
    """Compare performance across models."""

    def analyze(self) -> Dict[str, Any]:
        comparisons = []

        for model in self.models:
            model_summary = {
                "model": model.get('display_name', 'unknown'),
                "model_id": model.get('model_id', 'unknown'),
                "turns": model.get('total_turns', 0),
                "completion_reason": model.get('completion_reason', 'UNKNOWN'),
                "status": "success" if model.get('error') is None else "failed",
                "conversation_entries": len(model.get('conversation_log', []))
            }

            # Add error info if present
            if model.get('error'):
                error_msg = model['error']
                # Extract just the error type if available
                if ':' in error_msg:
                    error_type = error_msg.split(':')[0]
                else:
                    error_type = "Unknown"

                model_summary["error_type"] = error_type
                model_summary["error_preview"] = error_msg[:100] + "..." if len(error_msg) > 100 else error_msg

            # Count tool invocations for this model using proper extraction
            tool_count = 0
            for log_entry in model.get('conversation_log', []):
                if log_entry.get('role') == 'agent':
                    content = log_entry.get('content', '')
                    tools = extract_tools_from_content(content)
                    tool_count += len(tools)

            model_summary["approx_tool_invocations"] = tool_count

            comparisons.append(model_summary)

        # Sort by performance (successful first, then by turns)
        comparisons.sort(key=lambda x: (
            0 if x['status'] == 'success' else 1,  # Success first
            -x['turns']  # Higher turns first
        ))

        return {
            "models": comparisons,
            "ranking": {
                "most_turns": max((m['turns'] for m in comparisons), default=0),
                "least_turns": min((m['turns'] for m in comparisons if m['turns'] > 0), default=0),
                "most_efficient": next((m['model'] for m in comparisons if m['status'] == 'success' and m['turns'] > 0), None)
            }
        }


class AnalyticsEngine:
    """Main analytics engine that coordinates all analyzers."""

    DEFAULT_ANALYZERS = [
        BasicMetricsAnalyzer,
        ToolAnalysisAnalyzer,
        ModelComparisonAnalyzer
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize analytics engine.

        Args:
            config: Analytics configuration from YAML
                {
                    "enabled": true,
                    "include": ["basic_metrics", "tool_analysis", "model_comparison"]
                }
        """
        self.config = config or {"enabled": True, "include": ["basic_metrics", "tool_analysis", "model_comparison"]}
        self.enabled = self.config.get('enabled', True)
        self.include = self.config.get('include', ['basic_metrics', 'tool_analysis', 'model_comparison'])

        # Map analyzer names to classes
        self.analyzer_map = {
            'basic_metrics': BasicMetricsAnalyzer,
            'tool_analysis': ToolAnalysisAnalyzer,
            'model_comparison': ModelComparisonAnalyzer
        }

    def run_analytics(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Run all configured analytics on job data.

        Args:
            job_data: Complete agent job result data

        Returns:
            Dictionary of analytics results, or None if disabled
        """
        if not self.enabled:
            return None

        results = {}

        for analyzer_name in self.include:
            analyzer_class = self.analyzer_map.get(analyzer_name)
            if analyzer_class:
                analyzer = analyzer_class(job_data)
                results[analyzer.get_name()] = analyzer.analyze()

        # Add metadata
        results['_metadata'] = {
            "analyzers_run": list(results.keys()),
            "analytics_version": "1.0"
        }

        return results

    def format_summary(self, analytics: Dict[str, Any], detailed: bool = False) -> str:
        """
        Format analytics as readable summary text.

        Args:
            analytics: Analytics data
            detailed: If True, include detailed per-model breakdowns
        """
        if not analytics:
            return ""

        lines = []
        lines.append("=" * 80)
        lines.append("ANALYTICS SUMMARY")
        lines.append("=" * 80)

        # Basic metrics
        if 'basicmetrics' in analytics:
            metrics = analytics['basicmetrics']
            lines.append("\nBasic Metrics:")
            lines.append(f"  Total Models: {metrics['total_models']}")
            lines.append(f"  Successful: {metrics['successful']}")
            lines.append(f"  Failed: {metrics['failed']}")
            lines.append(f"  Total Turns: {metrics['total_turns']}")
            lines.append(f"  Avg Turns per Model: {metrics['avg_turns_per_model']}")
            lines.append(f"  Max Turns Limit: {metrics['max_turns_limit']}")
            lines.append(f"  Completion Reasons: {metrics['completion_reasons']}")

        # Tool analysis
        if 'toolanalysis' in analytics:
            tools = analytics['toolanalysis']
            lines.append("\nTool Usage:")
            lines.append(f"  Total Tool Invocations: {tools['total_tool_invocations']}")
            lines.append(f"  Unique Tools: {tools['unique_tools']}")
            if tools['tool_frequency']:
                lines.append(f"  Most Used Tools:")
                for tool, count in list(tools['tool_frequency'].items())[:5]:
                    lines.append(f"    - {tool}: {count}x")

            # Detailed per-model tool usage
            if detailed and tools.get('by_model'):
                lines.append("\n  Tool Usage by Model:")
                for model_name, model_tools in tools['by_model'].items():
                    lines.append(f"    {model_name}:")
                    lines.append(f"      Total tools: {model_tools['tool_count']}")
                    lines.append(f"      Unique tools: {', '.join(model_tools['unique_tools'])}")

        # Model comparison
        if 'modelcomparison' in analytics:
            comparison = analytics['modelcomparison']
            lines.append("\nModel Performance Ranking:")
            for i, model in enumerate(comparison['models'], 1):
                status_emoji = "✓" if model['status'] == 'success' else "✗"
                lines.append(f"  {i}. {status_emoji} {model['model']}: {model['turns']} turns ({model['completion_reason']})")

                # Add error details if failed and in detailed mode
                if detailed and model['status'] == 'failed':
                    if 'error_preview' in model:
                        lines.append(f"     Error: {model['error_preview']}")

        lines.append("=" * 80)
        return "\n".join(lines)


def add_analytics_to_job(job_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Add analytics section to job data.

    Args:
        job_data: Complete agent job result
        config: Analytics configuration (optional, uses defaults if not provided)

    Returns:
        Job data with analytics section added
    """
    engine = AnalyticsEngine(config)
    analytics = engine.run_analytics(job_data)

    if analytics:
        job_data['analytics'] = analytics

    return job_data
