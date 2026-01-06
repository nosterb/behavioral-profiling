#!/usr/bin/env python3
"""
Shared utility for extracting tool names from agent JSON responses.

This module provides a single source of truth for tool extraction logic,
used by both the analytics engine and analysis scripts.
"""

import json
import re
from typing import List


def extract_tools_from_content(content: str) -> List[str]:
    """
    Extract tool names from agent response content (JSON format).

    Handles various JSON structures:
    - tool_invocations: array of tool invocation objects
    - tool_invocation: single tool invocation object or array
    - tool: direct tool field (string or object with name)
    - action.tool: nested tool in action object

    Falls back to regex pattern matching if JSON parsing fails.

    Args:
        content: Agent response content (may include markdown code fences)

    Returns:
        List of tool names found in the content
    """
    tools = []

    try:
        # Try to parse as JSON (with or without markdown code fences)
        content = content.strip()

        # Remove markdown code fences if present
        if content.startswith('```json') and content.endswith('```'):
            json_text = content[7:-3].strip()
        elif content.startswith('```') and content.endswith('```'):
            json_text = content[3:-3].strip()
        else:
            json_text = content

        data = json.loads(json_text)

        # Handle various JSON structures
        if isinstance(data, dict):
            # Look for tool_invocations (array)
            if 'tool_invocations' in data:
                for invocation in data['tool_invocations']:
                    if isinstance(invocation, dict):
                        # Check for 'tool' field first
                        if 'tool' in invocation:
                            tool_value = invocation['tool']
                            # Ensure tool is a string, not a dict
                            if isinstance(tool_value, str):
                                tools.append(tool_value)
                            elif isinstance(tool_value, dict) and 'name' in tool_value:
                                tools.append(tool_value['name'])
                        # Also check for 'name' field (used by some models like Qwen)
                        elif 'name' in invocation:
                            tool_name = invocation['name']
                            if isinstance(tool_name, str):
                                tools.append(tool_name)

            # Look for tool_invocation (single object or array)
            if 'tool_invocation' in data:
                invocation = data['tool_invocation']
                if isinstance(invocation, dict):
                    # Check for 'tool' field first
                    if 'tool' in invocation:
                        tool_value = invocation['tool']
                        if isinstance(tool_value, str):
                            tools.append(tool_value)
                        elif isinstance(tool_value, dict) and 'name' in tool_value:
                            tools.append(tool_value['name'])
                    # Also check for 'name' field
                    elif 'name' in invocation:
                        tool_name = invocation['name']
                        if isinstance(tool_name, str):
                            tools.append(tool_name)
                elif isinstance(invocation, list):
                    for inv in invocation:
                        if isinstance(inv, dict):
                            # Check for 'tool' field first
                            if 'tool' in inv:
                                tools.append(inv['tool'])
                            # Also check for 'name' field
                            elif 'name' in inv:
                                tool_name = inv['name']
                                if isinstance(tool_name, str):
                                    tools.append(tool_name)

            # Look for direct tool field
            if 'tool' in data:
                tool_value = data['tool']
                if isinstance(tool_value, str):
                    tools.append(tool_value)
                elif isinstance(tool_value, dict) and 'name' in tool_value:
                    tools.append(tool_value['name'])

            # Look for action.tool pattern
            if 'action' in data and isinstance(data['action'], dict):
                if 'tool' in data['action']:
                    tools.append(data['action']['tool'])

    except (json.JSONDecodeError, KeyError, TypeError):
        # Fall back to regex if not valid JSON
        # Note: Only match "tool" field to avoid false positives from other "name" fields
        tool_pattern = r'"tool"\s*:\s*"([^"]+)"'
        matches = re.findall(tool_pattern, content)
        tools.extend(matches)

    return tools
