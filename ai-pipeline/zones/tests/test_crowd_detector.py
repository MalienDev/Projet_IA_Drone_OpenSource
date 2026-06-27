"""
Tests unitaires pour le module de détection de regroupement.
"""

import pytest
import time
from dataclasses import dataclass
from typing import List
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from crowd_detector import CrowdDetector, CrowdEvent
from zone_manager import ZoneManager, ZoneType


@dataclass
class MockTrack:
    """Mock d'un objet suivi pour les tests."""
    track_id: int
    bbox: List[int]


class TestCrowdDetector:
    """Tests pour la classe CrowdDetector."""
    
    def test_initialization(self):
        """Test l'initialisation du détecteur."""
        detector = CrowdDetector(min_person_threshold=5, min_duration=10.0)
        assert detector.min_person_threshold == 5
        assert detector.min_duration == 10.0
        assert len(detector.track_history) == 0
        assert len(detector.active_crowds) == 0
    
    def test_reset(self):
        """Test la réinitialisation du détecteur."""
        detector = CrowdDetector()
        detector.track_history[1] = []
        detector.active_crowds['zone-1'] = CrowdEvent(
            zone_id='zone-1',
            person_count=5,
            threshold=5,
            duration=10.0,
            start_time=time.time()
        )
        
        detector.reset()
        assert len(detector.track_history) == 0
        assert len(detector.active_crowds) == 0
    
    def test_count_people_in_zone(self):
        """Test le comptage de personnes dans une zone."""
        detector = CrowdDetector(min_person_threshold=3, min_duration=5.0)
        current_time = time.time()
        
        # Ajouter des tracks dans la zone
        detector.track_history[1].append((current_time - 1, 'zone-1'))
        detector.track_history[2].append((current_time - 2, 'zone-1'))
        detector.track_history[3].append((current_time - 3, 'zone-1'))
        
        # Ajouter un track hors zone
        detector.track_history[4].append((current_time - 1, 'zone-2'))
        
        count = detector._count_people_in_zone('zone-1', current_time)
        assert count == 3
    
    def test_count_people_in_zone_with_old_tracks(self):
        """Test que les vieux tracks ne sont pas comptés."""
        detector = CrowdDetector(min_person_threshold=3, min_duration=5.0)
        current_time = time.time()
        
        # Ajouter des tracks récents
        detector.track_history[1].append((current_time - 1, 'zone-1'))
        detector.track_history[2].append((current_time - 2, 'zone-1'))
        
        # Ajouter un track vieux (hors fenêtre de 10s)
        detector.track_history[3].append((current_time - 15, 'zone-1'))
        
        count = detector._count_people_in_zone('zone-1', current_time)
        assert count == 2  # Seuls les 2 tracks récents comptent
    
    def test_update_no_crowd(self):
        """Test la mise à jour sans regroupement (sous le seuil)."""
        detector = CrowdDetector(min_person_threshold=5, min_duration=5.0)
        zone_manager = ZoneManager()
        
        zone_manager.create_zone(
            zone_id='zone-1',
            name='Zone 1',
            zone_type=ZoneType.CROWD,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        # Créer 2 tracks (sous le seuil de 5)
        tracks = [
            MockTrack(track_id=1, bbox=[25, 25, 35, 35]),
            MockTrack(track_id=2, bbox=[50, 50, 60, 60])
        ]
        
        events = detector.update(tracks, zone_manager)
        assert len(events) == 0
        assert len(detector.active_crowds) == 0
    
    def test_update_crowd_detected(self):
        """Test la détection d'un regroupement."""
        detector = CrowdDetector(min_person_threshold=3, min_duration=5.0)
        zone_manager = ZoneManager()
        
        zone_manager.create_zone(
            zone_id='zone-1',
            name='Zone 1',
            zone_type=ZoneType.CROWD,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        # Créer 3 tracks (au seuil)
        tracks = [
            MockTrack(track_id=1, bbox=[25, 25, 35, 35]),
            MockTrack(track_id=2, bbox=[50, 50, 60, 60]),
            MockTrack(track_id=3, bbox=[75, 75, 85, 85])
        ]
        
        events = detector.update(tracks, zone_manager)
        assert len(events) == 1
        assert events[0].zone_id == 'zone-1'
        assert events[0].person_count == 3
        assert 'zone-1' in detector.active_crowds
    
    def test_update_crowd_ended(self):
        """Test la fin d'un regroupement."""
        detector = CrowdDetector(min_person_threshold=3, min_duration=5.0)
        zone_manager = ZoneManager()
        
        zone_manager.create_zone(
            zone_id='zone-1',
            name='Zone 1',
            zone_type=ZoneType.CROWD,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        # Créer un regroupement initial
        tracks = [
            MockTrack(track_id=1, bbox=[25, 25, 35, 35]),
            MockTrack(track_id=2, bbox=[50, 50, 60, 60]),
            MockTrack(track_id=3, bbox=[75, 75, 85, 85])
        ]
        detector.update(tracks, zone_manager)
        
        # Nettoyer l'historique pour simuler le temps qui passe
        detector.track_history.clear()
        
        # Réduire le nombre de personnes sous le seuil
        tracks = [
            MockTrack(track_id=1, bbox=[25, 25, 35, 35])
        ]
        events = detector.update(tracks, zone_manager)
        
        # L'événement devrait être désactivé
        assert 'zone-1' not in detector.active_crowds
    
    def test_get_active_crowds(self):
        """Test la récupération des regroupements actifs."""
        detector = CrowdDetector(min_person_threshold=3, min_duration=5.0)
        zone_manager = ZoneManager()
        
        zone_manager.create_zone(
            zone_id='zone-1',
            name='Zone 1',
            zone_type=ZoneType.CROWD,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        tracks = [
            MockTrack(track_id=1, bbox=[25, 25, 35, 35]),
            MockTrack(track_id=2, bbox=[50, 50, 60, 60]),
            MockTrack(track_id=3, bbox=[75, 75, 85, 85])
        ]
        
        detector.update(tracks, zone_manager)
        
        active_crowds = detector.get_active_crowds()
        assert len(active_crowds) == 1
        assert active_crowds[0].zone_id == 'zone-1'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
