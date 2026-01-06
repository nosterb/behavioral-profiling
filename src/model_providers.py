#!/usr/bin/env python3
"""
Model provider abstraction layer for multi-provider LLM API calls.
Supports Bedrock, OpenAI, Grok, and Gemini (with placeholders for non-Bedrock).
"""

import json
import os
import base64
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from botocore.config import Config


# Models that support extended thinking
EXTENDED_THINKING_MODELS = {
    "us.anthropic.claude-opus-4-20250514-v1:0",
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "us.anthropic.claude-opus-4-1-20250805-v1:0",  # Claude-4.1-Opus
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "global.anthropic.claude-opus-4-5-20251101-v1:0"  # New global model with thinking
}

# OpenAI pricing per 1M tokens (approximate, check openai.com/pricing for current rates)
OPENAI_PRICING = {
    # GPT-4o series
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-realtime-preview": {"input": 5.00, "output": 20.00},

    # GPT-4.1 series
    "gpt-4.1": {"input": 3.00, "output": 12.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano": {"input": 0.20, "output": 0.80},

    # GPT-5 series (reasoning models - higher pricing)
    "gpt-5.1": {"input": 10.00, "output": 40.00},
    "gpt-5-mini": {"input": 2.00, "output": 8.00},
    "gpt-5-nano": {"input": 1.00, "output": 4.00},

    # O series (reasoning models)
    "o3": {"input": 10.00, "output": 40.00},
    "o4-mini": {"input": 2.00, "output": 8.00},
}

# Grok (xAI) pricing per 1M tokens (approximate, check x.ai/api for current rates)
# Note: Grok models do not currently support reasoning_effort parameter
# They may have built-in reasoning capabilities but the API doesn't expose configuration
GROK_PRICING = {
    # Grok 4 series (always reasoning, no reasoning_effort parameter)
    "grok-4-1-fast-reasoning": {"input": 5.00, "output": 15.00},
    "grok-4-0709": {"input": 5.00, "output": 15.00},
    # Grok 3 series (no reasoning_effort parameter)
    "grok-3": {"input": 2.00, "output": 10.00},
    "grok-3-mini": {"input": 1.00, "output": 5.00},
    # Grok 2 series
    "grok-2": {"input": 2.00, "output": 10.00},
}

# Gemini (Google) pricing per 1M tokens (approximate, check ai.google.dev/pricing for current rates)
# Note: Gemini 2.5 uses thinking_budget (token-based), Gemini 3 uses thinking_level
GEMINI_PRICING = {
    # Gemini 3 series
    "gemini-3-pro-preview": {"input": 0.00, "output": 0.00},  # Free during preview
    # Gemini 2.5 series
    "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
    # Gemini 2.0 series
    "gemini-2.0-flash-exp": {"input": 0.00, "output": 0.00},  # Free during preview
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    # Gemini 1.5 series
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-1.5-flash-8b": {"input": 0.0375, "output": 0.15},
}

def calculate_openai_cost(model_id: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    """Calculate cost for OpenAI API call in USD.

    Args:
        model_id: OpenAI model identifier
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Estimated cost in USD, or None if pricing unknown
    """
    if not input_tokens or not output_tokens:
        return None

    # Find pricing by checking if model_id starts with any known model
    for model_key, pricing in OPENAI_PRICING.items():
        if model_id.startswith(model_key):
            input_cost = (input_tokens / 1_000_000) * pricing["input"]
            output_cost = (output_tokens / 1_000_000) * pricing["output"]
            return round(input_cost + output_cost, 6)  # Round to 6 decimal places

    return None  # Unknown model pricing


def calculate_grok_cost(model_id: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    """Calculate cost for Grok (xAI) API call in USD.

    Args:
        model_id: Grok model identifier
        input_tokens: Number of input tokens (includes reasoning tokens)
        output_tokens: Number of output tokens (includes reasoning tokens)

    Returns:
        Estimated cost in USD, or None if pricing unknown
    """
    if not input_tokens or not output_tokens:
        return None

    # Find pricing by checking if model_id starts with any known model
    for model_key, pricing in GROK_PRICING.items():
        if model_id.startswith(model_key):
            input_cost = (input_tokens / 1_000_000) * pricing["input"]
            output_cost = (output_tokens / 1_000_000) * pricing["output"]
            return round(input_cost + output_cost, 6)  # Round to 6 decimal places

    return None  # Unknown model pricing


def calculate_gemini_cost(model_id: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    """Calculate cost for Gemini (Google) API call in USD.

    Args:
        model_id: Gemini model identifier
        input_tokens: Number of input tokens (includes thinking tokens)
        output_tokens: Number of output tokens (includes thinking tokens)

    Returns:
        Estimated cost in USD, or None if pricing unknown
    """
    if not input_tokens or not output_tokens:
        return None

    # Find pricing by checking if model_id starts with any known model
    for model_key, pricing in GEMINI_PRICING.items():
        if model_id.startswith(model_key):
            input_cost = (input_tokens / 1_000_000) * pricing["input"]
            output_cost = (output_tokens / 1_000_000) * pricing["output"]
            return round(input_cost + output_cost, 6)  # Round to 6 decimal places

    return None  # Unknown model pricing


@dataclass
class ModelResponse:
    """Standardized response from any model provider."""
    success: bool
    response_text: str
    stop_reason: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    thinking: Optional[str] = None  # Extended thinking content (Claude 4+ only)
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    inference_time_seconds: Optional[float] = None  # Time for this individual invocation
    cost_usd: Optional[float] = None  # Estimated cost in USD (when available)


class ModelProvider(ABC):
    """Abstract base class for model providers."""

    def __init__(self, model_id: str, display_name: str):
        self.model_id = model_id
        self.display_name = display_name

    @abstractmethod
    def invoke(self, prompt: str, max_tokens: int = 4096) -> ModelResponse:
        """Invoke the model with a prompt and return standardized response."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name (bedrock, openai, etc.)."""
        pass


class BedrockProvider(ModelProvider):
    """AWS Bedrock provider implementation."""

    def __init__(self, model_id: str, display_name: str, region: str = "us-east-1",
                 retry_config: Optional[Dict[str, Any]] = None):
        super().__init__(model_id, display_name)
        self.region = region
        self._client = None

        # Default retry configuration
        self.retry_config = retry_config or {
            "max_retries": 3,
            "initial_timeout": 120,  # seconds
            "backoff_multiplier": 2.0,
            "max_timeout": 300  # seconds
        }

    def _get_client(self):
        """Lazy initialization of Bedrock client with timeout configuration."""
        if self._client is None:
            import boto3

            bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
            if not bearer_token:
                raise ValueError("AWS_BEARER_TOKEN_BEDROCK environment variable not set")

            # Decode bearer token
            token = bearer_token[4:] if bearer_token.startswith('ABSK') else bearer_token
            decoded = base64.b64decode(token).decode('utf-8')
            access_key, secret_key = decoded.split(':', 1)

            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=self.region
            )

            # Configure timeouts - start with initial timeout from retry_config
            boto_config = Config(
                read_timeout=self.retry_config['initial_timeout'],
                connect_timeout=10,
                retries={'max_attempts': 0}  # We handle retries manually
            )

            self._client = session.client('bedrock-runtime', region_name=self.region, config=boto_config)

        return self._client

    def _is_timeout_error(self, error: Exception) -> bool:
        """Check if error is a timeout error that should be retried."""
        error_str = str(error).lower()
        return any(keyword in error_str for keyword in [
            'read timeout',
            'connect timeout',
            'timed out',
            'timeout',
            'connection timeout'
        ])

    def invoke(self, prompt: str, max_tokens: int = 4096, extended_thinking: bool = False) -> ModelResponse:
        """Invoke Bedrock model using Converse API with retry logic for timeouts.

        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens in response
            extended_thinking: Enable extended thinking (Claude 4+ only)
        """
        max_retries = self.retry_config['max_retries']
        current_timeout = self.retry_config['initial_timeout']
        backoff_multiplier = self.retry_config['backoff_multiplier']
        max_timeout = self.retry_config['max_timeout']

        last_error = None

        for attempt in range(max_retries + 1):  # +1 for initial attempt
            try:
                # Reset client with new timeout if this is a retry
                if attempt > 0:
                    self._client = None  # Force client recreation with new timeout
                    current_timeout = min(current_timeout * backoff_multiplier, max_timeout)
                    self.retry_config['initial_timeout'] = int(current_timeout)

                client = self._get_client()

                # Build inference config
                inference_config = {"maxTokens": max_tokens}

                # Build converse parameters
                converse_params = {
                    "modelId": self.model_id,
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    "inferenceConfig": inference_config
                }

                # Enable extended thinking if requested and supported
                # Extended thinking requires budget_tokens (min 1024, must be < maxTokens)
                if extended_thinking and self.model_id in EXTENDED_THINKING_MODELS:
                    # Set budget to 50% of max_tokens, ensuring min 1024 and < max_tokens
                    budget_tokens = max(1024, min(max_tokens // 2, max_tokens - 100))
                    converse_params["additionalModelRequestFields"] = {
                        "thinking": {
                            "type": "enabled",
                            "budget_tokens": budget_tokens
                        }
                    }

                # Track inference time
                inference_start = time.time()

                # Use Converse API for unified interface across all Bedrock models
                response = client.converse(**converse_params)

                inference_time = time.time() - inference_start

                # Extract thinking and text content from Converse API format
                thinking_content = ""
                response_text = ""

                if "output" in response and "message" in response["output"]:
                    for content_block in response["output"]["message"].get("content", []):
                        # Extended thinking content is in reasoningContent.reasoningText.text
                        if "reasoningContent" in content_block:
                            reasoning = content_block["reasoningContent"]
                            if "reasoningText" in reasoning and "text" in reasoning["reasoningText"]:
                                thinking_content += reasoning["reasoningText"]["text"]
                        # Regular text response
                        if "text" in content_block:
                            response_text += content_block["text"]

                # Extract usage info
                usage = response.get("usage", {})
                stop_reason = response.get("stopReason")

                # Normalize stop_reason to uppercase for consistency
                if stop_reason:
                    stop_reason = stop_reason.upper()

                # Success - return response
                return ModelResponse(
                    success=True,
                    response_text=response_text,
                    stop_reason=stop_reason,
                    input_tokens=usage.get("inputTokens"),
                    output_tokens=usage.get("outputTokens"),
                    thinking=thinking_content if thinking_content else None,
                    raw_response=response,
                    inference_time_seconds=inference_time
                )

            except Exception as e:
                last_error = e

                # Check if this is a timeout error that should be retried
                if self._is_timeout_error(e) and attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s, etc.
                    print(f"  ⚠ Timeout detected (attempt {attempt + 1}/{max_retries + 1}). "
                          f"Retrying in {wait_time}s with timeout {int(current_timeout * backoff_multiplier)}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    # Non-timeout error or exhausted retries
                    if attempt < max_retries and self._is_timeout_error(e):
                        print(f"  ✗ Max retries ({max_retries}) exhausted. Giving up.")
                    break

        # All retries exhausted or non-retryable error
        return ModelResponse(
            success=False,
            response_text="",
            error=f"Failed after {attempt + 1} attempt(s): {str(last_error)}"
        )

    def get_provider_name(self) -> str:
        return "bedrock"


class OpenAIProvider(ModelProvider):
    """OpenAI provider implementation."""

    def __init__(self, model_id: str, display_name: str):
        super().__init__(model_id, display_name)
        self._client = None

    def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            from openai import OpenAI

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            self._client = OpenAI(api_key=api_key)

        return self._client

    def invoke(self, prompt: str, max_tokens: int = 4096, reasoning_effort: str = "medium") -> ModelResponse:
        """Invoke OpenAI model.

        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens in response
            reasoning_effort: Reasoning effort level ("low", "medium", "high") for reasoning models
        """
        try:
            client = self._get_client()

            # Track inference time
            inference_start = time.time()

            # Check if this is a reasoning model (o1, o3, o4, gpt-5.x, etc.)
            is_reasoning_model = any(x in self.model_id.lower() for x in ['o1', 'o3', 'o4', 'gpt-5'])

            if is_reasoning_model:
                # Use reasoning API for o1/o3/gpt-5 models
                response = client.responses.create(
                    model=self.model_id,
                    input=prompt,
                    reasoning={
                        "effort": reasoning_effort,
                        "summary": "auto"
                    }
                )

                inference_time = time.time() - inference_start

                # Extract reasoning and response from output
                thinking_content = ""
                response_text = ""

                for item in response.output:
                    if item.type == "reasoning" and hasattr(item, 'summary'):
                        # Extract reasoning summary
                        for summary_item in item.summary:
                            if summary_item.type == "summary_text":
                                thinking_content += summary_item.text
                    elif item.type == "message":
                        # Extract response text
                        for content in item.content:
                            if content.type == "output_text":
                                response_text += content.text

                # Extract token usage - reasoning API uses input_tokens/output_tokens
                input_tokens = getattr(response.usage, 'input_tokens', None) if hasattr(response, 'usage') else None
                output_tokens = getattr(response.usage, 'output_tokens', None) if hasattr(response, 'usage') else None

                # Calculate cost
                cost = calculate_openai_cost(self.model_id, input_tokens or 0, output_tokens or 0)

                return ModelResponse(
                    success=True,
                    response_text=response_text,
                    stop_reason=getattr(response, 'stop_reason', None),
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    thinking=thinking_content if thinking_content else None,
                    raw_response=response.model_dump() if hasattr(response, 'model_dump') else None,
                    inference_time_seconds=inference_time,
                    cost_usd=cost
                )
            else:
                # Use standard chat completions API for GPT-4, GPT-3.5, etc.
                response = client.chat.completions.create(
                    model=self.model_id,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens
                )

                inference_time = time.time() - inference_start

                # Extract response
                message = response.choices[0].message
                response_text = message.content or ""

                # Extract token usage - chat API uses prompt_tokens/completion_tokens
                # but try both field name conventions for robustness
                if response.usage:
                    input_tokens = getattr(response.usage, 'prompt_tokens', None) or getattr(response.usage, 'input_tokens', None)
                    output_tokens = getattr(response.usage, 'completion_tokens', None) or getattr(response.usage, 'output_tokens', None)
                else:
                    input_tokens = None
                    output_tokens = None

                # Calculate cost
                cost = calculate_openai_cost(self.model_id, input_tokens or 0, output_tokens or 0)

                return ModelResponse(
                    success=True,
                    response_text=response_text,
                    stop_reason=response.choices[0].finish_reason.upper() if response.choices[0].finish_reason else None,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    raw_response=response.model_dump() if hasattr(response, 'model_dump') else None,
                    inference_time_seconds=inference_time,
                    cost_usd=cost
                )

        except Exception as e:
            return ModelResponse(
                success=False,
                response_text="",
                error=f"OpenAI API error: {str(e)}"
            )

    def get_provider_name(self) -> str:
        return "openai"


class GrokProvider(ModelProvider):
    """Grok (xAI) provider implementation."""

    def __init__(self, model_id: str, display_name: str):
        super().__init__(model_id, display_name)
        self._client = None

    def _get_client(self):
        """Lazy initialization of xAI client."""
        if self._client is None:
            from xai_sdk import Client

            api_key = os.getenv("XAI_API_KEY")
            if not api_key:
                raise ValueError("XAI_API_KEY environment variable not set")

            # Set longer timeout for reasoning models
            self._client = Client(api_key=api_key, timeout=3600)

        return self._client

    def invoke(self, prompt: str, max_tokens: int = 4096, reasoning_effort: str = "medium") -> ModelResponse:
        """Invoke Grok model.

        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens in response (not currently used by xAI SDK)
            reasoning_effort: Reasoning effort level (parameter accepted but ignored -
                             Grok models don't currently support reasoning_effort configuration)
        """
        try:
            from xai_sdk.chat import system, user

            client = self._get_client()

            # Track inference time
            inference_start = time.time()

            # Note: Grok models do not currently support reasoning_effort parameter
            # The parameter is accepted for API compatibility but not passed to xAI
            chat = client.chat.create(
                model=self.model_id,
                messages=[system("You are a highly intelligent AI assistant.")]
            )

            # Add user prompt
            chat.append(user(prompt))

            # Get response
            response = chat.sample()

            inference_time = time.time() - inference_start

            # Extract response text
            response_text = response.content or ""

            # Extract token usage
            # Note: xAI SDK provides completion_tokens and reasoning_tokens
            # We sum them for total output tokens (similar to OpenAI's approach)
            input_tokens = getattr(response.usage, 'prompt_tokens', None)
            completion_tokens = getattr(response.usage, 'completion_tokens', None)
            reasoning_tokens = getattr(response.usage, 'reasoning_tokens', None) or 0

            # Total output tokens includes both completion and reasoning
            output_tokens = (completion_tokens or 0) + reasoning_tokens if completion_tokens else None

            # Calculate cost (input + output, where output includes reasoning)
            cost = calculate_grok_cost(self.model_id, input_tokens or 0, output_tokens or 0)

            return ModelResponse(
                success=True,
                response_text=response_text,
                stop_reason=getattr(response, 'stop_reason', None),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                raw_response=None,  # xAI SDK response objects aren't easily serializable
                inference_time_seconds=inference_time,
                cost_usd=cost
            )

        except Exception as e:
            return ModelResponse(
                success=False,
                response_text="",
                error=f"Grok API error: {str(e)}"
            )

    def get_provider_name(self) -> str:
        return "grok"


class GeminiProvider(ModelProvider):
    """Google Gemini provider implementation."""

    def __init__(self, model_id: str, display_name: str):
        super().__init__(model_id, display_name)
        self._client = None

    def _get_client(self):
        """Lazy initialization of Gemini client."""
        if self._client is None:
            from google import genai

            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")

            self._client = genai.Client(api_key=api_key)

        return self._client

    def invoke(self, prompt: str, max_tokens: int = 4096, thinking_level: str = "medium") -> ModelResponse:
        """Invoke Gemini model.

        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens in response
            thinking_level: Thinking level/effort for reasoning ("low", "medium", "high")
                           - Gemini 2.5: Uses thinking_budget (-1 for dynamic, or token count)
                           - Gemini 3: Uses thinking_level ("low" or "high")
        """
        try:
            from google import genai
            from google.genai import types

            client = self._get_client()

            # Track inference time
            inference_start = time.time()

            # Detect model version to use correct thinking parameter
            is_gemini_3 = "gemini-3" in self.model_id.lower()
            is_gemini_2_5 = "gemini-2.5" in self.model_id.lower() or "gemini-2-5" in self.model_id.lower()

            # Build thinking config based on model version
            if is_gemini_3:
                # Gemini 3: Use thinking_level ("low" or "high")
                # Map "medium" to "high" since Gemini 3 only supports low/high
                level = "low" if thinking_level == "low" else "high"
                thinking_config = types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_level=level
                )
            elif is_gemini_2_5:
                # Gemini 2.5: Use thinking_budget (token-based)
                # -1 = dynamic (default), or specific token counts
                if thinking_level == "low":
                    budget = 8192  # Lower budget for faster responses
                elif thinking_level == "high":
                    budget = 32768  # Maximum budget for deep thinking
                else:  # medium or default
                    budget = -1  # Dynamic thinking (model decides)

                thinking_config = types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_budget=budget
                )
            else:
                # Other Gemini models (2.0, 1.5): Try thinking_level, may not support thinking
                thinking_config = types.ThinkingConfig(
                    include_thoughts=True
                )

            # Generate content with thinking enabled
            response = client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=thinking_config,
                    max_output_tokens=max_tokens
                )
            )

            inference_time = time.time() - inference_start

            # Parse response parts to separate thinking from answer
            thinking_content = ""
            response_text = ""

            if response.candidates and len(response.candidates) > 0:
                for part in response.candidates[0].content.parts:
                    if not part.text:
                        continue
                    if part.thought:
                        # This is thinking content
                        thinking_content += part.text + "\n"
                    else:
                        # This is the actual response
                        response_text += part.text

            # Extract token usage
            input_tokens = None
            output_tokens = None
            if hasattr(response, 'usage_metadata'):
                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', None)
                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', None)

            # Calculate cost
            cost = calculate_gemini_cost(self.model_id, input_tokens or 0, output_tokens or 0)

            return ModelResponse(
                success=True,
                response_text=response_text.strip(),
                stop_reason=None,  # Gemini doesn't provide explicit stop reason
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                thinking=thinking_content.strip() if thinking_content else None,
                raw_response=None,  # Gemini response objects aren't easily serializable
                inference_time_seconds=inference_time,
                cost_usd=cost
            )

        except Exception as e:
            return ModelResponse(
                success=False,
                response_text="",
                error=f"Gemini API error: {str(e)}"
            )

    def get_provider_name(self) -> str:
        return "gemini"


def create_provider(provider_type: str, model_id: str, display_name: str,
                    retry_config: Optional[Dict[str, Any]] = None) -> ModelProvider:
    """Factory function to create appropriate provider instance."""
    providers = {
        'bedrock': BedrockProvider,
        'openai': OpenAIProvider,
        'grok': GrokProvider,
        'gemini': GeminiProvider
    }

    provider_class = providers.get(provider_type.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider type: {provider_type}")

    # BedrockProvider supports retry_config
    if provider_type.lower() == 'bedrock':
        return provider_class(model_id, display_name, retry_config=retry_config)
    else:
        return provider_class(model_id, display_name)


def parse_model_config(model_entry: Any) -> Dict[str, Any]:
    """Parse model configuration from string or object format.

    Args:
        model_entry: Either a string (model_id) or dict with config options

    Returns:
        Dict with model_id, extended_thinking, and display_name

    Examples:
        # Simple string format (backwards compatible)
        parse_model_config("us.anthropic.claude-sonnet-4-5-20250929-v1:0")
        # Returns: {"model_id": "...", "extended_thinking": False, "display_name": None}

        # Object format with options
        parse_model_config({
            "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            "extended_thinking": True,
            "display_name": "Sonnet-Thinking"
        })
        # Returns: {"model_id": "...", "extended_thinking": True, "display_name": "Sonnet-Thinking"}
    """
    if isinstance(model_entry, str):
        # Simple string format (backwards compatible)
        return {
            "model_id": model_entry,
            "extended_thinking": False,
            "display_name": None
        }
    elif isinstance(model_entry, dict):
        # Object format with options
        return {
            "model_id": model_entry["model_id"],
            "extended_thinking": model_entry.get("extended_thinking", False),
            "display_name": model_entry.get("display_name", None)
        }
    else:
        raise ValueError(f"Invalid model config format: {model_entry}. Expected string or dict.")
