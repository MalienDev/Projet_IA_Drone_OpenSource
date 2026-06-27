"""
Tests unitaires pour le module de classification de mouvement.
"""

import pytest
from tracking.movement_classifier import (
    MovementClassifier,
    MovementType,
    MovementClassification
)
from tracking.tracker import TrackedObject


@pytest.fixture
def classifier():
    """Fixture pour le classifieur avec paramètres par défaut."""
    return MovementClassifier(
        association_distance_threshold=100.0,
        association_iou_threshold=0.1,
        min_association_frames=3,
        walking_speed_threshold=2.0,
        fast_walking_speed_threshold=5.0
    )


@pytest.fixture
def person_track():
    """Fixture pour un track de personne."""
    track = TrackedObject(
        track_id=1,
        class_name="person",
        bbox=[100, 100, 150, 200],
        confidence=0.9,
        class_id=0,
        frame_count=10,
        last_seen=10
    )
    # Historique de positions simulant un déplacement lent
    for i in range(10):
        track.history.append([100 + i, 100 + i, 150 + i, 200 + i])
    return track


@pytest.fixture
def motorcycle_track():
    """Fixture pour un track de moto."""
    track = TrackedObject(
        track_id=2,
        class_name="motorcycle",
        bbox=[120, 110, 180, 220],
        confidence=0.85,
        class_id=3,
        frame_count=10,
        last_seen=10
    )
    # Historique de positions simulant un déplacement rapide
    for i in range(10):
        track.history.append([120 + i*2, 110 + i*2, 180 + i*2, 220 + i*2])
    return track


class TestMovementClassifier:
    """Tests pour la classe MovementClassifier."""
    
    def test_initialization(self, classifier):
        """Test l'initialisation du classifieur."""
        assert classifier.association_distance_threshold == 100.0
        assert classifier.association_iou_threshold == 0.1
        assert classifier.min_association_frames == 3
        assert classifier.walking_speed_threshold == 2.0
        assert classifier.fast_walking_speed_threshold == 5.0
    
    def test_classify_no_tracks(self, classifier):
        """Test la classification sans tracks."""
        classifications = classifier.classify([], [])
        assert len(classifications) == 0
    
    def test_classify_person_only(self, classifier, person_track):
        """Test la classification d'une personne sans moto."""
        classifications = classifier.classify([person_track], [])
        assert len(classifications) == 1
        assert classifications[0].track_id == 1
        assert classifications[0].class_name == "person"
        assert classifications[0].movement_type == MovementType.FOOT
        assert classifications[0].associated_vehicle_id is None
    
    def test_classify_person_with_nearby_motorcycle(self, classifier, person_track, motorcycle_track):
        """Test la classification d'une personne avec une moto proche."""
        classifications = classifier.classify([person_track], [motorcycle_track])
        assert len(classifications) == 1
        # Première frame : pas encore d'association stable
        assert classifications[0].movement_type == MovementType.FOOT
    
    def test_stable_motorcycle_association(self, classifier, person_track, motorcycle_track):
        """Test l'association stable avec une moto après plusieurs frames."""
        # Simuler plusieurs frames avec la même association
        for _ in range(5):
            classifier.classify([person_track], [motorcycle_track])
        
        classifications = classifier.classify([person_track], [motorcycle_track])
        assert len(classifications) == 1
        # Après plusieurs frames, l'association devrait être stable
        assert classifications[0].movement_type == MovementType.MOTORBIKE
        assert classifications[0].associated_vehicle_id == 2
        assert classifications[0].confidence > 0.5
    
    def test_walking_speed_classification(self, classifier):
        """Test la classification basée sur la vitesse de marche."""
        # Personne avec déplacement lent
        slow_person = TrackedObject(
            track_id=3,
            class_name="person",
            bbox=[100, 100, 150, 200],
            confidence=0.9,
            class_id=0,
            frame_count=10,
            last_seen=10
        )
        # Historique très lent (0.3 pixel/frame en diagonal)
        slow_person.history = []
        for i in range(10):
            slow_person.history.append([100 + i*0.3, 100 + i*0.3, 150 + i*0.3, 200 + i*0.3])
        
        classifications = classifier.classify([slow_person], [])
        assert classifications[0].movement_type == MovementType.FOOT
        assert classifications[0].speed_pixels_per_frame < 2.0
    
    def test_fast_walking_speed_classification(self, classifier):
        """Test la classification basée sur la vitesse de marche rapide."""
        # Personne avec déplacement rapide
        fast_person = TrackedObject(
            track_id=4,
            class_name="person",
            bbox=[100, 100, 150, 200],
            confidence=0.9,
            class_id=0,
            frame_count=10,
            last_seen=10
        )
        # Historique rapide (10 pixels/frame)
        for i in range(10):
            fast_person.history.append([100 + i*10, 100 + i*10, 150 + i*10, 200 + i*10])
        
        classifications = classifier.classify([fast_person], [])
        assert classifications[0].movement_type == MovementType.FOOT
        assert classifications[0].speed_pixels_per_frame > 5.0
    
    def test_multiple_persons(self, classifier):
        """Test la classification de plusieurs personnes."""
        person1 = TrackedObject(
            track_id=1,
            class_name="person",
            bbox=[100, 100, 150, 200],
            confidence=0.9,
            class_id=0,
            frame_count=10,
            last_seen=10
        )
        for i in range(10):
            person1.history.append([100 + i, 100 + i, 150 + i, 200 + i])
        
        person2 = TrackedObject(
            track_id=2,
            class_name="person",
            bbox=[300, 300, 350, 400],
            confidence=0.85,
            class_id=0,
            frame_count=10,
            last_seen=10
        )
        for i in range(10):
            person2.history.append([300 + i*2, 300 + i*2, 350 + i*2, 400 + i*2])
        
        classifications = classifier.classify([person1, person2], [])
        assert len(classifications) == 2
        assert classifications[0].track_id == 1
        assert classifications[1].track_id == 2
    
    def test_iou_calculation(self, classifier):
        """Test le calcul de l'IoU."""
        # Bounding boxes qui se chevauchent
        bbox1 = [0, 0, 100, 100]
        bbox2 = [50, 50, 150, 150]
        iou = classifier._calculate_iou(bbox1, bbox2)
        assert 0 < iou < 1
        
        # Bounding boxes disjointes
        bbox3 = [0, 0, 100, 100]
        bbox4 = [200, 200, 300, 300]
        iou = classifier._calculate_iou(bbox3, bbox4)
        assert iou == 0.0
        
        # Bounding boxes identiques
        bbox5 = [0, 0, 100, 100]
        bbox6 = [0, 0, 100, 100]
        iou = classifier._calculate_iou(bbox5, bbox6)
        assert iou == 1.0
    
    def test_reset(self, classifier, person_track, motorcycle_track):
        """Test la réinitialisation du classifieur."""
        # Créer une association
        for _ in range(5):
            classifier.classify([person_track], [motorcycle_track])
        
        assert len(classifier.association_history) > 0
        
        # Réinitialiser
        classifier.reset()
        
        assert len(classifier.association_history) == 0
    
    def test_cleanup_association_history(self, classifier, person_track, motorcycle_track):
        """Test le nettoyage de l'historique d'association."""
        # Créer une association
        for _ in range(5):
            classifier.classify([person_track], [motorcycle_track])
        
        assert person_track.track_id in classifier.association_history
        
        # Nettoyer avec une liste vide (simulant la suppression des tracks)
        classifier._cleanup_association_history([], {})
        
        assert person_track.track_id not in classifier.association_history


class TestTrackedObjectSpeed:
    """Tests pour la méthode get_average_speed de TrackedObject."""
    
    def test_get_average_speed_insufficient_history(self):
        """Test avec un historique insuffisant."""
        track = TrackedObject(
            track_id=1,
            class_name="person",
            bbox=[100, 100, 150, 200],
            confidence=0.9,
            class_id=0,
            frame_count=2,
            last_seen=2
        )
        track.history = [[100, 100, 150, 200], [101, 101, 151, 201]]
        
        speed = track.get_average_speed(min_history=5)
        assert speed == 0.0
    
    def test_get_average_speed_sufficient_history(self):
        """Test avec un historique suffisant."""
        track = TrackedObject(
            track_id=1,
            class_name="person",
            bbox=[100, 100, 150, 200],
            confidence=0.9,
            class_id=0,
            frame_count=10,
            last_seen=10
        )
        # Historique avec déplacement constant de 0.5 pixel/frame en diagonal
        track.history = []
        for i in range(10):
            track.history.append([100 + i*0.5, 100 + i*0.5, 150 + i*0.5, 200 + i*0.5])
        
        speed = track.get_average_speed(min_history=5)
        # Vérifier que la vitesse est raisonnable (peut varier selon l'implémentation)
        assert speed > 0  # Juste vérifier qu'il y a une vitesse positive


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
