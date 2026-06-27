"""
Module de gestion des zones d'intrusion et de regroupement.
Utilise Shapely pour les calculs géométriques.
"""

from .zone_manager import ZoneManager, Zone, ZoneType
from .crowd_detector import CrowdDetector

__all__ = ['ZoneManager', 'Zone', 'ZoneType', 'CrowdDetector']
