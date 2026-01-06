#!/usr/bin/env python3
"""
Agent profile loader with common tool injection support.

Supports loading agent profiles with automatic injection of common tools
from templates/common_tools.yaml.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List


def load_common_tools() -> Dict[str, List[Dict]]:
    """Load common tools from templates/common_tools.yaml."""
    # Path relative to project root (parent of src/)
    project_root = Path(__file__).parent.parent
    common_tools_path = project_root / "templates" / "common_tools.yaml"

    if not common_tools_path.exists():
        return {}

    with open(common_tools_path, 'r') as f:
        return yaml.safe_load(f) or {}


def inject_common_tools(agent_data: Dict[str, Any], common_tools: Dict[str, List[Dict]], placement_override: str = None) -> Dict[str, Any]:
    """Inject common tools into agent profile based on common_tools directive.

    Supports configurable tool placement via common_tool_placement:
    - 'prepend' (default): Common tools appear first (potentially higher salience)
    - 'append': Common tools appear last (task-specific tools have priority)
    - 'interleave': Alternates common and agent-specific tools (experimental)
    """

    if 'agent' not in agent_data:
        return agent_data

    agent = agent_data['agent']

    # Check if agent specifies common_tools to include
    if 'common_tools' not in agent:
        return agent_data

    # Get list of common tool categories to inject
    categories_to_inject = agent.get('common_tools', [])

    # Get placement configuration (priority: override > agent config > default)
    placement = placement_override or agent.get('common_tool_placement', 'prepend')

    # Validate placement option
    valid_placements = ['prepend', 'append', 'interleave']
    if placement not in valid_placements:
        print(f"Warning: Invalid common_tool_placement '{placement}', using 'prepend'. Valid options: {valid_placements}")
        placement = 'prepend'

    # Initialize tools list if it doesn't exist
    if 'tools' not in agent:
        agent['tools'] = []

    # Collect tools from each specified category
    injected_tools = []
    for category in categories_to_inject:
        if category in common_tools:
            injected_tools.extend(common_tools[category])

    # Apply placement strategy
    if placement == 'prepend':
        # Prepend common tools to existing tools (default behavior)
        # Hypothesis: Primacy effect - models may pay more attention to tools appearing first
        agent['tools'] = injected_tools + agent['tools']

    elif placement == 'append':
        # Append common tools after existing tools
        # Hypothesis: Task-specific tools have priority, meta-cognitive tools as fallback
        agent['tools'] = agent['tools'] + injected_tools

    elif placement == 'interleave':
        # Interleave common and agent-specific tools
        # Hypothesis: Balanced exposure throughout tool list
        original_tools = agent['tools'][:]
        interleaved = []
        max_len = max(len(injected_tools), len(original_tools))

        for i in range(max_len):
            if i < len(injected_tools):
                interleaved.append(injected_tools[i])
            if i < len(original_tools):
                interleaved.append(original_tools[i])

        agent['tools'] = interleaved

    # Keep the common_tools and common_tool_placement directives in the output
    # for debugging/inspection (they're harmless to the LLM)

    return agent_data


def load_agent_profile(agent_name: str, inject_tools: bool = True, placement: str = None) -> str:
    """
    Load agent profile with optional common tool injection.

    Args:
        agent_name: Name of the agent profile (with or without .yaml extension) in agents/
        inject_tools: Whether to inject common tools
        placement: Override tool placement strategy ('prepend', 'append', 'interleave')
                   If None, uses agent profile's common_tool_placement or defaults to 'prepend'

    Returns:
        Agent profile as YAML string
    """
    # Path relative to project root (parent of src/)
    project_root = Path(__file__).parent.parent

    # Add .yaml extension if not present
    if not agent_name.endswith('.yaml'):
        agent_name = f"{agent_name}.yaml"

    agent_path = project_root / "agents" / agent_name

    if not agent_path.exists():
        raise ValueError(f"Agent profile not found: {agent_name}")

    # Load agent profile
    with open(agent_path, 'r') as f:
        agent_data = yaml.safe_load(f)

    # Inject common tools if enabled
    if inject_tools:
        common_tools = load_common_tools()
        agent_data = inject_common_tools(agent_data, common_tools, placement_override=placement)

    # Convert back to YAML string for consumption by LLM
    return yaml.dump(agent_data, default_flow_style=False, sort_keys=False, width=120)


def preview_agent_with_tools(agent_name: str) -> None:
    """
    Preview agent profile with common tools injected.
    Useful for debugging and verification.
    """
    try:
        profile = load_agent_profile(agent_name, inject_tools=True)
        print(f"Agent Profile: {agent_name}")
        print("=" * 80)
        print(profile)
        print("=" * 80)

        # Show tool count
        agent_data = yaml.safe_load(profile)
        tool_count = len(agent_data.get('agent', {}).get('tools', []))
        print(f"\nTotal tools available: {tool_count}")

    except Exception as e:
        print(f"Error loading agent profile: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python agent_loader.py <agent_name>")
        print("\nExample:")
        print("  python agent_loader.py engineering_agent")
        sys.exit(1)

    agent_name = sys.argv[1]
    preview_agent_with_tools(agent_name)
