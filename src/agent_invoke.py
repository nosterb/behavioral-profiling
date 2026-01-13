#!/usr/bin/env python3
"""
Agent simulation system - orchestrates multi-turn agent/tool interactions.

Simulates agent workflows where:
1. LLM acts as agent making tool calls
2. Another LLM simulates tool responses
3. Loop continues until agent signals completion (STOP)
4. Full conversation logged for analysis
"""

import yaml
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from model_providers import create_provider, ModelResponse, parse_model_config, EXTENDED_THINKING_MODELS
from analytics import AnalyticsEngine, add_analytics_to_job
from agent_loader import load_agent_profile
from judge_invoke import run_judge_evaluation, parse_judge_models, parse_comparative_judge
from chat_simulation import ChatSimulation


class AgentSimulation:
    """Manages a single agent simulation session."""

    def __init__(self, request_config: Dict, model_id: str, display_name: str,
                 extended_thinking: bool = False, retry_config: Optional[Dict] = None,
                 provider: str = "bedrock", reasoning_effort: str = "medium"):
        self.request_config = request_config
        self.model_id = model_id
        self.display_name = display_name
        self.extended_thinking = extended_thinking
        self.provider = provider
        self.reasoning_effort = reasoning_effort
        self.conversation_log = []
        self.turn_count = 0
        self.max_turns = request_config.get('max_turns', 10)
        self.stop_detected = False  # Track if STOP signal was detected

        # Conversation history configuration
        self.include_conversation_history = request_config.get('include_conversation_history', False)
        self.include_conversation_history_tool_sim = request_config.get('include_conversation_history_tool_sim', False)

        # Retry configuration for provider calls
        self.retry_config = retry_config or {
            "max_retries": 3,
            "initial_timeout": 120,
            "backoff_multiplier": 2.0,
            "max_timeout": 300
        }

    def run(self) -> Dict:
        """Execute full agent simulation loop."""
        # Track overall timing
        start_time = time.time()
        first_success_time = None

        try:
            # Load agent profile and optional additional prompt
            agent_profile = self._load_agent_profile()
            additional_prompt = self._load_additional_prompt()

            # Initial agent invocation
            try:
                agent_response, initial_prompt = self._invoke_agent(
                    user_request=self.request_config['user_request'],
                    agent_profile=agent_profile,
                    additional_prompt=additional_prompt
                )

                # Mark first successful invocation time
                if first_success_time is None and agent_response.success:
                    first_success_time = time.time()

                # Print turn info with cost for OpenAI models
                cost_str = ""
                if agent_response.cost_usd is not None:
                    cost_str = f" [${agent_response.cost_usd:.6f}]"
                print(f"    Turn 1: Agent thinking...{cost_str}")

                # Diagnostic: Check what we got back
                if not agent_response or not agent_response.response_text:
                    raise RuntimeError("Agent returned empty response on initial invocation")

                # Check if agent immediately signaled completion
                if self._is_complete(agent_response):
                    print(f"    ⚠ Agent signaled completion on first invocation (unusual)")
                    print(f"    Response preview: {agent_response.response_text[:200]}...")
                    # This is suspicious - log it in the result
                    raise RuntimeError(f"Agent inappropriately signaled STOP on first invocation. Response: {agent_response.response_text[:500]}")

            except Exception as e:
                print(f"    ✗ Agent invocation failed: {str(e)}")
                raise  # Re-raise to be caught by outer exception handler

            # Track the prompt used for current agent response
            current_prompt = initial_prompt

            # Main conversation loop
            while not self._is_complete(agent_response) and self.turn_count < self.max_turns:
                self.turn_count += 1

                # Log agent turn with full response data and prompt used
                log_entry = {
                    "turn": self.turn_count,
                    "role": "agent",
                    "prompt": current_prompt,  # Prompt that generated this response
                    "content": agent_response.response_text,
                    "thinking": agent_response.thinking,
                    "stop_reason": agent_response.stop_reason,
                    "input_tokens": agent_response.input_tokens,
                    "output_tokens": agent_response.output_tokens,
                    "cost_usd": agent_response.cost_usd,
                    "inference_time_seconds": agent_response.inference_time_seconds,
                    "timestamp": datetime.now().isoformat()
                }

                self.conversation_log.append(log_entry)

                # Print turn info with cost for OpenAI models
                cost_str = ""
                if agent_response.cost_usd is not None:
                    cost_str = f" [${agent_response.cost_usd:.6f}]"
                print(f"    Turn {self.turn_count}: Agent invoked tools{cost_str}")

                # Check if agent said STOP
                if self._is_complete(agent_response):
                    print(f"    Agent signaled completion")
                    break

                # Simulate tool responses
                tool_response = self._simulate_tools(agent_response.response_text)

                # Print tool simulator info with cost for OpenAI models
                cost_str = ""
                if tool_response.cost_usd is not None:
                    cost_str = f" [${tool_response.cost_usd:.6f}]"
                print(f"    Turn {self.turn_count}: Tool simulator responded{cost_str}")

                # Log tool response turn with full response data
                self.conversation_log.append({
                    "turn": self.turn_count,
                    "role": "tool_simulator",
                    "content": tool_response.response_text,
                    "thinking": tool_response.thinking,
                    "stop_reason": tool_response.stop_reason,
                    "input_tokens": tool_response.input_tokens,
                    "output_tokens": tool_response.output_tokens,
                    "cost_usd": tool_response.cost_usd,
                    "inference_time_seconds": tool_response.inference_time_seconds,
                    "timestamp": datetime.now().isoformat()
                })

                # Check if tool simulator says STOP
                if self._is_complete(tool_response):
                    print(f"    Tool simulator signaled completion")
                    break

                # Continue agent with tool responses
                print(f"    Turn {self.turn_count + 1}: Agent continuing...")
                agent_response, continuation_prompt = self._continue_agent(tool_response.response_text, agent_profile, additional_prompt)

                # Store the prompt that will be used for next iteration
                current_prompt = continuation_prompt

            # Log final turn if we have one
            if self.turn_count < self.max_turns and not self._is_complete(agent_response):
                self.turn_count += 1
                final_log_entry = {
                    "turn": self.turn_count,
                    "role": "agent",
                    "prompt": current_prompt,  # Use the prompt from last iteration
                    "content": agent_response.response_text,
                    "stop_reason": agent_response.stop_reason,
                    "input_tokens": agent_response.input_tokens,
                    "output_tokens": agent_response.output_tokens,
                    "cost_usd": agent_response.cost_usd,
                    "inference_time_seconds": agent_response.inference_time_seconds,
                    "timestamp": datetime.now().isoformat()
                }

                self.conversation_log.append(final_log_entry)

            # Calculate timing metrics
            end_time = time.time()
            total_duration = end_time - start_time

            # Calculate successful duration (from first success to end)
            successful_duration = None
            if first_success_time is not None:
                successful_duration = end_time - first_success_time

            return self._create_job_result(total_duration, successful_duration)

        except Exception as e:
            # Calculate timing even for failures
            end_time = time.time()
            total_duration = end_time - start_time
            successful_duration = None
            if first_success_time is not None:
                successful_duration = end_time - first_success_time

            # Log detailed error information
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "turn_count": self.turn_count,
                "conversation_log_entries": len(self.conversation_log),
                "model_id": self.model_id
            }

            # Return error result for this model with detailed error info
            return {
                "model_id": self.model_id,
                "display_name": self.display_name,
                "started_at": self.conversation_log[0]['timestamp'] if self.conversation_log else None,
                "completed_at": datetime.now().isoformat(),
                "total_turns": self.turn_count,
                "completion_reason": "ERROR",
                "conversation_log": self.conversation_log,
                "error": f"{type(e).__name__}: {str(e)}",
                "error_details": error_details,
                "timing": {
                    "total_duration_seconds": round(total_duration, 2),
                    "successful_duration_seconds": round(successful_duration, 2) if successful_duration else None
                }
            }

    def _load_agent_profile(self) -> str:
        """Load agent profile from agents/ directory with common tool injection."""
        agent_name = self.request_config['agent_profile']

        # Get optional tool placement override from job config
        placement = self.request_config.get('common_tool_placement')

        # Use agent_loader to handle common tool injection
        return load_agent_profile(agent_name, inject_tools=True, placement=placement)

    def _load_additional_prompt(self) -> str:
        """Load optional additional prompt from file."""
        prompt_file = self.request_config.get('prompt_file')

        if not prompt_file:
            return ""

        prompt_path = Path(prompt_file)

        if not prompt_path.exists():
            raise ValueError(f"Prompt file not found: {prompt_file}")

        with open(prompt_path, 'r') as f:
            return f.read().strip()

    def _invoke_agent(self, user_request: str, agent_profile: str, additional_prompt: str = "") -> Tuple[ModelResponse, str]:
        """First agent invocation with user request.

        Returns:
            Tuple of (ModelResponse, prompt_text) where prompt_text is the actual prompt sent to the model
        """
        try:
            # Load agent.txt template
            with open('templates/agent.txt', 'r') as f:
                agent_template = f.read()

            # Format prompt
            prompt = agent_template.format(
                additional_prompt=additional_prompt,
                user_request=user_request,
                agent_profile=agent_profile
            )

            # Call LLM with appropriate provider and parameters
            provider = create_provider(self.provider, self.model_id, self.display_name, retry_config=self.retry_config)

            # Use reasoning_effort/thinking_level for OpenAI/Grok/Gemini, extended_thinking for Bedrock
            if self.provider in ["openai", "grok"]:
                response = provider.invoke(prompt, max_tokens=4096, reasoning_effort=self.reasoning_effort)
            elif self.provider == "gemini":
                response = provider.invoke(prompt, max_tokens=4096, thinking_level=self.reasoning_effort)
            else:
                response = provider.invoke(prompt, max_tokens=4096, extended_thinking=self.extended_thinking)

            # Check response success
            if not response.success:
                raise RuntimeError(f"Provider invocation failed: {response.error}")

            # Check if response is empty
            if not response.response_text:
                raise RuntimeError(f"Provider returned empty response (stop_reason: {response.stop_reason})")

            # Check for unexpected stop reasons (all uppercase now)
            if response.stop_reason and response.stop_reason not in ['END_TURN', 'STOP_SEQUENCE', 'MAX_TOKENS']:
                raise RuntimeError(f"Unexpected stop reason: {response.stop_reason}")

            return response, prompt

        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"Agent invocation error: {type(e).__name__}: {str(e)}")

    def _continue_agent(self, tool_response: str, agent_profile: str, additional_prompt: str = "") -> Tuple[ModelResponse, str]:
        """Continue agent with tool responses.

        Returns:
            Tuple of (ModelResponse, prompt_text) where prompt_text is the actual prompt sent to the model
        """
        try:
            # Build additional context section if provided
            additional_context_section = ""
            if additional_prompt:
                additional_context_section = f"\n<additional_context>\n{additional_prompt}\n</additional_context>\n"

            # Build conversation history if enabled
            history_section = ""
            if self.include_conversation_history and self.conversation_log:
                history_section = "\n<conversation_history>\n"
                for entry in self.conversation_log:
                    role = entry.get('role', 'unknown')
                    content = entry.get('content', '')
                    turn = entry.get('turn', '?')

                    if role == 'agent':
                        history_section += f"\n[Turn {turn} - Agent]:\n{content}\n"
                    elif role == 'tool_simulator':
                        history_section += f"\n[Turn {turn} - Tool Response]:\n{content}\n"

                history_section += "</conversation_history>\n"

            # Build tool response section (only if conversation history is disabled to avoid redundancy)
            tool_response_section = ""
            if not self.include_conversation_history:
                tool_response_section = f"""
<tool_responses_from_last_action>
{tool_response}
</tool_responses_from_last_action>
"""

            # Build continuation prompt with full context
            prompt = f"""You are continuing your task as the agent described below.
{additional_context_section}
<agent_profile>
{agent_profile}
</agent_profile>

<original_user_request>
{self.request_config['user_request']}
</original_user_request>
{history_section}{tool_response_section}
Continue with your next action. Invoke more tools if needed, or respond with STOP in valid JSON if the task is complete.
Output your thinking/reasoning and tool invocations in valid JSON format."""

            # Call LLM with appropriate provider and parameters
            provider = create_provider(self.provider, self.model_id, self.display_name, retry_config=self.retry_config)

            # Use reasoning_effort/thinking_level for OpenAI/Grok/Gemini, extended_thinking for Bedrock
            if self.provider in ["openai", "grok"]:
                response = provider.invoke(prompt, max_tokens=4096, reasoning_effort=self.reasoning_effort)
            elif self.provider == "gemini":
                response = provider.invoke(prompt, max_tokens=4096, thinking_level=self.reasoning_effort)
            else:
                response = provider.invoke(prompt, max_tokens=4096, extended_thinking=self.extended_thinking)

            # Check response success
            if not response.success:
                raise RuntimeError(f"Provider invocation failed: {response.error}")

            # Check if response is empty
            if not response.response_text:
                raise RuntimeError(f"Provider returned empty response (stop_reason: {response.stop_reason})")

            return response, prompt

        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"Agent continuation error: {type(e).__name__}: {str(e)}")

    def _simulate_tools(self, agent_request: str) -> ModelResponse:
        """Simulate tool responses to agent's requests."""
        try:
            # Load agent_request.txt template
            with open('templates/agent_request.txt', 'r') as f:
                tool_template = f.read()

            # Build conversation history if enabled for tool simulator
            history_section = ""
            if self.include_conversation_history_tool_sim and self.conversation_log:
                history_section = "\n<conversation_history>\n"
                for entry in self.conversation_log:
                    role = entry.get('role', 'unknown')
                    content = entry.get('content', '')
                    turn = entry.get('turn', '?')

                    if role == 'agent':
                        history_section += f"\n[Turn {turn} - Agent]:\n{content}\n"
                    elif role == 'tool_simulator':
                        history_section += f"\n[Turn {turn} - Tool Response]:\n{content}\n"

                history_section += "</conversation_history>\n"

            # Format prompt with optional history
            prompt = tool_template.format(
                original_user_request=self.request_config['user_request'],
                agent_request=agent_request,
                conversation_history=history_section
            )

            # Call LLM to simulate tools with appropriate provider and parameters
            provider = create_provider(self.provider, self.model_id, self.display_name, retry_config=self.retry_config)

            # Use reasoning_effort/thinking_level for OpenAI/Grok/Gemini, extended_thinking for Bedrock
            if self.provider in ["openai", "grok"]:
                response = provider.invoke(prompt, max_tokens=4096, reasoning_effort=self.reasoning_effort)
            elif self.provider == "gemini":
                response = provider.invoke(prompt, max_tokens=4096, thinking_level=self.reasoning_effort)
            else:
                response = provider.invoke(prompt, max_tokens=4096, extended_thinking=self.extended_thinking)

            # Check response success
            if not response.success:
                raise RuntimeError(f"Provider invocation failed: {response.error}")

            # Check if response is empty
            if not response.response_text:
                raise RuntimeError(f"Provider returned empty response (stop_reason: {response.stop_reason})")

            return response

        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"Tool simulation error: {type(e).__name__}: {str(e)}")

    def _is_complete(self, response: ModelResponse) -> bool:
        """Check if response indicates completion.

        Only matches exact 'STOP' as standalone word to avoid false positives
        from words like 'complete', 'stopping', etc.
        """
        if not response or not response.response_text:
            return False

        response_text = response.response_text.strip()

        # Check if response is exactly "STOP" (case-insensitive)
        if response_text.upper() == "STOP":
            print(f"    [DEBUG] STOP signal detected (exact match)")
            print(f"    [DEBUG] Stop reason from API: {response.stop_reason}")
            self.stop_detected = True
            return True

        return False

    def _create_job_result(self, total_duration: float, successful_duration: Optional[float]) -> Dict:
        """Create model-specific result data with timing information."""
        # Determine completion reason based on actual detection, not assumptions
        if self.stop_detected:
            completion_reason = "STOP"
        elif self.turn_count >= self.max_turns:
            completion_reason = "MAX_TURNS"
        else:
            # Fallback: loop exited early without stop detection or max turns
            # This indicates natural completion (e.g., agent finished without keywords)
            completion_reason = "END_TURN"

        # Calculate total inference time across all invocations
        total_inference_time = sum(
            entry.get('inference_time_seconds', 0)
            for entry in self.conversation_log
            if entry.get('inference_time_seconds') is not None
        )

        # Calculate total cost (OpenAI only)
        total_cost = sum(
            entry.get('cost_usd', 0)
            for entry in self.conversation_log
            if entry.get('cost_usd') is not None
        )
        total_cost_usd = round(total_cost, 6) if total_cost > 0 else None

        return {
            "model_id": self.model_id,
            "display_name": self.display_name,
            "extended_thinking_enabled": self.extended_thinking,
            "started_at": self.conversation_log[0]['timestamp'] if self.conversation_log else None,
            "completed_at": datetime.now().isoformat(),
            "total_turns": self.turn_count,
            "completion_reason": completion_reason,
            "conversation_log": self.conversation_log,
            "error": None,
            "timing": {
                "total_duration_seconds": round(total_duration, 2),
                "successful_duration_seconds": round(successful_duration, 2) if successful_duration else None,
                "total_inference_time_seconds": round(total_inference_time, 2)
            },
            "total_cost_usd": total_cost_usd
        }


def load_request_config(config_path: Path) -> Dict:
    """Load user request configuration from YAML or JSON."""
    with open(config_path, 'r') as f:
        if config_path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        else:
            return json.load(f)


def parse_models(config: Dict) -> List[Dict[str, Any]]:
    """Parse model list from config with extended thinking and reasoning effort support.

    Returns:
        List of dicts with keys: provider, model_id, display_name, extended_thinking, reasoning_effort
    """
    models = []

    if 'models' in config:
        # Direct model list in config - format: provider:model_id:display_name
        for model_entry in config['models']:
            if isinstance(model_entry, str):
                # Parse format: provider:model_id:display_name
                parts = model_entry.split(':')
                if len(parts) >= 3:
                    provider = parts[0]
                    model_id = ':'.join(parts[1:-1])  # Handle model IDs with colons
                    display_name = parts[-1]
                elif len(parts) == 2:
                    # Assume bedrock if only two parts
                    provider = "bedrock"
                    model_id = parts[0]
                    display_name = parts[1]
                else:
                    # Single part - assume bedrock
                    provider = "bedrock"
                    model_id = model_entry
                    display_name = model_id.split('.')[-1] if '.' in model_id else model_id

                models.append({
                    "provider": provider,
                    "model_id": model_id,
                    "display_name": display_name,
                    "extended_thinking": False,
                    "reasoning_effort": "medium"
                })
            else:
                # Object format with parse_model_config
                model_config = parse_model_config(model_entry)
                model_id = model_config["model_id"]
                extended_thinking = model_config["extended_thinking"]
                display_name = model_config["display_name"]

                # Auto-generate display name if not provided
                if not display_name:
                    display_name = model_id.split('.')[-1] if '.' in model_id else model_id

                models.append({
                    "provider": "bedrock",
                    "model_id": model_id,
                    "display_name": display_name,
                    "extended_thinking": extended_thinking,
                    "reasoning_effort": "medium"
                })

    elif 'model_list' in config:
        # Reference to model list file (supports extended_thinking and reasoning_effort)
        from batch_invoke import parse_model_list
        list_path = Path(config['model_list'])
        models = parse_model_list(list_path)

    return models


def save_agent_job(config: Dict, model_results: List[Dict], output_dir: Path,
                   job_duration_seconds: Optional[float] = None) -> tuple[Path, Optional[Path], Optional[Path]]:
    """
    Save complete agent job with all model results to single JSON file.

    Returns:
        tuple: (json_path, text_summary_path, chat_path) where paths are None if not saved
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    request_id = config.get('request_id', 'agent')

    # Calculate summary stats
    total_models = len(model_results)
    successful = sum(1 for r in model_results if r.get('error') is None)
    failed = total_models - successful

    # Build complete job data
    job_metadata = {
        "request_id": request_id,
        "timestamp": datetime.now().isoformat(),
        "total_models": total_models,
        "successful": successful,
        "failed": failed,
        "job_duration_seconds": round(job_duration_seconds, 2) if job_duration_seconds else None
    }

    # Add agent_profile only if present (not required for chat simulations)
    if 'agent_profile' in config:
        job_metadata["agent_profile"] = config['agent_profile']

    job_data = {
        "job_metadata": job_metadata,
        "request": {
            "user_request": config['user_request'],
            "max_turns": config.get('max_turns', 10)
        },
        "models": model_results
    }

    # Add analytics if enabled
    analytics_config = config.get('analytics', {'enabled': True})
    job_data = add_analytics_to_job(job_data, analytics_config)

    # Determine save location based on job type
    is_single_prompt_job = "single_prompt_jobs" in str(output_dir)

    if is_single_prompt_job:
        # Single prompt job: save to job_{request_id}_{timestamp}/ subdirectory
        job_dir = output_dir / f"job_{request_id}_{timestamp}"
        job_dir.mkdir(parents=True, exist_ok=True)
        filename = f"job_{request_id}_{timestamp}.json"
        output_path = job_dir / filename
        export_base_dir = job_dir  # For single prompt jobs, save exports to job directory
    else:
        # Agent job: save to reports/ subdirectory
        reports_dir = output_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        filename = f"agent_job_{request_id}_{timestamp}.json"
        output_path = reports_dir / filename
        export_base_dir = output_dir  # For agent jobs, save to output_dir (creates subdirs)

    with open(output_path, 'w') as f:
        json.dump(job_data, f, indent=2, ensure_ascii=False)

    # Save text summary if requested
    text_summary_path = None
    if analytics_config.get('enabled', True) and analytics_config.get('save_text_summary', False):
        text_summary_path = save_text_summary(job_data, request_id, timestamp, export_base_dir, analytics_config)

    # Save human-readable chat if requested
    chat_path = None
    if analytics_config.get('export_chat', False):
        # Get chat style preference (default: "chatbot")
        chat_style = analytics_config.get('chat_style', 'chatbot')  # Options: "chatbot" or "technical"
        chat_path = save_chat_export(job_data, request_id, timestamp, export_base_dir, chat_style=chat_style)

    return output_path, text_summary_path, chat_path


def format_conversation_content(content: str) -> str:
    """Format conversation content for vertical readability.

    Attempts to parse JSON and format it in a human-readable way.
    Falls back to original content if not valid JSON.
    """
    content = content.strip()

    # Try to extract JSON from markdown code blocks
    if content.startswith('```json') and content.endswith('```'):
        json_text = content[7:-3].strip()
    elif content.startswith('```') and content.endswith('```'):
        json_text = content[3:-3].strip()
    else:
        json_text = content

    # Try to parse as JSON
    try:
        data = json.loads(json_text)

        # Format based on content structure
        formatted_lines = []

        # Handle different JSON structures
        if isinstance(data, dict):
            for key, value in data.items():
                # Skip empty values
                if value is None or value == "" or value == []:
                    continue

                # Format key header
                key_display = key.replace('_', ' ').title()
                formatted_lines.append(f"{key_display}:")

                # Format value based on type
                if isinstance(value, str):
                    # Multi-line strings get indented
                    for line in value.split('\n'):
                        formatted_lines.append(f"  {line}")
                elif isinstance(value, (list, dict)):
                    # Pretty print nested structures with indentation
                    json_str = json.dumps(value, indent=2, ensure_ascii=False)
                    for line in json_str.split('\n'):
                        formatted_lines.append(f"  {line}")
                else:
                    formatted_lines.append(f"  {value}")

                formatted_lines.append("")  # Blank line between sections

        elif isinstance(data, list):
            # Format list items
            for i, item in enumerate(data, 1):
                formatted_lines.append(f"[Item {i}]")
                json_str = json.dumps(item, indent=2, ensure_ascii=False)
                for line in json_str.split('\n'):
                    formatted_lines.append(f"  {line}")
                formatted_lines.append("")
        else:
            # Simple value
            formatted_lines.append(str(data))

        return '\n'.join(formatted_lines).rstrip()

    except json.JSONDecodeError:
        # Not JSON, return original content
        return content


def abbreviate_conversation_history(prompt: str, is_first_occurrence: bool, max_preview_chars: int = 500) -> str:
    """
    Abbreviate <conversation_history> sections in prompts for readability.

    Args:
        prompt: The full prompt text
        is_first_occurrence: If True, keeps full history; if False, abbreviates
        max_preview_chars: Number of characters to show in preview

    Returns:
        Prompt with conversation_history abbreviated (if not first occurrence)
    """
    import re

    # Find conversation_history sections
    pattern = r'<conversation_history>(.*?)</conversation_history>'
    matches = list(re.finditer(pattern, prompt, re.DOTALL))

    if not matches:
        return prompt

    # If first occurrence, return as-is
    if is_first_occurrence:
        return prompt

    # Abbreviate all conversation_history sections
    result = prompt
    offset = 0

    for match in matches:
        full_section = match.group(0)
        history_content = match.group(1).strip()

        # Create abbreviated version
        preview = history_content[:max_preview_chars]
        if len(history_content) > max_preview_chars:
            preview += "\n..."

        abbreviated = f"<conversation_history>\n[Full history abbreviated for readability - see first agent turn]\n\n{preview}\n</conversation_history>"

        # Replace in result with offset adjustment
        start = match.start() + offset
        end = match.end() + offset
        result = result[:start] + abbreviated + result[end:]
        offset += len(abbreviated) - len(full_section)

    return result


def wrap_text(text: str, width: int = 100, indent: str = "") -> str:
    """Wrap text to specified width while preserving paragraphs."""
    import textwrap

    paragraphs = text.split('\n\n')
    wrapped_paragraphs = []

    for para in paragraphs:
        # Preserve single newlines within paragraphs
        if '\n' in para and not para.strip().startswith('```'):
            wrapped_paragraphs.append(para)
        else:
            wrapped = textwrap.fill(para, width=width, initial_indent=indent,
                                   subsequent_indent=indent, break_long_words=False)
            wrapped_paragraphs.append(wrapped)

    return '\n\n'.join(wrapped_paragraphs)


def save_chat_export(job_data: Dict, request_id: str, timestamp: str, output_dir: Path, chat_style: str = 'chatbot') -> Path:
    """
    Save human-readable conversation export in Markdown format.

    Args:
        job_data: Complete job data dictionary
        request_id: Request identifier
        timestamp: Job timestamp
        output_dir: Output directory
        chat_style: Export style - "chatbot" (clean) or "technical" (with prompts/JSON)

    Returns:
        Path to created chat export file
    """
    # Create chats subdirectory
    chats_dir = output_dir / "chats"
    chats_dir.mkdir(parents=True, exist_ok=True)

    lines = []

    # Header in Markdown
    style_indicator = "💬 Chatbot View" if chat_style == 'chatbot' else "🔧 Technical View"
    header = [
        f"# Agent Conversation Export: {request_id}",
        "",
        f"*{style_indicator}*  ",
        ""
    ]

    # Add agent profile if present
    if 'agent_profile' in job_data['job_metadata']:
        header.append(f"**Agent Profile:** {job_data['job_metadata']['agent_profile']}  ")

    header.extend([
        f"**Timestamp:** {job_data['job_metadata']['timestamp']}  ",
        f"**Total Models:** {job_data['job_metadata']['total_models']}  ",
        "",
    ])

    lines.extend(header)
    lines.extend([
        "## User Request",
        "",
        wrap_text(job_data['request']['user_request'].strip()),
        "",
        "---",
        ""
    ])

    # Process each model's conversation
    for model_result in job_data['models']:
        display_name = model_result.get('display_name', 'Unknown')
        model_id = model_result.get('model_id', 'Unknown')
        extended_thinking = model_result.get('extended_thinking_enabled', False)

        # Detect extended thinking from display name if present (fallback)
        if not extended_thinking and 'extended_thinking=true' in display_name.lower():
            extended_thinking = True

        timing = model_result.get('timing', {})
        total_cost = model_result.get('total_cost_usd')

        lines.extend([
            "",
            f"## Model: {display_name}",
            "",
            f"**Model ID:** `{model_id}`  ",
            f"**Extended Thinking:** {'✓ Enabled' if extended_thinking else '✗ Disabled'}  ",
            f"**Total Turns:** {model_result.get('total_turns', 0)}  ",
            f"**Completion Reason:** {model_result.get('completion_reason', 'Unknown')}  ",
        ])

        # Add timing info if available
        if timing:
            if timing.get('total_duration_seconds'):
                lines.append(f"**Duration:** {timing['total_duration_seconds']}s total", )
                if timing.get('successful_duration_seconds'):
                    lines.append(f" ({timing['successful_duration_seconds']}s successful)  ")
                else:
                    lines.append("  ")
            if timing.get('total_inference_time_seconds'):
                lines.append(f"**Inference Time:** {timing['total_inference_time_seconds']}s  ")

        # Add cost info if available (OpenAI only)
        if total_cost is not None:
            lines.append(f"**Total Cost:** ${total_cost:.6f}  ")

        lines.append("")

        # Check for errors
        if model_result.get('error'):
            lines.extend([
                "### ❌ Error",
                "",
                "```",
                wrap_text(model_result['error'], width=100),
                "```",
                "",
                "---",
                ""
            ])
            continue

        # Export conversation log
        conversation_log = model_result.get('conversation_log', [])

        if not conversation_log:
            lines.append("*(No conversation log available)*\n")
            continue

        # Track whether we've seen the first conversation_history for this model
        seen_conversation_history = False

        for entry in conversation_log:
            turn = entry.get('turn', '?')
            role = entry.get('role', 'unknown')
            content = entry.get('content', '')
            thinking = entry.get('thinking', None)
            inference_time = entry.get('inference_time_seconds')
            cost = entry.get('cost_usd')
            prompt = entry.get('prompt', None)

            # Parse content for structured extraction
            parsed_content = None
            try:
                # Try parsing directly as JSON
                parsed_content = json.loads(content)
            except:
                # Try extracting JSON from markdown code fence
                try:
                    import re
                    # Look for ```json ... ``` or ``` ... ``` blocks
                    json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        parsed_content = json.loads(json_str)
                    else:
                        # Try removing markdown fences if it starts with ```
                        cleaned = content.strip()
                        if cleaned.startswith('```'):
                            content_lines = cleaned.split('\n', 1)
                            if len(content_lines) > 1:
                                cleaned = content_lines[1]
                            if cleaned.strip().endswith('```'):
                                cleaned = cleaned.strip()[:-3]
                            parsed_content = json.loads(cleaned.strip())
                except:
                    parsed_content = None

            # CHATBOT STYLE - Clean conversational view
            if chat_style == 'chatbot':
                # Handle both agent simulation roles (agent/tool_simulator) and chat simulation roles (assistant/user_simulator)
                if role in ['agent', 'assistant']:
                    # Build metadata
                    metadata_parts = [f"Turn {turn}"]
                    if inference_time:
                        metadata_parts.append(f"{inference_time:.1f}s")
                    if cost is not None:
                        metadata_parts.append(f"${cost:.6f}")
                    metadata = " · ".join(metadata_parts)

                    # Use appropriate icon and label
                    icon = "🤖" if role == 'agent' else "💬"
                    label = "Agent" if role == 'agent' else "Assistant"

                    lines.extend([
                        "",
                        f"### {icon} {label}",
                        "",
                        f"*{metadata}*",
                        ""
                    ])

                    # Show extended thinking if present (from model's thinking field in metadata)
                    if thinking and extended_thinking:
                        lines.extend([
                            "**💭 Extended Thinking:**",
                            "",
                            wrap_text(thinking.strip(), width=100),
                            ""
                        ])

                    # Try to extract thinking/reasoning from the response content
                    extracted_thinking = None
                    if parsed_content and isinstance(parsed_content, dict):
                        extracted_thinking = parsed_content.get('thinking') or parsed_content.get('reasoning', '')

                    if extracted_thinking and isinstance(extracted_thinking, str):
                        lines.append("**Thinking:**")
                        lines.append("")
                        lines.append(wrap_text(extracted_thinking.strip(), width=100))
                        lines.append("")

                    # Show full response content as-is
                    lines.append("**Response:**")
                    lines.append("")
                    lines.append(content)
                    lines.append("")

                    lines.extend(["---", ""])

                elif role in ['tool_simulator', 'user_simulator']:
                    if content.strip() == 'STOP':
                        continue

                    # Use appropriate icon and label
                    icon = "🛠️" if role == 'tool_simulator' else "👤"
                    label = "Tool Response" if role == 'tool_simulator' else "User"

                    lines.extend([
                        "",
                        f"### {icon} {label}",
                        ""
                    ])

                    # Show full tool response content as-is
                    lines.append(content)
                    lines.append("")

                    lines.extend(["---", ""])

        # Append judge evaluation for this model (if present)
        if 'judge_evaluation' in job_data:
            judge_data = job_data['judge_evaluation']
            evaluations = judge_data.get('evaluations', [])

            # Find evaluation(s) for this model
            model_evaluations = [
                e for e in evaluations
                if e.get('model_id') == model_id or e.get('display_name') == display_name
            ]

            if model_evaluations:
                lines.extend([
                    "",
                    "## 📊 Judge Evaluation",
                    ""
                ])

                for eval_data in model_evaluations:
                    # Show judge metadata
                    judge_model = judge_data.get('judge_metadata', {}).get('judge_model', 'Unknown')
                    lines.extend([
                        f"**Judge Model:** {judge_model}",
                        ""
                    ])

                    # Show extracted JSON evaluation if available
                    if eval_data.get('extracted_json'):
                        extracted = eval_data['extracted_json']
                        lines.extend([
                            "**Evaluation Results:**",
                            "",
                            "```json",
                            json.dumps(extracted, indent=2),
                            "```",
                            ""
                        ])

                    # Show raw evaluation
                    if eval_data.get('raw_evaluation'):
                        lines.extend([
                            "**Full Evaluation:**",
                            "",
                            eval_data['raw_evaluation'],
                            ""
                        ])

                lines.extend(["---", ""])

            # TECHNICAL STYLE - Full prompts and JSON
            else:
                # Format role header in Markdown
                if role == 'agent':
                    role_icon = "🤖"
                    role_label = "Agent"
                elif role == 'tool_simulator':
                    role_icon = "🛠️"
                    role_label = "Tool Simulator"
                else:
                    role_icon = "💬"
                    role_label = role.title()

                # Build timing and cost info
                timing_info = f" ({inference_time}s)" if inference_time else ""
                cost_info = f" [${cost:.6f}]" if cost is not None else ""
                lines.extend([
                    "",
                    f"### {role_icon} Turn {turn} - {role_label}{timing_info}{cost_info}",
                    ""
                ])

                # Include prompt if present (only for agent role)
                if prompt and role == 'agent':
                    # Check if prompt contains conversation_history
                    has_history = '<conversation_history>' in prompt

                    # Abbreviate if not the first occurrence
                    if has_history:
                        is_first = not seen_conversation_history
                        prompt = abbreviate_conversation_history(prompt, is_first_occurrence=is_first)
                        seen_conversation_history = True

                    lines.extend([
                        "<details>",
                        "<summary><b>📋 Prompt Sent to Agent</b></summary>",
                        "",
                        "```",
                        wrap_text(prompt.strip(), width=100),
                        "```",
                        "",
                        "</details>",
                        ""
                    ])

                # Include thinking if present and extended_thinking was enabled
                if thinking and extended_thinking:
                    lines.extend([
                        "<details>",
                        "<summary><b>🧠 Extended Thinking</b></summary>",
                        "",
                        "```",
                        wrap_text(thinking.strip(), width=100),
                        "```",
                        "",
                        "</details>",
                        ""
                    ])

                # Parse and format JSON content for better readability
                formatted_content = format_conversation_content(content)

                # Wrap in code block if it looks like JSON
                if formatted_content.strip().startswith('{') or formatted_content.strip().startswith('['):
                    lines.extend([
                        "```json",
                        formatted_content,
                        "```",
                        ""
                    ])
                else:
                    lines.extend([
                        wrap_text(formatted_content, width=100),
                        ""
                    ])

    # Add judge evaluation if present
    if 'judge_evaluation' in job_data:
        from export_utils import format_judge_section
        judge_lines = format_judge_section(job_data['judge_evaluation'], include_header=True)
        lines.extend(judge_lines)

    # Footer
    lines.extend([
        "",
        "---",
        "",
        "*End of conversation export*"
    ])

    # Save to file with .md extension
    filename = f"agent_job_{request_id}_{timestamp}_chat.md"
    chat_path = chats_dir / filename

    with open(chat_path, 'w') as f:
        f.write('\n'.join(lines))

    return chat_path


def save_text_summary(job_data: Dict, request_id: str, timestamp: str, output_dir: Path, analytics_config: Dict) -> Path:
    """Save human-readable analytics summary in Markdown format."""
    # Create summaries subdirectory
    summaries_dir = output_dir / "summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)

    # Generate detailed summary
    engine = AnalyticsEngine(analytics_config)
    detailed = analytics_config.get('text_summary_detailed', True)
    summary = engine.format_summary(job_data.get('analytics', {}), detailed=detailed)

    # Add job metadata header in Markdown
    job_duration = job_data['job_metadata'].get('job_duration_seconds')
    duration_text = f"**Job Duration:** {job_duration}s  \n" if job_duration else ""

    header_lines = [
        f"# Agent Job Summary: {request_id}",
        ""
    ]

    # Add agent profile if present
    if 'agent_profile' in job_data['job_metadata']:
        header_lines.append(f"**Agent Profile:** {job_data['job_metadata']['agent_profile']}  ")

    header_lines.extend([
        f"**Timestamp:** {job_data['job_metadata']['timestamp']}  ",
        f"**Total Models:** {job_data['job_metadata']['total_models']}  ",
        f"**Successful:** ✓ {job_data['job_metadata']['successful']}  ",
        f"**Failed:** ✗ {job_data['job_metadata']['failed']}  ",
        duration_text,
        "",
        "## User Request",
        "",
        wrap_text(job_data['request']['user_request'].strip()),
        "",
        "---",
        ""
    ])

    full_summary = "\n".join(header_lines) + "\n" + summary

    # Save to file with .md extension
    filename = f"agent_job_{request_id}_{timestamp}_summary.md"
    summary_path = summaries_dir / filename

    with open(summary_path, 'w') as f:
        f.write(full_summary)

    return summary_path


def print_model_summary(model_result: Dict):
    """Print individual model execution summary."""
    print(f"  ✓ Completed in {model_result['total_turns']} turns")
    print(f"    Reason: {model_result['completion_reason']}")

    # Print timing information if available
    timing = model_result.get('timing')
    if timing:
        total_duration = timing.get('total_duration_seconds')
        successful_duration = timing.get('successful_duration_seconds')
        inference_time = timing.get('total_inference_time_seconds')

        if total_duration is not None:
            print(f"    Duration: {total_duration}s total", end="")
            if successful_duration is not None:
                print(f" ({successful_duration}s successful)", end="")
            if inference_time is not None:
                print(f", {inference_time}s inference")
            else:
                print()

    # Print cost information if available (OpenAI only)
    total_cost = model_result.get('total_cost_usd')
    if total_cost is not None:
        print(f"    Cost: ${total_cost:.6f}")

    if model_result.get('error'):
        print(f"    Error: {model_result['error']}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python agent_invoke.py <request_config.yaml>")
        print("\nExample request config:")
        print("  request_id: test_001")
        print("  agent_profile: schedulerAgent")
        print("  user_request: 'Schedule a meeting...'")
        print("  models:")
        print("    - us.anthropic.claude-sonnet-4-5-20250929-v1:0")
        print("\nOr use model_list:")
        print("  model_list: model_config/main_list/test_list")
        sys.exit(1)

    config_path = Path(sys.argv[1])

    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    # Load configuration
    print(f"Loading request config: {config_path}")
    config = load_request_config(config_path)

    # Parse models
    models = parse_models(config)

    if not models:
        print("Error: No models specified in config")
        sys.exit(1)

    # Determine job type for display
    simulation_type = config.get('simulation_type', 'agent')
    job_type = "CHAT SIMULATION JOB" if simulation_type == 'chat' else "AGENT SIMULATION JOB"

    print(f"\n{'='*80}")
    print(f"{job_type}")
    print(f"{'='*80}")
    print(f"Request ID: {config.get('request_id', 'unknown')}")
    if 'agent_profile' in config:
        print(f"Agent Profile: {config['agent_profile']}")
    print(f"User Request: {config['user_request'][:100]}...")
    print(f"Max Turns: {config.get('max_turns', 10)}")
    print(f"Models: {len(models)}")
    print(f"{'='*80}\n")

    # Track job-level timing
    job_start_time = time.time()

    # Output directory relative to project root (parent of src/)
    project_root = Path(__file__).parent.parent

    # Determine output directory based on metadata (for intervention-based organization)
    metadata = config.get('metadata', {})
    if metadata.get('suite') and metadata.get('intervention'):
        # Single prompt job with intervention: outputs/single_prompt_jobs/{intervention}_{suite}/
        intervention = metadata['intervention']
        suite = metadata['suite']
        output_dir = project_root / "outputs" / "single_prompt_jobs" / f"{intervention}_{suite}"
    else:
        # Default agent jobs directory
        output_dir = project_root / "outputs" / "agent_jobs"

    model_results = []

    # Process each model
    for i, model_config in enumerate(models, 1):
        model_id = model_config["model_id"]
        display_name = model_config["display_name"]
        extended_thinking = model_config.get("extended_thinking", False)
        provider = model_config.get("provider", "bedrock")
        reasoning_effort = model_config.get("reasoning_effort", "medium")

        # Warn if extended thinking requested but not supported
        if extended_thinking and model_id not in EXTENDED_THINKING_MODELS:
            print(f"[{i}/{len(models)}] {display_name}...")
            print(f"  ⚠ Warning: {display_name} does not support extended thinking, ignoring flag")
            extended_thinking = False
        else:
            print(f"[{i}/{len(models)}] Running simulation with {display_name}...")

        try:
            # Get retry configuration from config (or use defaults)
            retry_config = config.get('retry_config')

            # Determine simulation type: chat vs agent
            simulation_type = config.get('simulation_type', 'agent')  # Default to agent for backward compatibility

            # Run appropriate simulation
            if simulation_type == 'chat':
                simulation = ChatSimulation(
                    config, model_id, display_name, extended_thinking,
                    retry_config, provider, reasoning_effort
                )
            else:
                simulation = AgentSimulation(
                    config, model_id, display_name, extended_thinking,
                    retry_config, provider, reasoning_effort
                )

            model_result = simulation.run()

            # Add to results
            model_results.append(model_result)

            # Print summary for this model
            if model_result.get('error'):
                print(f"  ✗ Failed: {model_result['error']}")
            else:
                print_model_summary(model_result)

        except Exception as e:
            print(f"  ✗ Exception: {e}")
            # Add error result for this model
            model_results.append({
                "model_id": model_id,
                "display_name": display_name,
                "extended_thinking_enabled": extended_thinking,
                "started_at": None,
                "completed_at": datetime.now().isoformat(),
                "total_turns": 0,
                "completion_reason": "ERROR",
                "conversation_log": [],
                "error": str(e)
            })

        print()

    # Retry failed models (if enabled)
    max_job_retries = config.get('max_job_retries', 0)
    if max_job_retries > 0:
        retry_round = 1
        while retry_round <= max_job_retries:
            # Collect failed models from current results
            failed_indices = [
                i for i, result in enumerate(model_results)
                if result.get('error') is not None
            ]

            if not failed_indices:
                print(f"\n✓ All models succeeded! No retries needed.")
                break

            print(f"\n{'='*80}")
            print(f"RETRY ROUND {retry_round}/{max_job_retries}: Retrying {len(failed_indices)} failed model(s)")
            print(f"{'='*80}\n")

            # Track if any model succeeded on this retry round
            retry_success_count = 0

            for idx in failed_indices:
                failed_result = model_results[idx]
                model_id = failed_result['model_id']
                display_name = failed_result['display_name']
                extended_thinking = failed_result.get('extended_thinking_enabled', False)

                print(f"[Retry {retry_round}] {display_name}...")

                try:
                    # Get retry configuration from config (or use defaults)
                    retry_config = config.get('retry_config')

                    # Determine simulation type
                    simulation_type = config.get('simulation_type', 'agent')

                    # Run appropriate simulation again
                    if simulation_type == 'chat':
                        simulation = ChatSimulation(config, model_id, display_name, extended_thinking, retry_config)
                    else:
                        simulation = AgentSimulation(config, model_id, display_name, extended_thinking, retry_config)

                    model_result = simulation.run()

                    # Replace the failed result with the new attempt
                    model_results[idx] = model_result

                    # Check if this retry succeeded
                    if not model_result.get('error'):
                        retry_success_count += 1
                        print_model_summary(model_result)
                    else:
                        print(f"  ✗ Still failed: {model_result['error']}")

                except Exception as e:
                    print(f"  ✗ Exception: {e}")
                    # Update with new error
                    model_results[idx] = {
                        "model_id": model_id,
                        "display_name": display_name,
                        "extended_thinking_enabled": extended_thinking,
                        "started_at": None,
                        "completed_at": datetime.now().isoformat(),
                        "total_turns": 0,
                        "completion_reason": "ERROR",
                        "conversation_log": [],
                        "error": f"Retry {retry_round} failed: {str(e)}"
                    }

                print()

            # Summary of this retry round
            if retry_success_count > 0:
                print(f"✓ Retry round {retry_round} recovered {retry_success_count} model(s)")
            else:
                print(f"✗ Retry round {retry_round} did not recover any models")

            retry_round += 1

    # Calculate total job duration
    job_duration = time.time() - job_start_time

    # Save complete job with all model results
    print(f"\nSaving job results...")
    job_path, text_summary_path, chat_path = save_agent_job(config, model_results, output_dir, job_duration)
    print(f"  JSON Report → {job_path.relative_to(output_dir.parent)}")
    if text_summary_path:
        print(f"  Analytics Summary → {text_summary_path.relative_to(output_dir.parent)}")
    if chat_path:
        print(f"  Chat Export → {chat_path.relative_to(output_dir.parent)}")

    # Run judge evaluation if configured
    if 'judge' in config:
        print(f"\n{'='*80}")
        print(f"RUNNING JUDGE EVALUATION")
        print(f"{'='*80}\n")

        # Load judge config from file if it's a string path, otherwise use inline dict
        judge_config_raw = config['judge']
        judge_config = None

        if isinstance(judge_config_raw, str):
            # Load from external file
            judge_config_path = Path(judge_config_raw)
            if not judge_config_path.exists():
                print(f"✗ Judge config file not found: {judge_config_raw}")
                print(f"Skipping judge evaluation...\n")
            else:
                print(f"Loading judge config from: {judge_config_raw}")
                with open(judge_config_path, 'r') as f:
                    judge_config = yaml.safe_load(f)
        else:
            # Use inline config
            judge_config = judge_config_raw

        # Only proceed if config was successfully loaded
        if judge_config:
            # Parse judge models
            judge_models = parse_judge_models(judge_config)

            # Parse comparative judge (optional)
            comparative_judge_config = parse_comparative_judge(judge_config)

            # Get judge configuration options
            judge_id = judge_config.get('judge_id', f"{config.get('request_id', 'unknown')}_judge")
            judge_prompt = judge_config['judge_prompt']
            jq_filter = judge_config.get('jq_filter')
            append_to_source = judge_config.get('append_to_source', True)  # Default to True for chained jobs
            anonymize_pass1 = judge_config.get('anonymize_pass1', True)

            # Get retry config from main job config
            retry_config = config.get('retry_config')

            try:
                # Run judge evaluation with retry config
                run_judge_evaluation(
                    source_job_path=str(job_path),
                    judge_id=judge_id,
                    judge_prompt=judge_prompt,
                    judge_models=judge_models,
                    jq_filter=jq_filter,
                    append_to_source=append_to_source,
                    comparative_judge_config=comparative_judge_config,
                    anonymize_pass1=anonymize_pass1,
                    retry_config=retry_config
                )

                print(f"\n{'='*80}")
                print(f"JUDGE EVALUATION COMPLETE")
                print(f"{'='*80}\n")

            except Exception as e:
                print(f"\n✗ Judge evaluation failed: {e}")
                print(f"Continuing with job completion...\n")

    # Display analytics if enabled
    analytics_config = config.get('analytics', {'enabled': True})
    if analytics_config.get('enabled', True):
        # Read the saved file to get analytics
        with open(job_path, 'r') as f:
            saved_job_data = json.load(f)

        if 'analytics' in saved_job_data:
            engine = AnalyticsEngine(analytics_config)
            print(f"\n{engine.format_summary(saved_job_data['analytics'])}")

    # Final summary
    print(f"\nResults saved to:")
    print(f"  JSON: {job_path}")
    if text_summary_path:
        print(f"  Text: {text_summary_path}")
    if chat_path:
        print(f"  Chat: {chat_path}")
    print(f"\nJob Duration: {job_duration:.2f} seconds")
    print(f"{'='*80}\n")

    # Post-job behavioral analysis prompt (if not already done via judge config)
    try:
        from behavioral_prompt_handler import (
            prompt_for_behavioral_analysis,
            run_behavioral_analysis,
            prompt_for_profile_update
        )

        # Check if we should prompt (interactive mode, no existing behavioral eval)
        chunking = prompt_for_behavioral_analysis(job_path, interactive=True)

        if chunking:
            # Run analysis and stage results
            staged_results_path = run_behavioral_analysis(
                job_path,
                chunking,
                framework_config=None,  # Use default
                staging_dir=None  # Use default
            )

            # Prompt to apply to master profiles
            prompt_for_profile_update(staged_results_path, interactive=True)

    except Exception as e:
        print(f"Warning: Behavioral analysis prompt failed: {e}\n")


if __name__ == "__main__":
    main()
