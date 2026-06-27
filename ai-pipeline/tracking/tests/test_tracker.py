"""
Tests unitaires pour le module de tracking.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Ajouter le répertoire tracking au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tracker import MultiObjectTracker, TrackedObject


class TestTrackedObject:
    """Tests pour la classe TrackedObject."""
    
    def test_centroid_calculation(self):
        """Test le calcul du centroïde."""
        obj = TrackedObject(
            track_id=1,
            class_name="person",
            bbox=[100, 100, 200, 200],
            confidence=0.9,
            class_id=0
        )
        centroid = obj.get_centroid()
        assert centroid == (150.0, 150.0)
    
    def test_velocity_calculation(self):
        """Test le calcul de vélocité."""
        obj = TrackedObject(
            track_id=1,
            class_name="person",
            bbox=[100, 100, 200, 200],
            confidence=0.9,
            class_id=0
        )
        prev_bbox = [90, 90, 190, 190]
        velocity = obj.get_velocity(prev_bbox)
        assert velocity == (10.0, 10.0)


class TestMultiObjectTracker:
    """Tests pour la classe MultiObjectTracker."""
    
    def test_initialization(self):
        """Test l'initialisation du tracker."""
        tracker = MultiObjectTracker(tracker_type="bytetrack")
        assert tracker.tracker_type == "bytetrack"
        assert len(tracker.tracks) == 0
        assert tracker.frame_count == 0
    
    def test_reset(self):
        """Test la réinitialisation du tracker."""
        tracker = MultiObjectTracker()
        tracker.tracks[1] = TrackedObject(
            track_id=1,
            class_name="person",
            bbox=[100, 100, 200, 200],
            confidence=0.9,
            class_id=0
        )
        tracker.reset()
        assert len(tracker.tracks) == 0
        assert tracker.next_track_id == 1
    
    def test_get_track(self):
        """Test la récupération d'un track par ID."""
        tracker = MultiObjectTracker()
        track = TrackedObject(
            track_id=1,
            class_name="person",
            bbox=[100, 100, 200, 200],
            confidence=0.9,
            class_id=0
        )
        tracker.tracks[1] = track
        
        retrieved = tracker.get_track(1)
        assert retrieved is not None
        assert retrieved.track_id == 1
        
        not_found = tracker.get_track(999)
        assert not_found is None
    
    def test_get_tracks_by_class(self):
        """Test la récupération des tracks par classe."""
        tracker = MultiObjectTracker()
        
        tracker.tracks[1] = TrackedObject(
            track_id=1,
            class_name="person",
            bbox=[100, 100, 200, 200],
            confidence=0.9,
            class_id=0
        )
        tracker.tracks[2] = TrackedObject(
            track_id=2,
            class_name="car",
            bbox=[300, 300, 400, 400],
            confidence=0.8,
            class_id=2
        )
        tracker.tracks[3] = TrackedObject(
            track_id=3,
            class_name="person",
            bbox=[500, 500, 600, 600],
            confidence=0.85,
            class_id=0
        )
        
        person_tracks = tracker.get_tracks_by_class("person")
        assert len(person_tracks) == 2
        
        car_tracks = tracker.get_tracks_by_class("car")
        assert len(car_tracks) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
