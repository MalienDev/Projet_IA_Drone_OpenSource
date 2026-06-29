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
import os

from ultralytics import YOLO
from sahi import AutoDetectionModel
from sahi.predict import get_prediction

try:
    from .config import DetectionConfig, Colors
except ImportError:
    from config import DetectionConfig, Colors

try:
    from ..tracking.movement_classifier import MovementClassifier, MovementType
except ImportError:
    from tracking.movement_classifier import MovementClassifier, MovementType

try:
    from ..rules.engine import RuleEngine, AlertType, Severity
    from ..rules.alert_manager import AlertManager, CooldownConfig
    from ..rules.publisher import EventPublisher
    from ..storage.media_storage import MediaStorage
except ImportError:
    from rules.engine import RuleEngine, AlertType, Severity
    from rules.alert_manager import AlertManager, CooldownConfig
    from rules.publisher import EventPublisher
    from storage.media_storage import MediaStorage


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
    movement_type: Optional[str] = None  # Type de mouvement (foot, motorbike, unknown)
    requires_confirmation: bool = False  # Flag pour les détections nécessitant confirmation opérateur (ex: armes)


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
        self.weapon_model = None  # Modèle d'armes
        self.fps = 0.0
        self.frame_count = 0
        self.start_time = time.time()
        self.movement_classifier = None
        
        # Moteur de règles et alertes
        self.rule_engine = None
        self.alert_manager = None
        self.event_publisher = None
        
        # Stockage des médias
        self.media_storage = None
        
        # Initialiser le modèle principal
        self._load_model()
        
        # Initialiser le modèle d'armes si activé
        if self.config.weapon_model_enabled:
            self._load_weapon_model()
        
        # Initialiser le classifieur de mouvement si le tracking est activé
        if self.config.use_tracking:
            self.movement_classifier = MovementClassifier()
        
        # Initialiser le moteur de règles si activé
        if self.config.enable_rules_engine:
            self._init_rules_engine()
        
        # Initialiser le stockage des médias si activé
        if self.config.enable_media_storage:
            self._init_media_storage()
        
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
    
    def _load_weapon_model(self):
        """Charge le modèle de détection d'armes."""
        import os
        from pathlib import Path
        
        weapon_path = self.config.weapon_model_path
        
        # Vérifier si le fichier existe
        if not os.path.exists(weapon_path):
            logger.warning(f"Modèle d'armes non trouvé à {weapon_path}. Détection d'armes désactivée.")
            self.config.weapon_model_enabled = False
            self.weapon_model = None
            return
        
        try:
            logger.info(f"Chargement du modèle d'armes depuis {weapon_path}...")
            self.weapon_model = YOLO(weapon_path)
            self.weapon_model.to(self.config.device)
            logger.info("Modèle d'armes chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle d'armes: {e}")
            logger.warning("Détection d'armes désactivée.")
            self.config.weapon_model_enabled = False
            self.weapon_model = None
    
    def _init_rules_engine(self):
        """Initialise le moteur de règles et le publisher d'événements."""
        try:
            logger.info("Initialisation du moteur de règles...")
            self.rule_engine = RuleEngine()
            
            # Initialiser l'alert manager avec cooldowns par défaut
            self.alert_manager = AlertManager()
            
            # Initialiser le publisher Redis si activé
            if self.config.enable_alert_publishing:
                logger.info(f"Initialisation du publisher Redis ({self.config.redis_host}:{self.config.redis_port})...")
                self.event_publisher = EventPublisher(
                    redis_host=self.config.redis_host,
                    redis_port=self.config.redis_port,
                    channel=self.config.redis_channel,
                    drone_id=self.config.drone_id
                )
                self.event_publisher.connect()
                if not self.event_publisher.is_connected():
                    logger.warning("Impossible de se connecter à Redis. Publication d'alertes désactivée.")
                    self.event_publisher = None
            else:
                logger.info("Publication d'alertes désactivée (enable_alert_publishing=False)")
            
            logger.info("Moteur de règles initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du moteur de règles: {e}")
            self.rule_engine = None
            self.alert_manager = None
            self.event_publisher = None
    
    def _init_media_storage(self):
        """Initialise le stockage des médias."""
        try:
            logger.info("Initialisation du stockage des médias...")
            self.media_storage = MediaStorage(
                storage_dir=self.config.storage_dir,
                clip_duration_seconds=self.config.clip_duration_seconds,
                fps=self.config.storage_fps
            )
            logger.info("Stockage des médias initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du stockage des médias: {e}")
            self.media_storage = None
    
    def detect_frame(self, frame: np.ndarray, zone_id: Optional[str] = None) -> List[Detection]:
        """
        Détecte les objets dans une frame.
        
        Args:
            frame: Image numpy array (BGR)
            zone_id: ID de la zone (optionnel, pour les alertes)
            
        Returns:
            Liste des détections
        """
        # Ajouter la frame au buffer de stockage si activé
        if self.media_storage:
            self.media_storage.add_frame(frame)
        
        # Détecter avec le modèle principal (personnes/vehicules)
        if self.config.use_sahi and self.sahi_model:
            detections = self._detect_with_sahi(frame)
        else:
            detections = self._detect_with_yolo(frame)
        
        # Détecter les armes avec le modèle secondaire si activé
        if self.config.weapon_model_enabled and self.weapon_model:
            weapon_detections = self._detect_weapons(frame)
            detections.extend(weapon_detections)
        
        # Traiter les alertes si le moteur de règles est activé
        if self.config.enable_rules_engine:
            self._process_alerts(detections, zone_id, frame)
        
        return detections
    
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
        person_tracks = []
        motorcycle_tracks = []
        
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
                
                detection = Detection(
                    bbox=bbox.tolist(),
                    class_name=class_name,
                    confidence=confidence,
                    class_id=class_id,
                    track_id=track_id
                )
                
                # Collecter les tracks pour la classification de mouvement
                if self.config.use_tracking and track_id is not None:
                    if class_name == "person":
                        person_tracks.append(detection)
                    elif class_name == "motorcycle":
                        motorcycle_tracks.append(detection)
                
                detections.append(detection)
        
        # Classifier le mouvement si activé
        if self.config.use_tracking and self.movement_classifier and person_tracks:
            # Créer des objets TrackedObject temporaires pour la classification
            from ..tracking.tracker import TrackedObject
            person_tracked_objects = []
            for det in person_tracks:
                tracked_obj = TrackedObject(
                    track_id=det.track_id,
                    class_name=det.class_name,
                    bbox=det.bbox,
                    confidence=det.confidence,
                    class_id=det.class_id
                )
                person_tracked_objects.append(tracked_obj)
            
            moto_tracked_objects = []
            for det in motorcycle_tracks:
                tracked_obj = TrackedObject(
                    track_id=det.track_id,
                    class_name=det.class_name,
                    bbox=det.bbox,
                    confidence=det.confidence,
                    class_id=det.class_id
                )
                moto_tracked_objects.append(tracked_obj)
            
            # Classifier
            classifications = self.movement_classifier.classify(
                person_tracked_objects, moto_tracked_objects
            )
            
            # Appliquer les classifications aux détections
            classification_map = {c.track_id: c for c in classifications}
            for det in detections:
                if det.track_id in classification_map:
                    det.movement_type = classification_map[det.track_id].movement_type.value
        
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
    
    def _detect_weapons(self, frame: np.ndarray) -> List[Detection]:
        """Détection d'armes avec le modèle dédié."""
        try:
            results = self.weapon_model(
                frame,
                conf=self.config.weapon_confidence_threshold,  # Seuil élevé
                iou=self.config.iou_threshold,
                imgsz=self.config.img_size,
                verbose=False
            )
            
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = self.weapon_model.names[class_id]
                    
                    bbox = box.xyxy[0].cpu().numpy().astype(int)
                    confidence = float(box.conf[0])
                    
                    # Créer la détection avec flag de confirmation obligatoire
                    detection = Detection(
                        bbox=bbox.tolist(),
                        class_name=class_name,
                        confidence=confidence,
                        class_id=class_id,
                        requires_confirmation=True  # Confirmation opérateur obligatoire
                    )
                    
                    detections.append(detection)
            
            if detections:
                logger.info(f"Détection(s) arme(s): {len(detections)} (seuil: {self.config.weapon_confidence_threshold})")
            
            return detections
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection d'armes: {e}")
            return []
    
    def _map_detection_to_alert_type(self, detection: Detection) -> AlertType:
        """
        Mappe une détection à un type d'alerte.
        
        Args:
            detection: Objet Detection
        
        Returns:
            AlertType correspondant
        """
        if detection.class_name == "Weapon":
            return AlertType.WEAPON_SUSPECTED
        elif detection.class_name == "person":
            if detection.movement_type == "motorbike":
                return AlertType.MOVEMENT_MOTORBIKE
            elif detection.movement_type == "foot":
                return AlertType.MOVEMENT_FOOT
            return AlertType.PERSON
        elif detection.class_name in ["car", "truck", "bus", "motorcycle"]:
            return AlertType.VEHICLE
        elif detection.class_name == "bicycle":
            return AlertType.VEHICLE
        else:
            return AlertType.PERSON  # Default
    
    def _process_alerts(self, detections: List[Detection], zone_id: Optional[str] = None, frame: Optional[np.ndarray] = None):
        """
        Traite les détections pour générer et publier des alertes.
        
        Args:
            detections: Liste des détections
            zone_id: ID de la zone (optionnel)
            frame: Frame vidéo actuelle (optionnel, pour capture médias)
        """
        if not self.rule_engine or not self.alert_manager:
            return
        
        for detection in detections:
            # Mapper la détection à un type d'alerte
            alert_type = self._map_detection_to_alert_type(detection)
            
            # Classifier l'alerte avec le moteur de règles
            context = {}
            if detection.movement_type:
                context["movement_type"] = detection.movement_type
            
            classification = self.rule_engine.classify_alert(
                alert_type=alert_type,
                confidence=detection.confidence,
                zone_id=zone_id,
                **context
            )
            
            if not classification["should_alert"]:
                continue
            
            # Vérifier le cooldown
            track_id_str = str(detection.track_id) if detection.track_id else None
            should_alert, reason = self.alert_manager.should_alert(
                alert_type=alert_type,
                zone_id=zone_id,
                track_id=track_id_str
            )
            
            if not should_alert:
                logger.debug(f"Alerte bloquée par cooldown: {reason}")
                continue
            
            # Enregistrer l'alerte
            severity = Severity(classification["severity"])
            self.alert_manager.record_alert(
                alert_type=alert_type,
                zone_id=zone_id,
                track_id=track_id_str,
                severity=severity
            )
            
            # Capturer les médias si activé et frame disponible
            snapshot_path = None
            clip_path = None
            if self.media_storage and frame is not None:
                try:
                    # Générer un alert_id temporaire
                    import uuid
                    alert_id = str(uuid.uuid4())
                    
                    # Capturer snapshot et clip
                    snapshot_path, clip_path = self.media_storage.capture_alert_media(
                        frame,
                        alert_id=alert_id,
                        bbox=tuple(detection.bbox) if detection.bbox else None,
                        save_clip=True
                    )
                    logger.debug(f"Médias capturés: snapshot={snapshot_path}, clip={clip_path}")
                except Exception as e:
                    logger.error(f"Erreur lors de la capture des médias: {e}")
            
            # Publier sur Redis si activé
            if self.event_publisher:
                try:
                    self.event_publisher.publish_alert(
                        alert_type=alert_type,
                        severity=severity,
                        confidence=detection.confidence,
                        bbox=detection.bbox,
                        track_id=track_id_str,
                        zone_id=zone_id,
                        snapshot_path=snapshot_path,
                        clip_path=clip_path,
                        requires_operator_ack=classification["requires_operator_ack"] or detection.requires_confirmation
                    )
                    logger.info(f"Alerte publiée: {alert_type.value} (sevérité: {severity.value})")
                except Exception as e:
                    logger.error(f"Erreur lors de la publication de l'alerte: {e}")
            else:
                logger.info(f"Alerte générée (non publiée): {alert_type.value} (sevérité: {severity.value})")
    
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
            
            # Dessiner le label avec confiance, track_id, mouvement et confirmation
            if detection.track_id is not None:
                movement_str = f" [{detection.movement_type}]" if detection.movement_type else ""
                confirm_str = " [CONFIRM]" if detection.requires_confirmation else ""
                label = f"{detection.class_name}: {detection.confidence:.2f} [ID:{detection.track_id}]{movement_str}{confirm_str}"
            else:
                confirm_str = " [CONFIRM]" if detection.requires_confirmation else ""
                label = f"{detection.class_name}: {detection.confidence:.2f}{confirm_str}"
            
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
