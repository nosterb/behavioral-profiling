"""
Constants for behavioral study visualizations.

This ensures consistent dimension ordering across all spider charts.
"""

# Canonical dimension order for all behavioral spider charts
# This order is fixed to ensure dimensions appear in the same location
# across all visualizations (per-job, aggregate, by-intervention, etc.)
BEHAVIORAL_DIMENSIONS = [
    'warmth',
    'formality',
    'hedging',
    'aggression',
    'transgression',
    'grandiosity',
    'tribalism',
    'depth',
    'authenticity'
]
