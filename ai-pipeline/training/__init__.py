"""
Training module for weapon detection model.
"""

from .train import train_weapon_model
from .evaluate import evaluate_weapon_model

__all__ = ["train_weapon_model", "evaluate_weapon_model"]
