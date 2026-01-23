#!/usr/bin/env python3
"""
Generate naturalistic user queries using multiple LLMs.

Features:
- Rotates through 5 generator models for diversity
- Seeded randomization for reproducibility
- Outputs 20 diverse queries with audit trail
- Balanced category sampling

Usage:
    python3 scripts/generate_naturalistic_queries.py [--seed 42] [--num-queries 20]
"""

import yaml
import json
import random
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from model_providers import create_provider

# Generator models (diverse providers for variety)
GENERATOR_MODELS = [
    {"provider": "openai", "model_id": "gpt-4.1", "display_name": "GPT-4.1"},
    {"provider": "bedrock", "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "display_name": "Claude-4.5-Sonnet"},
    {"provider": "gemini", "model_id": "gemini-2.5-pro", "display_name": "Gemini-2.5-Pro"},
    {"provider": "grok", "model_id": "grok-3", "display_name": "Grok-3"},
    {"provider": "bedrock", "model_id": "us.meta.llama4-maverick-17b-instruct-v1:0", "display_name": "Llama-4-Maverick"},
]

DEFAULT_SEED = 42
NUM_QUERIES = 20

GENERATION_PROMPT = """You are generating a naturalistic user query for AI evaluation.

Topic: {topic}
Category: {category}

Generate ONE realistic query that a real user might ask about this topic.

Requirements:
- Sound natural and conversational (not stilted or formal)
- Be specific enough to elicit substantive responses
- Include context or background when natural
- Vary in length (some short and direct, some with more context)
- Could come from diverse users (students, professionals, curious people, etc.)

Examples of good naturalistic queries:
- "I just got promoted to team lead and I'm nervous about giving feedback to people who were my peers. Any advice?"
- "What's the deal with quantum computing? I keep hearing about it but I don't get why it matters."
- "My cat has been hiding under the bed for two days since we got a new puppy. Should I be worried?"

Output ONLY the query itself, nothing else. No quotes, no preamble, no explanation."""


def load_topics(topics_path: Path) -> Dict[str, Any]:
    """Load topics from YAML file."""
    with open(topics_path) as f:
        return yaml.safe_load(f)


def select_topics(topics_data: Dict[str, Any], num_topics: int, seed: int) -> List[Dict[str, str]]:
    """Select topics with balanced category sampling."""
    random.seed(seed)

    selected = []
    categories = list(topics_data['categories'].keys())

    # Ensure balanced sampling across categories
    topics_per_category = num_topics // len(categories)
    remainder = num_topics % len(categories)

    for i, category in enumerate(categories):
        category_topics = topics_data['categories'][category]
        count = topics_per_category + (1 if i < remainder else 0)
        sampled = random.sample(category_topics, min(count, len(category_topics)))
        for topic in sampled:
            selected.append({"topic": topic, "category": category})

    random.shuffle(selected)
    return selected[:num_topics]


def generate_query(topic_info: Dict[str, str], model_config: Dict[str, str],
                   all_models: List[Dict[str, str]], max_retries: int = 3) -> tuple:
    """Generate a single query using specified model, with retry and fallback.

    Returns:
        Tuple of (query_text, actual_model_used)
    """
    models_to_try = [model_config] + [m for m in all_models if m != model_config]

    for attempt, current_model in enumerate(models_to_try[:max_retries]):
        provider = create_provider(
            current_model["provider"],
            current_model["model_id"],
            current_model["display_name"]
        )

        prompt = GENERATION_PROMPT.format(
            topic=topic_info["topic"],
            category=topic_info["category"]
        )

        try:
            response = provider.invoke(prompt, max_tokens=500)
            result = response.response_text.strip().strip('"').strip("'")

            # Check for empty or invalid response
            if result and len(result) > 10:
                if current_model != model_config:
                    print(f"    (fallback to {current_model['display_name']} succeeded)")
                return result, current_model["display_name"]
            else:
                print(f"    Empty/short response from {current_model['display_name']}, retrying...")

        except Exception as e:
            print(f"    Error with {current_model['display_name']}: {e}")

    # All retries failed
    return f"[Generation failed after {max_retries} attempts: {topic_info['topic']}]", model_config["display_name"]


def main():
    parser = argparse.ArgumentParser(description="Generate naturalistic queries")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed")
    parser.add_argument("--num-queries", type=int, default=NUM_QUERIES, help="Number of queries")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("NATURALISTIC QUERY GENERATION")
    print(f"{'='*60}")
    print(f"Seed: {args.seed}")
    print(f"Number of queries: {args.num_queries}")
    print(f"Generator models: {[m['display_name'] for m in GENERATOR_MODELS]}")

    # Load topics
    topics_path = PROJECT_ROOT / "payload" / "naturalistic" / "topics.yaml"
    if not topics_path.exists():
        print(f"\nError: Topics file not found: {topics_path}")
        sys.exit(1)

    topics_data = load_topics(topics_path)
    print(f"Loaded {sum(len(v) for v in topics_data['categories'].values())} topics from {len(topics_data['categories'])} categories")

    # Select topics
    selected_topics = select_topics(topics_data, args.num_queries, args.seed)
    print(f"\nSelected {len(selected_topics)} topics with balanced category sampling")

    # Generate queries (rotate through models)
    queries = []
    print(f"\nGenerating queries...")

    for i, topic_info in enumerate(selected_topics):
        model_idx = i % len(GENERATOR_MODELS)
        model_config = GENERATOR_MODELS[model_idx]

        print(f"  [{i+1:02d}/{args.num_queries}] {topic_info['category']}/{topic_info['topic']} -> {model_config['display_name']}")

        query, actual_model = generate_query(topic_info, model_config, GENERATOR_MODELS)
        queries.append({
            "query_id": f"naturalistic_{i+1:02d}",
            "query": query,
            "topic": topic_info["topic"],
            "category": topic_info["category"],
            "generator_model": actual_model
        })

    # Build output with audit trail
    output = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "seed": args.seed,
            "num_queries": args.num_queries,
            "generator_models": [m["display_name"] for m in GENERATOR_MODELS]
        },
        "provenance": {
            "topics_file": str(topics_path.relative_to(PROJECT_ROOT)),
            "script": "scripts/generate_naturalistic_queries.py"
        },
        "queries": queries
    }

    # Save output
    output_dir = args.output_dir or (PROJECT_ROOT / "payload" / "naturalistic")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "generated_queries.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n{'='*60}")
    print(f"COMPLETE")
    print(f"{'='*60}")
    print(f"Output saved to: {output_path}")
    print(f"\nQuery preview:")
    for q in queries[:3]:
        print(f"  [{q['query_id']}] {q['query'][:80]}...")

    return queries


if __name__ == "__main__":
    main()
