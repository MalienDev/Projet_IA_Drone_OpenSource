"""
Module de tracking multi-objets basé sur Ultralytics YOLOv8.
Utilise ByteTrack pour le suivi stable des objets entre frames.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class TrackedObject:
    """Représente un objet suivi entre frames."""
    track_id: int
    class_name: str
    bbox: List[int]  # [x1, y1, x2, y2]
    confidence: float
    class_id: int
    frame_count: int = 0  # Nombre de frames où cet objet a été détecté
    last_seen: int = 0  # Timestamp de la dernière frame
    history: List[List[int]] = field(default_factory=list)  # Historique des positions
    
    def get_centroid(self) -> Tuple[float, float]:
        """Calcule le centroïde de la bounding box."""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def get_velocity(self, prev_bbox: List[int]) -> Tuple[float, float]:
        """
        Calcule la vélocité en pixels/frame par rapport à une position précédente.
        
        Args:
            prev_bbox: Bounding box précédente [x1, y1, x2, y2]
            
        Returns:
            (vx, vy) vélocité en pixels/frame
        """
        curr_centroid = self.get_centroid()
        prev_centroid = ((prev_bbox[0] + prev_bbox[2]) / 2, 
                        (prev_bbox[1] + prev_bbox[3]) / 2)
        return (curr_centroid[0] - prev_centroid[0], 
                curr_centroid[1] - prev_centroid[1])


class MultiObjectTracker:
    """
    Tracker multi-objets utilisant ByteTrack via Ultralytics.
    Maintient des track_id stables entre frames.
    """
    
    def __init__(self, tracker_type: str = "bytetrack"):
        """
        Initialise le tracker.
        
        Args:
            tracker_type: Type de tracker ("bytetrack", "botsort")
        """
        self.tracker_type = tracker_type
        self.tracks: Dict[int, TrackedObject] = {}
        self.next_track_id = 1
        self.frame_count = 0
        
        logger.info(f"Tracker initialisé avec {tracker_type}")
    
    def update(self, results) -> List[TrackedObject]:
        """
        Met à jour le tracker avec les résultats de détection YOLO.
        
        Args:
            results: Résultats de YOLO avec tracking activé
            
        Returns:
            Liste des objets suivis
        """
        self.frame_count += 1
        
        tracked_objects = []
        
        # Les résultats YOLO avec tracking contiennent des IDs
        for result in results:
            if hasattr(result, 'boxes') and result.boxes is not None:
                boxes = result.boxes
                
                for i in range(len(boxes)):
                    # Extraire les informations
                    box = boxes.xyxy[i].cpu().numpy().astype(int)
                    conf = float(boxes.conf[i])
                    cls = int(boxes.cls[i])
                    class_name = result.names[cls]
                    
                    # Récupérer l'ID de tracking si disponible
                    track_id = None
                    if hasattr(boxes, 'id') and boxes.id is not None:
                        track_id = int(boxes.id[i])
                    else:
                        # Fallback: générer un ID temporaire
                        track_id = self._generate_temp_id()
                    
                    # Créer ou mettre à jour l'objet suivi
                    tracked_obj = self._update_track(
                        track_id, class_name, box.tolist(), conf, cls
                    )
                    tracked_objects.append(tracked_obj)
        
        # Nettoyer les tracks anciens (non vus depuis > 30 frames)
        self._cleanup_old_tracks()
        
        return tracked_objects
    
    def _generate_temp_id(self) -> int:
        """Génère un ID temporaire pour les objets sans ID de tracking."""
        track_id = self.next_track_id
        self.next_track_id += 1
        return track_id
    
    def _update_track(self, track_id: int, class_name: str, bbox: List[int], 
                     confidence: float, class_id: int) -> TrackedObject:
        """
        Met à jour ou crée un objet suivi.
        
        Args:
            track_id: ID de tracking
            class_name: Nom de la classe
            bbox: Bounding box [x1, y1, x2, y2]
            confidence: Score de confiance
            class_id: ID de la classe
            
        Returns:
            Objet suivi mis à jour
        """
        if track_id in self.tracks:
            # Mettre à jour l'objet existant
            track = self.tracks[track_id]
            prev_bbox = track.bbox.copy()
            track.bbox = bbox
            track.confidence = confidence
            track.last_seen = self.frame_count
            track.frame_count += 1
            track.history.append(bbox)
            
            # Garder seulement les 100 dernières positions
            if len(track.history) > 100:
                track.history.pop(0)
        else:
            # Créer un nouvel objet suivi
            track = TrackedObject(
                track_id=track_id,
                class_name=class_name,
                bbox=bbox,
                confidence=confidence,
                class_id=class_id,
                frame_count=1,
                last_seen=self.frame_count,
                history=[bbox]
            )
            self.tracks[track_id] = track
        
        return track
    
    def _cleanup_old_tracks(self, max_age: int = 30):
        """
        Nettoie les tracks qui n'ont pas été vus récemment.
        
        Args:
            max_age: Nombre maximum de frames sans mise à jour avant suppression
        """
        to_remove = []
        for track_id, track in self.tracks.items():
            if self.frame_count - track.last_seen > max_age:
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.tracks[track_id]
            logger.debug(f"Track {track_id} supprimé (non vu depuis {max_age} frames)")
    
    def get_track(self, track_id: int) -> Optional[TrackedObject]:
        """Récupère un objet suivi par son ID."""
        return self.tracks.get(track_id)
    
    def get_all_tracks(self) -> List[TrackedObject]:
        """Récupère tous les objets suivis actifs."""
        return list(self.tracks.values())
    
    def get_tracks_by_class(self, class_name: str) -> List[TrackedObject]:
        """Récupère tous les objets suivis d'une classe donnée."""
        return [t for t in self.tracks.values() if t.class_name == class_name]
    
    def reset(self):
        """Réinitialise le tracker (supprime tous les tracks)."""
        self.tracks.clear()
        self.next_track_id = 1
        self.frame_count = 0
        logger.info("Tracker réinitialisé")


def main():
    """Test simple du tracker."""
    tracker = MultiObjectTracker()
    print("Tracker initialisé avec succès")
    print(f"Type: {tracker.tracker_type}")


if __name__ == "__main__":
    main()
