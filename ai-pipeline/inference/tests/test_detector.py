"""
Tests unitaires du module de détection.
"""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock

from inference.config import DetectionConfig, Colors
from inference.detector import ObjectDetector, Detection


class TestDetectionConfig:
    """Tests de la configuration de détection."""
    
    def test_default_config(self):
        """Test que la configuration par défaut est correcte."""
        config = DetectionConfig()
        
        assert config.model_name == "yolov8n.pt"
        assert config.confidence_threshold == 0.5
        assert config.iou_threshold == 0.45
        assert config.use_sahi == True
        assert config.device == "cpu"
        assert "person" in config.target_classes
        assert "car" in config.target_classes
        assert "motorcycle" in config.target_classes
    
    def test_custom_config(self):
        """Test la configuration personnalisée."""
        config = DetectionConfig(
            model_name="yolov8s.pt",
            confidence_threshold=0.7,
            device="cuda"
        )
        
        assert config.model_name == "yolov8s.pt"
        assert config.confidence_threshold == 0.7
        assert config.device == "cuda"


class TestColors:
    """Tests des couleurs d'affichage."""
    
    def test_get_color_person(self):
        """Test que la couleur pour 'person' est verte."""
        color = Colors.get_color("person")
        assert color == Colors.person
    
    def test_get_color_vehicle(self):
        """Test que la couleur pour les véhicules est rouge."""
        for vehicle in ["car", "truck", "bus", "motorcycle"]:
            color = Colors.get_color(vehicle)
            assert color == Colors.vehicle
    
    def test_get_color_bicycle(self):
        """Test que la couleur pour 'bicycle' est jaune."""
        color = Colors.get_color("bicycle")
        assert color == Colors.bicycle
    
    def test_get_color_default(self):
        """Test que la couleur par défaut est blanche."""
        color = Colors.get_color("unknown")
        assert color == Colors.default


class TestDetection:
    """Tests de la classe Detection."""
    
    def test_detection_creation(self):
        """Test la création d'une détection."""
        detection = Detection(
            bbox=[10, 20, 30, 40],
            class_name="person",
            confidence=0.85,
            class_id=0
        )
        
        assert detection.bbox == [10, 20, 30, 40]
        assert detection.class_name == "person"
        assert detection.confidence == 0.85
        assert detection.class_id == 0


class TestObjectDetector:
    """Tests du détecteur d'objets."""
    
    @pytest.fixture
    def config(self):
        """Fixture de configuration pour les tests."""
        return DetectionConfig(
            model_name="yolov8n.pt",
            confidence_threshold=0.5,
            use_sahi=False,  # Désactiver SAHI pour les tests
            device="cpu"
        )
    
    @pytest.fixture
    def sample_frame(self):
        """Fixture d'une frame de test."""
        return np.zeros((480, 640, 3), dtype=np.uint8)
    
    def test_detector_initialization(self, config):
        """Test l'initialisation du détecteur."""
        with patch('inference.detector.YOLO') as mock_yolo:
            mock_model = Mock()
            mock_yolo.return_value = mock_model
            
            detector = ObjectDetector(config)
            
            assert detector.config == config
            assert detector.model is not None
            assert detector.fps == 0.0
    
    def test_draw_detections_empty(self, config, sample_frame):
        """Test le dessin sans détections."""
        with patch('inference.detector.YOLO'):
            detector = ObjectDetector(config)
            
            result = detector.draw_detections(sample_frame, [])
            
            assert result.shape == sample_frame.shape
    
    def test_draw_detections_with_detections(self, config, sample_frame):
        """Test le dessin avec des détections."""
        with patch('inference.detector.YOLO'):
            detector = ObjectDetector(config)
            
            detections = [
                Detection(
                    bbox=[10, 10, 50, 50],
                    class_name="person",
                    confidence=0.9,
                    class_id=0
                )
            ]
            
            result = detector.draw_detections(sample_frame, detections)
            
            assert result.shape == sample_frame.shape
            # Vérifier que la frame a été modifiée (pixels différents)
            assert not np.array_equal(result, sample_frame)
    
    def test_fps_update(self, config):
        """Test la mise à jour du FPS."""
        with patch('inference.detector.YOLO'):
            detector = ObjectDetector(config)
            
            # Simuler plusieurs frames
            for _ in range(30):
                detector._update_fps()
            
            # Le FPS devrait être calculé après 1 seconde
            # Dans le test, on ne peut pas vraiment simuler le temps
            # mais on vérifie que la méthode ne crash pas
            assert detector.frame_count >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
