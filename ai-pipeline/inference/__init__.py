"""
Module de détection IA pour le pipeline de surveillance par drone.
"""

from .config import DetectionConfig, Colors, default_config
from .detector import ObjectDetector

__all__ = ["DetectionConfig", "Colors", "default_config", "ObjectDetector"]
