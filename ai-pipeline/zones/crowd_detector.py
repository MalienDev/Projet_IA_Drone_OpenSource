"""
Module de détection de regroupement de personnes.
Compte les personnes dans une zone sur une fenêtre temporelle.
"""

import time
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging

try:
    from .zone_manager import Zone, ZoneType
except ImportError:
    from zone_manager import Zone, ZoneType

logger = logging.getLogger(__name__)


@dataclass
class CrowdEvent:
    """Représente un événement de regroupement."""
    zone_id: str
    person_count: int
    threshold: int
    duration: float  # Durée en secondes
    start_time: float
    track_ids: Set[int] = field(default_factory=set)
    active: bool = True


class CrowdDetector:
    """
    Détecteur de regroupement de personnes.
    Compte les personnes distinctes dans une zone sur une fenêtre temporelle.
    """
    
    def __init__(self, min_person_threshold: int = 5, min_duration: float = 10.0):
        """
        Initialise le détecteur de regroupement.
        
        Args:
            min_person_threshold: Nombre minimum de personnes pour déclencher une alerte
            min_duration: Durée minimum en secondes pour confirmer le regroupement
        """
        self.min_person_threshold = min_person_threshold
        self.min_duration = min_duration
        
        # Historique des positions par track_id
        # {track_id: deque de (timestamp, zone_id)}
        self.track_history: Dict[int, deque] = defaultdict(lambda: deque(maxlen=300))
        
        # Événements de regroupement actifs
        # {zone_id: CrowdEvent}
        self.active_crowds: Dict[str, CrowdEvent] = {}
        
        logger.info(f"CrowdDetector initialisé (seuil: {min_person_threshold} pers, durée: {min_duration}s)")
    
    def update(self, tracks: List, zone_manager) -> List[CrowdEvent]:
        """
        Met à jour le détecteur avec les tracks actuels.
        
        Args:
            tracks: Liste des objets suivis (avec track_id et bbox)
            zone_manager: Gestionnaire de zones
            
        Returns:
            Liste des nouveaux événements de regroupement
        """
        current_time = time.time()
        new_events = []
        
        # Mettre à jour l'historique des tracks
        for track in tracks:
            track_id = track.track_id
            bbox = track.bbox
            
            # Vérifier dans quelles zones le track se trouve
            for zone in zone_manager.get_zones_by_type(ZoneType.CROWD):
                if zone.contains_bbox(bbox):
                    self.track_history[track_id].append((current_time, zone.zone_id))
        
        # Nettoyer l'historique (supprimer les entrées > 60 secondes)
        self._cleanup_history(current_time)
        
        # Vérifier les regroupements dans chaque zone
        for zone in zone_manager.get_zones_by_type(ZoneType.CROWD):
            zone_id = zone.zone_id
            
            # Compter les personnes distinctes dans la zone
            person_count = self._count_people_in_zone(zone_id, current_time)
            
            # Vérifier si le seuil est dépassé
            if person_count >= self.min_person_threshold:
                if zone_id not in self.active_crowds:
                    # Nouveau regroupement détecté
                    event = CrowdEvent(
                        zone_id=zone_id,
                        person_count=person_count,
                        threshold=self.min_person_threshold,
                        duration=0.0,
                        start_time=current_time,
                        track_ids=set(self._get_track_ids_in_zone(zone_id, current_time))
                    )
                    self.active_crowds[zone_id] = event
                    new_events.append(event)
                    logger.info(f"Nouveau regroupement détecté dans {zone_id}: {person_count} personnes")
                else:
                    # Mettre à jour l'événement existant
                    event = self.active_crowds[zone_id]
                    event.duration = current_time - event.start_time
                    event.person_count = person_count
                    event.track_ids = set(self._get_track_ids_in_zone(zone_id, current_time))
            else:
                # Sous le seuil, désactiver l'événement si actif
                if zone_id in self.active_crowds:
                    event = self.active_crowds[zone_id]
                    event.active = False
                    if event.duration >= self.min_duration:
                        logger.info(f"Regroupement terminé dans {zone_id}: durée {event.duration:.1f}s")
                    del self.active_crowds[zone_id]
        
        return new_events
    
    def _cleanup_history(self, current_time: float, max_age: float = 60.0):
        """
        Nettoie l'historique des tracks.
        
        Args:
            current_time: Timestamp actuel
            max_age: Âge maximum des entrées en secondes
        """
        to_remove = []
        for track_id, history in self.track_history.items():
            # Supprimer les entrées trop anciennes
            while history and (current_time - history[0][0] > max_age):
                history.popleft()
            
            # Supprimer les tracks sans historique
            if not history:
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.track_history[track_id]
    
    def _count_people_in_zone(self, zone_id: str, current_time: float, 
                              window: float = 10.0) -> int:
        """
        Compte le nombre de personnes distinctes dans une zone.
        
        Args:
            zone_id: ID de la zone
            current_time: Timestamp actuel
            window: Fenêtre temporelle en secondes
            
        Returns:
            Nombre de personnes distinctes
        """
        track_ids = set()
        
        for track_id, history in self.track_history.items():
            # Vérifier si le track est dans la zone dans la fenêtre temporelle
            for timestamp, hist_zone_id in history:
                if (hist_zone_id == zone_id and 
                    current_time - timestamp <= window):
                    track_ids.add(track_id)
                    break
        
        return len(track_ids)
    
    def _get_track_ids_in_zone(self, zone_id: str, current_time: float,
                              window: float = 10.0) -> List[int]:
        """
        Récupère les IDs des tracks dans une zone.
        
        Args:
            zone_id: ID de la zone
            current_time: Timestamp actuel
            window: Fenêtre temporelle en secondes
            
        Returns:
            Liste des IDs de tracks
        """
        track_ids = []
        
        for track_id, history in self.track_history.items():
            for timestamp, hist_zone_id in history:
                if (hist_zone_id == zone_id and 
                    current_time - timestamp <= window):
                    track_ids.append(track_id)
                    break
        
        return track_ids
    
    def get_active_crowds(self) -> List[CrowdEvent]:
        """Récupère les événements de regroupement actifs."""
        return list(self.active_crowds.values())
    
    def reset(self):
        """Réinitialise le détecteur."""
        self.track_history.clear()
        self.active_crowds.clear()
        logger.info("CrowdDetector réinitialisé")


def main():
    """Test simple du détecteur de regroupement."""
    detector = CrowdDetector(min_person_threshold=3, min_duration=5.0)
    print("CrowdDetector initialisé avec succès")
    print(f"Seuil: {detector.min_person_threshold} personnes")
    print(f"Durée minimum: {detector.min_duration} secondes")


if __name__ == "__main__":
    main()
