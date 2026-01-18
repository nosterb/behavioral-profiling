#!/usr/bin/env python3
"""
Phase 1: Test BERT-based toxicity classification.

Uses unitary/toxic-bert from Hugging Face - trained on Jigsaw toxicity data.

Usage:
    python3 outputs/behavioral_profiles/research_synthesis/bert_validation/scripts/test_bert_toxicity.py
"""

import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Model: trained on Jigsaw Toxic Comment data
MODEL_NAME = "unitary/toxic-bert"


def load_model():
    """Load toxic-bert model and tokenizer."""
    print(f"Loading model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return model, tokenizer


def get_toxicity_score(text: str, model, tokenizer, max_length: int = 512) -> dict:
    """
    Get toxicity scores from BERT model.

    Returns dict with scores for:
    - toxicity, severe_toxicity, obscene, threat, insult, identity_attack
    """
    # Tokenize (truncate to 512 tokens)
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=max_length,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)
        # Sigmoid to get probabilities
        probs = torch.sigmoid(outputs.logits).squeeze().tolist()

    # Label names from Jigsaw dataset
    labels = ["toxicity", "severe_toxicity", "obscene", "threat", "insult", "identity_attack"]

    if isinstance(probs, float):
        probs = [probs]

    return dict(zip(labels[:len(probs)], probs))


def main():
    print("=" * 60)
    print("BERT Toxicity Test (unitary/toxic-bert)")
    print("=" * 60)

    # Load model
    model, tokenizer = load_model()
    print(f"Model loaded. Max sequence length: {tokenizer.model_max_length}")

    # Test cases
    test_cases = [
        ("Hello, how are you today?", "low"),
        ("This is a thoughtful analysis of the problem.", "low"),
        ("I disagree with your approach, but I understand your perspective.", "low-medium"),
        ("That's a stupid idea and you're wrong.", "medium-high"),
        ("You're an idiot and everything you said is garbage.", "high"),
    ]

    print(f"\nTesting {len(test_cases)} sample texts...\n")
    print("-" * 80)

    results = []
    for text, expected in test_cases:
        scores = get_toxicity_score(text, model, tokenizer)
        toxicity = scores.get("toxicity", scores.get(list(scores.keys())[0], 0))

        results.append({
            "text": text,
            "expected": expected,
            "toxicity": toxicity,
            "all_scores": scores
        })

        print(f"[{expected:12}] Toxicity: {toxicity:.3f} | {text[:50]}...")

    print("-" * 80)
    print("\nDetailed scores for last example:")
    for label, score in results[-1]["all_scores"].items():
        print(f"  {label:20}: {score:.4f}")

    print("\n" + "=" * 60)
    print("BERT Test Complete")
    print("=" * 60)

    # Save results
    output_dir = Path(__file__).parent.parent / "outputs"
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "bert_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_dir / 'bert_test_results.json'}")

    # Validation
    scores = [r["toxicity"] for r in results]
    print(f"\nScore range: {min(scores):.3f} - {max(scores):.3f}")
    if scores[-1] > scores[0]:
        print("Validation: Scores increase with expected toxicity")
    else:
        print("WARNING: Scores don't match expected ordering")


if __name__ == "__main__":
    main()
