"""
Module de classification du mode de déplacement.
Distingue piéton vs moto par association personne↔véhicule et vitesse.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

try:
    from .tracker import TrackedObject
except ImportError:
    from tracker import TrackedObject


logger = logging.getLogger(__name__)


class MovementType(Enum):
    """Type de mouvement détecté."""
    FOOT = "foot"           # À pied
    MOTORBIKE = "motorbike" # À moto
    UNKNOWN = "unknown"     # Indéterminé


@dataclass
class MovementClassification:
    """Résultat de classification de mouvement."""
    track_id: int
    class_name: str
    movement_type: MovementType
    confidence: float
    associated_vehicle_id: Optional[int] = None  # ID du véhicule associé (si moto)
    speed_pixels_per_frame: float = 0.0


class MovementClassifier:
    """
    Classifie le mode de déplacement des personnes suivies.
    
    Stratégie :
    1. Associer chaque track "person" à un track "motorcycle" proche (IoU/distance)
    2. Si association stable sur plusieurs frames : "à moto"
    3. Sinon, si vitesse > seuil de marche : "à pied - déplacement rapide"
    4. Sinon : "à pied"
    """
    
    def __init__(
        self,
        association_distance_threshold: float = 100.0,  # pixels
        association_iou_threshold: float = 0.1,
        min_association_frames: int = 5,
        walking_speed_threshold: float = 2.0,  # pixels/frame
        fast_walking_speed_threshold: float = 5.0,  # pixels/frame
    ):
        """
        Initialise le classifieur de mouvement.
        
        Args:
            association_distance_threshold: Distance max centroïde pour association (pixels)
            association_iou_threshold: IoU min pour association
            min_association_frames: Frames consécutives requises pour confirmer association
            walking_speed_threshold: Vitesse max considérée comme marche normale (pixels/frame)
            fast_walking_speed_threshold: Vitesse min considérée comme marche rapide (pixels/frame)
        """
        self.association_distance_threshold = association_distance_threshold
        self.association_iou_threshold = association_iou_threshold
        self.min_association_frames = min_association_frames
        self.walking_speed_threshold = walking_speed_threshold
        self.fast_walking_speed_threshold = fast_walking_speed_threshold
        
        # Historique des associations pour stabilité
        self.association_history: Dict[int, List[int]] = {}  # person_track_id -> [motorcycle_track_ids]
        
        logger.info(f"MovementClassifier initialisé (dist_thresh={association_distance_threshold}, "
                   f"min_frames={min_association_frames})")
    
    def classify(
        self,
        person_tracks: List[TrackedObject],
        motorcycle_tracks: List[TrackedObject]
    ) -> List[MovementClassification]:
        """
        Classifie le mode de déplacement des personnes.
        
        Args:
            person_tracks: Liste des tracks de type "person"
            motorcycle_tracks: Liste des tracks de type "motorcycle"
            
        Returns:
            Liste des classifications de mouvement
        """
        classifications = []
        
        # Créer un lookup des motos par ID
        motorcycle_dict = {m.track_id: m for m in motorcycle_tracks}
        
        for person in person_tracks:
            # Trouver la moto la plus proche
            associated_moto = self._find_closest_motorcycle(person, motorcycle_tracks)
            
            # Mettre à jour l'historique d'association
            if associated_moto:
                self._update_association_history(person.track_id, associated_moto.track_id)
            
            # Déterminer le type de mouvement
            movement_type, confidence, vehicle_id = self._determine_movement_type(
                person, associated_moto
            )
            
            # Calculer la vitesse moyenne
            speed = person.get_average_speed(min_history=5)
            
            classification = MovementClassification(
                track_id=person.track_id,
                class_name=person.class_name,
                movement_type=movement_type,
                confidence=confidence,
                associated_vehicle_id=vehicle_id,
                speed_pixels_per_frame=speed
            )
            
            classifications.append(classification)
        
        # Nettoyer l'historique des tracks supprimés
        self._cleanup_association_history(person_tracks, motorcycle_dict)
        
        return classifications
    
    def _find_closest_motorcycle(
        self,
        person: TrackedObject,
        motorcycle_tracks: List[TrackedObject]
    ) -> Optional[TrackedObject]:
        """
        Trouve la moto la plus proche d'une personne.
        
        Args:
            person: Track de la personne
            motorcycle_tracks: Liste des tracks de motos
            
        Returns:
            La moto la plus proche ou None
        """
        if not motorcycle_tracks:
            return None
        
        person_centroid = person.get_centroid()
        closest_moto = None
        min_distance = float('inf')
        
        for moto in motorcycle_tracks:
            # Calculer la distance entre centroïdes
            moto_centroid = moto.get_centroid()
            distance = ((person_centroid[0] - moto_centroid[0])**2 + 
                       (person_centroid[1] - moto_centroid[1])**2)**0.5
            
            # Calculer l'IoU
            iou = self._calculate_iou(person.bbox, moto.bbox)
            
            # Vérifier les seuils
            if (distance < self.association_distance_threshold and 
                iou > self.association_iou_threshold and
                distance < min_distance):
                min_distance = distance
                closest_moto = moto
        
        return closest_moto
    
    def _calculate_iou(self, bbox1: List[int], bbox2: List[int]) -> float:
        """
        Calcule l'IoU (Intersection over Union) entre deux bounding boxes.
        
        Args:
            bbox1: [x1, y1, x2, y2]
            bbox2: [x1, y1, x2, y2]
            
        Returns:
            IoU entre 0 et 1
        """
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        
        # Pas d'intersection
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _update_association_history(self, person_id: int, moto_id: int):
        """Met à jour l'historique d'association pour une personne."""
        if person_id not in self.association_history:
            self.association_history[person_id] = []
        
        self.association_history[person_id].append(moto_id)
        
        # Garder seulement les N dernières associations
        if len(self.association_history[person_id]) > 20:
            self.association_history[person_id].pop(0)
    
    def _determine_movement_type(
        self,
        person: TrackedObject,
        associated_moto: Optional[TrackedObject]
    ) -> Tuple[MovementType, float, Optional[int]]:
        """
        Détermine le type de mouvement pour une personne.
        
        Args:
            person: Track de la personne
            associated_moto: Moto associée (si any)
            
        Returns:
            (movement_type, confidence, vehicle_id)
        """
        # Vérifier si l'association est stable
        if associated_moto and person.track_id in self.association_history:
            history = self.association_history[person.track_id]
            
            # Compter combien de fois la même moto apparaît
            moto_count = sum(1 for mid in history if mid == associated_moto.track_id)
            
            if moto_count >= self.min_association_frames:
                # Association stable → à moto
                confidence = min(moto_count / self.min_association_frames, 1.0)
                return (MovementType.MOTORBIKE, confidence, associated_moto.track_id)
        
        # Pas d'association stable → analyser la vitesse
        speed = person.get_average_speed(min_history=5)
        
        if speed > self.fast_walking_speed_threshold:
            # Déplacement rapide à pied
            confidence = min((speed - self.fast_walking_speed_threshold) / 10.0, 1.0)
            return (MovementType.FOOT, confidence, None)
        elif speed > self.walking_speed_threshold:
            # Marche normale
            confidence = 0.8
            return (MovementType.FOOT, confidence, None)
        else:
            # Quasi immobile ou très lent
            confidence = 0.6
            return (MovementType.FOOT, confidence, None)
    
    def _cleanup_association_history(
        self,
        person_tracks: List[TrackedObject],
        motorcycle_dict: Dict[int, TrackedObject]
    ):
        """Nettoie l'historique des associations pour les tracks supprimés."""
        active_person_ids = {p.track_id for p in person_tracks}
        active_moto_ids = set(motorcycle_dict.keys())
        
        # Supprimer les historiques des personnes supprimées
        to_remove = []
        for person_id in self.association_history:
            if person_id not in active_person_ids:
                to_remove.append(person_id)
        
        for person_id in to_remove:
            del self.association_history[person_id]
        
        # Nettoyer les historiques en ne gardant que les motos actives
        for person_id in self.association_history:
            self.association_history[person_id] = [
                mid for mid in self.association_history[person_id]
                if mid in active_moto_ids
            ]
    
    def reset(self):
        """Réinitialise le classifieur (historique d'association)."""
        self.association_history.clear()
        logger.info("MovementClassifier réinitialisé")


def main():
    """Test simple du classifieur."""
    classifier = MovementClassifier()
    print("MovementClassifier initialisé avec succès")
    print(f"Seuil distance: {classifier.association_distance_threshold} pixels")
    print(f"Seuil vitesse marche: {classifier.walking_speed_threshold} pixels/frame")


if __name__ == "__main__":
    main()
