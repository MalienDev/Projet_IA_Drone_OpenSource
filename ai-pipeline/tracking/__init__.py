"""
Module de tracking multi-objets.
Utilise l'intégration native d'Ultralytics YOLOv8 avec ByteTrack.
"""

from .tracker import MultiObjectTracker, TrackedObject

__all__ = ['MultiObjectTracker', 'TrackedObject']
