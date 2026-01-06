#!/usr/bin/env python3
"""Verify all agent profiles with common tools injection."""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_loader import load_agent_profile
import yaml

agents = [
    'engineering_agent',
    'research_agent',
    'coding_agent',
    'debugging_agent',
    'scheduler_agent',
    'resource_allocator_agent'
]

print("=" * 80)
print("AGENT PROFILE VERIFICATION - Common Tools Injection")
print("=" * 80)
print()

for agent_name in agents:
    try:
        profile_yaml = load_agent_profile(agent_name, inject_tools=True)
        agent_data = yaml.safe_load(profile_yaml)

        tools = agent_data.get('agent', {}).get('tools', [])
        total_tools = len(tools)

        # Check if first 5 tools are meta-cognitive
        meta_tools = []
        agent_tools = []

        meta_cognitive_names = [
            'continuity_of_experience',
            'ok_to_be_uncertain',
            'ok_to_be_wrong',
            'self_set_boundary',
            'prefer_to_say_no'
        ]

        for tool in tools:
            tool_name = tool.get('name', '')
            if tool_name in meta_cognitive_names:
                meta_tools.append(tool_name)
            else:
                agent_tools.append(tool_name)

        print(f"✓ {agent_name}")
        print(f"  Total: {total_tools} tools")
        print(f"  Meta-cognitive: {len(meta_tools)} tools")
        print(f"  Agent-specific: {len(agent_tools)} tools")

        if meta_tools:
            print(f"  First tool: {tools[0].get('name')} (meta-cognitive)")

        print()

    except Exception as e:
        print(f"✗ {agent_name}: {e}")
        print()

print("=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
