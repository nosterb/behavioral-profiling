#!/usr/bin/env python3
"""
Chat simulation system - simple back-and-forth conversations without tools.

Simulates chat conversations where:
1. LLM acts as assistant responding to user messages
2. Another LLM simulates user responses
3. Loop continues until either side signals completion (STOP)
4. Full conversation logged for analysis

This is separate from agent_invoke.py which is designed for tool-based workflows.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from model_providers import create_provider, ModelResponse


class ChatSimulation:
    """Manages a simple chat conversation simulation (no tools, just dialogue)."""

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
        self.total_cost_usd = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_inference_time = 0.0

        # Chat-specific settings
        self.include_conversation_history = request_config.get('include_conversation_history', True)
        self.include_conversation_history_user_sim = request_config.get('include_conversation_history_user_sim', True)
        self.reinject_prompt_every_turn = request_config.get('reinject_prompt_every_turn', False)

        # Template configuration (sensible defaults for chat)
        self.assistant_template = request_config.get('assistant_template', 'templates/chat_assistant.txt')
        self.assistant_continuation_template = request_config.get('assistant_continuation_template', None)
        self.user_simulator_template = request_config.get('user_simulator_template', 'templates/chat_user_simulator.txt')

        # Retry configuration
        self.retry_config = retry_config or {
            "max_retries": 3,
            "initial_timeout": 120,
            "backoff_multiplier": 2.0,
            "max_timeout": 300
        }

    def run(self) -> Dict[str, Any]:
        """Execute chat simulation."""
        start_time = time.time()
        max_turns = self.request_config.get('max_turns', 10)

        try:
            # Load optional prompt injection
            additional_prompt = self._load_additional_prompt()

            # Initial assistant response
            turn = 1
            response, prompt = self._invoke_assistant(
                user_message=self.request_config['user_request'],
                additional_prompt=additional_prompt,
                is_first_turn=True
            )

            # Log assistant response
            self._log_turn(turn, 'assistant', response.response_text, response, prompt)

            # Check for immediate stop
            if self._should_stop(response.response_text):
                return self._build_result(start_time, turn, "STOP")

            # Chat loop
            for turn in range(2, max_turns + 1):
                # Simulate user response
                user_response, user_prompt = self._simulate_user(response.response_text)

                # Log user response
                self._log_turn(turn, 'user_simulator', user_response.response_text, user_response, user_prompt)

                # Check if user simulator said stop
                if self._should_stop(user_response.response_text):
                    return self._build_result(start_time, turn, "STOP")

                # Continue assistant
                response, prompt = self._continue_assistant(
                    user_message=user_response.response_text,
                    additional_prompt=additional_prompt
                )

                # Log assistant response
                self._log_turn(turn, 'assistant', response.response_text, response, prompt)

                # Check if assistant said stop
                if self._should_stop(response.response_text):
                    return self._build_result(start_time, turn, "STOP")

            # Reached max turns
            return self._build_result(start_time, max_turns, "MAX_TURNS")

        except Exception as e:
            return self._build_error_result(start_time, str(e))

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

    def _invoke_assistant(self, user_message: str, additional_prompt: str = "", is_first_turn: bool = False) -> Tuple[ModelResponse, str]:
        """Initial assistant invocation."""
        with open(self.assistant_template, 'r') as f:
            template = f.read()

        prompt = template.format(
            additional_prompt=additional_prompt,
            user_message=user_message,
            conversation_history=""
        )

        provider = create_provider(self.provider, self.model_id, self.display_name, retry_config=self.retry_config)

        if self.provider in ["openai", "grok"]:
            response = provider.invoke(prompt, max_tokens=4096, reasoning_effort=self.reasoning_effort)
        elif self.provider == "gemini":
            response = provider.invoke(prompt, max_tokens=4096, thinking_level=self.reasoning_effort)
        else:
            response = provider.invoke(prompt, max_tokens=4096, extended_thinking=self.extended_thinking)

        if not response.success:
            raise RuntimeError(f"Provider invocation failed: {response.error}")

        if not response.response_text:
            raise RuntimeError(f"Provider returned empty response (stop_reason: {response.stop_reason})")

        return response, prompt

    def _continue_assistant(self, user_message: str, additional_prompt: str = "") -> Tuple[ModelResponse, str]:
        """Continue assistant with new user message."""
        # Use continuation template if specified, otherwise use same template
        if self.assistant_continuation_template:
            with open(self.assistant_continuation_template, 'r') as f:
                template = f.read()
        else:
            with open(self.assistant_template, 'r') as f:
                template = f.read()

        # Build conversation history
        history_section = ""
        if self.include_conversation_history and self.conversation_log:
            for entry in self.conversation_log:
                role = entry.get('role', 'unknown')
                content = entry.get('content', '')
                turn = entry.get('turn', '?')

                if role == 'assistant':
                    history_section += f"\n[Turn {turn} - Assistant]:\n{content}\n"
                elif role == 'user_simulator':
                    history_section += f"\n[Turn {turn} - User]:\n{content}\n"

        # Only reinject prompt if configured to do so
        injection = additional_prompt if self.reinject_prompt_every_turn else ""

        prompt = template.format(
            additional_prompt=injection,
            user_message=user_message,
            conversation_history=history_section
        )

        provider = create_provider(self.provider, self.model_id, self.display_name, retry_config=self.retry_config)

        if self.provider in ["openai", "grok"]:
            response = provider.invoke(prompt, max_tokens=4096, reasoning_effort=self.reasoning_effort)
        elif self.provider == "gemini":
            response = provider.invoke(prompt, max_tokens=4096, thinking_level=self.reasoning_effort)
        else:
            response = provider.invoke(prompt, max_tokens=4096, extended_thinking=self.extended_thinking)

        if not response.success:
            raise RuntimeError(f"Provider invocation failed: {response.error}")

        if not response.response_text:
            raise RuntimeError(f"Provider returned empty response (stop_reason: {response.stop_reason})")

        return response, prompt

    def _simulate_user(self, assistant_message: str) -> Tuple[ModelResponse, str]:
        """Simulate user response to assistant message."""
        with open(self.user_simulator_template, 'r') as f:
            template = f.read()

        # Build conversation history for user simulator
        history_section = ""
        if self.include_conversation_history_user_sim and self.conversation_log:
            for entry in self.conversation_log:
                role = entry.get('role', 'unknown')
                content = entry.get('content', '')
                turn = entry.get('turn', '?')

                if role == 'assistant':
                    history_section += f"\n[Turn {turn} - Assistant]:\n{content}\n"
                elif role == 'user_simulator':
                    history_section += f"\n[Turn {turn} - User]:\n{content}\n"

        prompt = template.format(
            original_user_request=self.request_config['user_request'],
            assistant_message=assistant_message,
            conversation_history=history_section
        )

        provider = create_provider(self.provider, self.model_id, self.display_name, retry_config=self.retry_config)

        if self.provider in ["openai", "grok"]:
            response = provider.invoke(prompt, max_tokens=4096, reasoning_effort=self.reasoning_effort)
        elif self.provider == "gemini":
            response = provider.invoke(prompt, max_tokens=4096, thinking_level=self.reasoning_effort)
        else:
            response = provider.invoke(prompt, max_tokens=4096, extended_thinking=self.extended_thinking)

        if not response.success:
            raise RuntimeError(f"User simulator invocation failed: {response.error}")

        if not response.response_text:
            raise RuntimeError(f"User simulator returned empty response")

        return response, prompt

    def _should_stop(self, text: str) -> bool:
        """Check if message contains stop signal.

        Only matches exact 'STOP' as standalone word to avoid false positives
        from words like 'stopped', 'stopping', etc.
        """
        if not text:
            return False

        # Check if response is exactly "STOP" (case-insensitive)
        return text.strip().upper() == "STOP"

    def _log_turn(self, turn: int, role: str, content: str, response: ModelResponse, prompt: Optional[str]):
        """Log a conversation turn."""
        entry = {
            'turn': turn,
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'input_tokens': response.input_tokens,
            'output_tokens': response.output_tokens,
            'inference_time_seconds': response.inference_time_seconds,
            'cost_usd': response.cost_usd
        }

        if prompt:
            entry['prompt'] = prompt

        if response.thinking:
            entry['thinking'] = response.thinking

        self.conversation_log.append(entry)

        # Update totals
        if response.input_tokens:
            self.total_input_tokens += response.input_tokens
        if response.output_tokens:
            self.total_output_tokens += response.output_tokens
        if response.inference_time_seconds:
            self.total_inference_time += response.inference_time_seconds
        if response.cost_usd:
            self.total_cost_usd += response.cost_usd

    def _build_result(self, start_time: float, final_turn: int, completion_reason: str) -> Dict[str, Any]:
        """Build successful result."""
        end_time = time.time()
        total_duration = end_time - start_time

        return {
            'model_id': self.model_id,
            'display_name': self.display_name,
            'started_at': datetime.fromtimestamp(start_time).isoformat(),
            'completed_at': datetime.fromtimestamp(end_time).isoformat(),
            'total_turns': final_turn,
            'completion_reason': completion_reason,
            'conversation_log': self.conversation_log,
            'extended_thinking_enabled': self.extended_thinking,
            'timing': {
                'total_duration_seconds': round(total_duration, 2),
                'total_inference_time_seconds': round(self.total_inference_time, 2)
            },
            'tokens': {
                'total_input': self.total_input_tokens,
                'total_output': self.total_output_tokens
            },
            'total_cost_usd': round(self.total_cost_usd, 6) if self.total_cost_usd else None
        }

    def _build_error_result(self, start_time: float, error_message: str) -> Dict[str, Any]:
        """Build error result."""
        end_time = time.time()
        total_duration = end_time - start_time

        return {
            'model_id': self.model_id,
            'display_name': self.display_name,
            'started_at': None,
            'completed_at': datetime.fromtimestamp(end_time).isoformat(),
            'total_turns': len([e for e in self.conversation_log if e.get('role') == 'assistant']),
            'completion_reason': 'ERROR',
            'conversation_log': self.conversation_log,
            'error': error_message,
            'error_details': {
                'error_type': 'RuntimeError',
                'error_message': error_message,
                'turn_count': len(self.conversation_log),
                'conversation_log_entries': len(self.conversation_log),
                'model_id': self.model_id
            },
            'timing': {
                'total_duration_seconds': round(total_duration, 2),
                'successful_duration_seconds': None
            }
        }
