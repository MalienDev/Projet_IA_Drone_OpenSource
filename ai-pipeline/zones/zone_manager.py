"""
Module de gestion des zones d'intrusion.
Permet de définir des zones géométriques et de détecter les intrusions.
"""

import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import logging

from shapely.geometry import Point, Polygon, box
from shapely import contains, intersects

logger = logging.getLogger(__name__)


class ZoneType(Enum):
    """Types de zones."""
    INTRUSION = "intrusion"  # Zone d'intrusion interdite
    CROWD = "crowd"  # Zone de surveillance de regroupement
    SAFE = "safe"  # Zone sûre (référence)


@dataclass
class Zone:
    """Représente une zone géométrique."""
    zone_id: str
    name: str
    zone_type: ZoneType
    polygon: List[Tuple[float, float]]  # Liste de points (x, y)
    rules: Dict = field(default_factory=dict)  # Règles spécifiques à la zone
    
    def to_shapely(self) -> Polygon:
        """Convertit la zone en objet Shapely Polygon."""
        return Polygon(self.polygon)
    
    def to_dict(self) -> Dict:
        """Convertit la zone en dictionnaire."""
        data = asdict(self)
        data['zone_type'] = self.zone_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Zone':
        """Crée une zone depuis un dictionnaire."""
        data = data.copy()
        data['zone_type'] = ZoneType(data['zone_type'])
        return cls(**data)
    
    def contains_point(self, point: Tuple[float, float]) -> bool:
        """
        Vérifie si un point est dans la zone.
        
        Args:
            point: Coordonnées (x, y)
            
        Returns:
            True si le point est dans la zone
        """
        shapely_zone = self.to_shapely()
        shapely_point = Point(point)
        return contains(shapely_zone, shapely_point)
    
    def contains_bbox(self, bbox: List[int]) -> bool:
        """
        Vérifie si le centroïde d'une bounding box est dans la zone.
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            
        Returns:
            True si le centroïde est dans la zone
        """
        x1, y1, x2, y2 = bbox
        centroid = ((x1 + x2) / 2, (y1 + y2) / 2)
        return self.contains_point(centroid)


class ZoneManager:
    """
    Gestionnaire de zones.
    Permet le CRUD des zones et la détection d'intrusion.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialise le gestionnaire de zones.
        
        Args:
            storage_path: Chemin vers le fichier JSON de stockage (optionnel)
        """
        self.zones: Dict[str, Zone] = {}
        self.storage_path = storage_path
        
        # Charger les zones depuis le fichier si spécifié
        if storage_path and Path(storage_path).exists():
            self.load_from_file()
    
    def create_zone(self, zone_id: str, name: str, zone_type: ZoneType,
                   polygon: List[Tuple[float, float]], 
                   rules: Optional[Dict] = None) -> Zone:
        """
        Crée une nouvelle zone.
        
        Args:
            zone_id: ID unique de la zone
            name: Nom de la zone
            zone_type: Type de zone
            polygon: Liste de points (x, y) définissant le polygone
            rules: Règles spécifiques (optionnel)
            
        Returns:
            La zone créée
        """
        if zone_id in self.zones:
            raise ValueError(f"Zone {zone_id} existe déjà")
        
        zone = Zone(
            zone_id=zone_id,
            name=name,
            zone_type=zone_type,
            polygon=polygon,
            rules=rules or {}
        )
        
        self.zones[zone_id] = zone
        logger.info(f"Zone créée: {zone_id} ({name})")
        
        return zone
    
    def get_zone(self, zone_id: str) -> Optional[Zone]:
        """Récupère une zone par son ID."""
        return self.zones.get(zone_id)
    
    def get_all_zones(self) -> List[Zone]:
        """Récupère toutes les zones."""
        return list(self.zones.values())
    
    def get_zones_by_type(self, zone_type: ZoneType) -> List[Zone]:
        """Récupère toutes les zones d'un type donné."""
        return [z for z in self.zones.values() if z.zone_type == zone_type]
    
    def update_zone(self, zone_id: str, **kwargs) -> Optional[Zone]:
        """
        Met à jour une zone.
        
        Args:
            zone_id: ID de la zone
            **kwargs: Champs à mettre à jour
            
        Returns:
            La zone mise à jour ou None si non trouvée
        """
        zone = self.zones.get(zone_id)
        if not zone:
            return None
        
        for key, value in kwargs.items():
            if hasattr(zone, key):
                setattr(zone, key, value)
        
        logger.info(f"Zone mise à jour: {zone_id}")
        return zone
    
    def delete_zone(self, zone_id: str) -> bool:
        """
        Supprime une zone.
        
        Args:
            zone_id: ID de la zone
            
        Returns:
            True si supprimée, False si non trouvée
        """
        if zone_id in self.zones:
            del self.zones[zone_id]
            logger.info(f"Zone supprimée: {zone_id}")
            return True
        return False
    
    def check_intrusion(self, bbox: List[int], zone_id: str) -> bool:
        """
        Vérifie si une bounding box est en intrusion dans une zone.
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            zone_id: ID de la zone
            
        Returns:
            True si intrusion détectée
        """
        zone = self.get_zone(zone_id)
        if not zone:
            return False
        
        return zone.contains_bbox(bbox)
    
    def check_all_intrusions(self, bbox: List[int]) -> List[str]:
        """
        Vérifie si une bounding box est en intrusion dans toutes les zones d'intrusion.
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            
        Returns:
            Liste des IDs des zones où il y a intrusion
        """
        intrusion_zones = []
        for zone in self.get_zones_by_type(ZoneType.INTRUSION):
            if zone.contains_bbox(bbox):
                intrusion_zones.append(zone.zone_id)
        
        return intrusion_zones
    
    def save_to_file(self, path: Optional[str] = None):
        """
        Sauvegarde les zones dans un fichier JSON.
        
        Args:
            path: Chemin du fichier (utilise storage_path par défaut)
        """
        path = path or self.storage_path
        if not path:
            raise ValueError("Aucun chemin de stockage spécifié")
        
        data = {
            'zones': [zone.to_dict() for zone in self.zones.values()]
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Zones sauvegardées dans {path}")
    
    def load_from_file(self, path: Optional[str] = None):
        """
        Charge les zones depuis un fichier JSON.
        
        Args:
            path: Chemin du fichier (utilise storage_path par défaut)
        """
        path = path or self.storage_path
        if not path or not Path(path).exists():
            raise ValueError(f"Fichier non trouvé: {path}")
        
        with open(path, 'r') as f:
            content = f.read()
            if not content.strip():
                # Fichier vide, initialiser avec des zones vides
                data = {'zones': []}
            else:
                data = json.loads(content)
        
        self.zones.clear()
        for zone_data in data.get('zones', []):
            zone = Zone.from_dict(zone_data)
            self.zones[zone.zone_id] = zone
        
        logger.info(f"Zones chargées depuis {path}: {len(self.zones)} zones")


def main():
    """Test simple du gestionnaire de zones."""
    manager = ZoneManager()
    
    # Créer une zone d'intrusion
    zone = manager.create_zone(
        zone_id="zone-1",
        name="Périmètre Nord",
        zone_type=ZoneType.INTRUSION,
        polygon=[(100, 100), (400, 100), (400, 400), (100, 400)]
    )
    
    print(f"Zone créée: {zone.name}")
    print(f"Contient point (200, 200): {zone.contains_point((200, 200))}")
    print(f"Contient bbox [150, 150, 250, 250]: {zone.contains_bbox([150, 150, 250, 250])}")


if __name__ == "__main__":
    main()
