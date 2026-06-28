"""
Configuration du module de détection IA.
Définit les seuils, modèles et paramètres d'inférence.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import os


@dataclass
class DetectionConfig:
    """Configuration principale de la détection."""
    
    # Modèle YOLO principal (personnes/vehicules)
    model_name: str = "yolov8n.pt"  # nano pour CPU, yolov8s/m/l/x pour GPU
    model_path: str = ""  # Chemin vers un modèle custom si vide utilise le modèle pré-entraîné
    
    # Modèle d'armes (optionnel)
    weapon_model_path: str = "ai-pipeline/models/weapon_detection.pt"  # Modèle entraîné pour les armes
    weapon_model_enabled: bool = True  # Activer la détection d'armes
    weapon_confidence_threshold: float = 0.8  # Seuil élevé pour minimiser les faux positifs
    
    # Classes COCO à détecter
    target_classes: List[str] = None
    
    # Seuils de confiance
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    
    # SAHI (Small Object Detection)
    use_sahi: bool = False  # Désactivé par défaut sur CPU (0.15 FPS), activer pour GPU
    sahi_slice_size: int = 320  # Taille des slices pour SAHI
    sahi_overlap_ratio: float = 0.2  # Chevauchement entre slices
    
    # Tracking multi-objets
    use_tracking: bool = True  # Activer ByteTrack pour le suivi multi-objets
    tracker_type: str = "bytetrack"  # Type de tracker (bytetrack, botsort)
    
    # Device d'inférence
    device: str = "cpu"  # "cpu", "cuda", "mps"
    
    # Taille d'entrée du modèle
    img_size: int = 640
    
    # FPS cible
    target_fps: int = 30
    
    # Flux vidéo
    rtsp_url: str = "rtsp://localhost:8554/drone-01-los"
    
    # Moteur de règles et alertes
    enable_rules_engine: bool = True  # Activer le moteur de règles
    enable_alert_publishing: bool = False  # Activer la publication d'alertes sur Redis (nécessite Redis)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_channel: str = "alerts"
    drone_id: str = "drone-01"
    
    def __post_init__(self):
        if self.target_classes is None:
            # Classes COCO pertinentes pour la surveillance drone
            self.target_classes = [
                "person",      # Personnes
                "bicycle",     # Vélos
                "car",         # Voitures
                "motorcycle",  # Motos
                "truck",       # Camions
                "bus"          # Bus
            ]
        
        # Charger depuis les variables d'environnement si disponibles
        if os.getenv("INFERENCE_MODEL"):
            self.model_name = os.getenv("INFERENCE_MODEL")
        if os.getenv("INFERENCE_DEVICE"):
            self.device = os.getenv("INFERENCE_DEVICE")
        if os.getenv("INFERENCE_RTSP_URL"):
            self.rtsp_url = os.getenv("INFERENCE_RTSP_URL")
        if os.getenv("INFERENCE_CONFIDENCE"):
            self.confidence_threshold = float(os.getenv("INFERENCE_CONFIDENCE"))


@dataclass
class Colors:
    """Couleurs pour l'affichage des bounding boxes."""
    person: tuple = (0, 255, 0)      # Vert
    vehicle: tuple = (255, 0, 0)     # Rouge
    bicycle: tuple = (255, 255, 0)  # Jaune
    weapon: tuple = (255, 0, 255)    # Magenta (pour les armes)
    default: tuple = (255, 255, 255) # Blanc
    
    @classmethod
    def get_color(cls, class_name: str) -> tuple:
        """Retourne la couleur associée à une classe."""
        if class_name == "person":
            return cls.person
        elif class_name in ["car", "truck", "bus", "motorcycle"]:
            return cls.vehicle
        elif class_name == "bicycle":
            return cls.bicycle
        elif class_name == "Weapon":
            return cls.weapon
        return cls.default


# Configuration globale par défaut
default_config = DetectionConfig()
