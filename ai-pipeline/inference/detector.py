"""
Module de détection d'objets avec YOLO et SAHI.
Consomme un flux vidéo MediaMTX et détecte personnes/vehicules.
"""

import cv2
import numpy as np
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

from ultralytics import YOLO
from sahi import AutoDetectionModel
from sahi.predict import get_prediction

try:
    from .config import DetectionConfig, Colors
except ImportError:
    from config import DetectionConfig, Colors


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Représente une détection d'objet."""
    bbox: List[int]  # [x1, y1, x2, y2]
    class_name: str
    confidence: float
    class_id: int
    track_id: Optional[int] = None  # ID de tracking si activé


class ObjectDetector:
    """Détecteur d'objets basé sur YOLO + SAHI."""
    
    def __init__(self, config: DetectionConfig):
        """
        Initialise le détecteur.
        
        Args:
            config: Configuration de détection
        """
        self.config = config
        self.model = None
        self.sahi_model = None
        self.fps = 0.0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Initialiser le modèle
        self._load_model()
        
    def _load_model(self):
        """Charge le modèle YOLO et initialise SAHI si configuré."""
        logger.info(f"Chargement du modèle {self.config.model_name}...")
        
        try:
            # Charger le modèle YOLO
            self.model = YOLO(self.config.model_name)
            
            # Configurer le device
            self.model.to(self.config.device)
            
            logger.info(f"Modèle chargé avec succès sur {self.config.device}")
            
            # Initialiser SAHI si activé
            if self.config.use_sahi:
                logger.info("Initialisation de SAHI pour la détection de petits objets...")
                self.sahi_model = AutoDetectionModel.from_pretrained(
                    model_type="ultralytics",  # Changé de "yolov8" à "ultralytics" pour SAHI 0.12+
                    model_path=self.config.model_name,
                    confidence_threshold=self.config.confidence_threshold,
                    device=self.config.device,
                )
                logger.info("SAHI initialisé avec succès")
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            raise
    
    def detect_frame(self, frame: np.ndarray) -> List[Detection]:
        """
        Détecte les objets dans une frame.
        
        Args:
            frame: Image numpy array (BGR)
            
        Returns:
            Liste des détections
        """
        if self.config.use_sahi and self.sahi_model:
            return self._detect_with_sahi(frame)
        else:
            return self._detect_with_yolo(frame)
    
    def _detect_with_yolo(self, frame: np.ndarray) -> List[Detection]:
        """Détection avec YOLO standard."""
        # Activer le tracking si configuré
        if self.config.use_tracking:
            results = self.model.track(
                frame,
                conf=self.config.confidence_threshold,
                iou=self.config.iou_threshold,
                imgsz=self.config.img_size,
                verbose=False,
                persist=True,
                tracker=self.config.tracker_type
            )
        else:
            results = self.model(
                frame,
                conf=self.config.confidence_threshold,
                iou=self.config.iou_threshold,
                imgsz=self.config.img_size,
                verbose=False
            )
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                
                # Filtrer les classes cibles
                if class_name not in self.config.target_classes:
                    continue
                
                bbox = box.xyxy[0].cpu().numpy().astype(int)
                confidence = float(box.conf[0])
                
                # Récupérer l'ID de tracking si disponible
                track_id = None
                if self.config.use_tracking and hasattr(box, 'id') and box.id is not None:
                    track_id = int(box.id[0])
                
                detections.append(Detection(
                    bbox=bbox.tolist(),
                    class_name=class_name,
                    confidence=confidence,
                    class_id=class_id,
                    track_id=track_id
                ))
        
        return detections
    
    def _detect_with_sahi(self, frame: np.ndarray) -> List[Detection]:
        """Détection avec SAHI (meilleure pour petits objets)."""
        try:
            from sahi.predict import get_sliced_prediction
            
            result = get_sliced_prediction(
                image=frame,
                detection_model=self.sahi_model,
                slice_height=self.config.sahi_slice_size,
                slice_width=self.config.sahi_slice_size,
                overlap_height_ratio=self.config.sahi_overlap_ratio,
                overlap_width_ratio=self.config.sahi_overlap_ratio,
                verbose=0
            )
            
            detections = []
            for object_prediction in result.object_prediction_list:
                class_name = object_prediction.category.name
                
                # Filtrer les classes cibles
                if class_name not in self.config.target_classes:
                    continue
                
                bbox = object_prediction.bbox.to_xyxy()
                confidence = object_prediction.score.value
                
                detections.append(Detection(
                    bbox=[int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])],
                    class_name=class_name,
                    confidence=confidence,
                    class_id=object_prediction.category.id
                ))
            
            return detections
            
        except Exception as e:
            logger.warning(f"Erreur SAHI, fallback sur YOLO standard: {e}")
            return self._detect_with_yolo(frame)
    
    def draw_detections(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """
        Dessine les bounding boxes sur la frame.
        
        Args:
            frame: Image originale
            detections: Liste des détections
            
        Returns:
            Frame avec les bounding boxes dessinées
        """
        frame_copy = frame.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            color = Colors.get_color(detection.class_name)
            
            # Dessiner la bounding box
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)
            
            # Dessiner le label avec confiance et track_id
            if detection.track_id is not None:
                label = f"{detection.class_name}: {detection.confidence:.2f} [ID:{detection.track_id}]"
            else:
                label = f"{detection.class_name}: {detection.confidence:.2f}"
            
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            
            # Fond du label
            cv2.rectangle(
                frame_copy,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                color,
                -1
            )
            
            # Texte du label
            cv2.putText(
                frame_copy,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )
        
        # Afficher le FPS et le statut de tracking
        self._update_fps()
        tracking_status = "ON" if self.config.use_tracking else "OFF"
        fps_text = f"FPS: {self.fps:.1f} | Tracking: {tracking_status}"
        cv2.putText(
            frame_copy,
            fps_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        
        return frame_copy
    
    def _update_fps(self):
        """Met à jour le compteur de FPS."""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
    
    def process_stream(self, display: bool = True):
        """
        Traite le flux vidéo en continu.
        
        Args:
            display: Si True, affiche la fenêtre de visualisation
        """
        logger.info(f"Démarrage du traitement du flux: {self.config.rtsp_url}")
        
        # Ouvrir le flux vidéo
        cap = cv2.VideoCapture(self.config.rtsp_url)
        
        if not cap.isOpened():
            logger.error(f"Impossible d'ouvrir le flux: {self.config.rtsp_url}")
            return
        
        logger.info("Flux ouvert avec succès")
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning("Fin du flux ou erreur de lecture")
                    time.sleep(0.1)
                    continue
                
                # Détecter les objets
                detections = self.detect_frame(frame)
                
                # Dessiner les détections
                if display:
                    frame_with_detections = self.draw_detections(frame, detections)
                    cv2.imshow("Drone Surveillance - Detection", frame_with_detections)
                    
                    # Quitter avec 'q'
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        logger.info("Arrêt demandé par l'utilisateur")
                        break
                
        except KeyboardInterrupt:
            logger.info("Interruption par l'utilisateur")
        finally:
            cap.release()
            if display:
                cv2.destroyAllWindows()
            logger.info("Traitement du flux terminé")


def main():
    """Point d'entrée pour tester le détecteur."""
    config = DetectionConfig()
    detector = ObjectDetector(config)
    detector.process_stream(display=True)


if __name__ == "__main__":
    main()
