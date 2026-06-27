"""
Tests unitaires pour le module de gestion des zones.
"""

import pytest
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from zone_manager import ZoneManager, Zone, ZoneType


class TestZone:
    """Tests pour la classe Zone."""
    
    def test_zone_creation(self):
        """Test la création d'une zone."""
        zone = Zone(
            zone_id="test-zone",
            name="Zone de test",
            zone_type=ZoneType.INTRUSION,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        assert zone.zone_id == "test-zone"
        assert zone.name == "Zone de test"
        assert zone.zone_type == ZoneType.INTRUSION
    
    def test_contains_point(self):
        """Test la détection de point dans la zone."""
        zone = Zone(
            zone_id="test-zone",
            name="Zone de test",
            zone_type=ZoneType.INTRUSION,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        # Point à l'intérieur
        assert zone.contains_point((50, 50)) == True
        
        # Point à l'extérieur
        assert zone.contains_point((150, 150)) == False
    
    def test_contains_bbox(self):
        """Test la détection de bbox dans la zone (via centroïde)."""
        zone = Zone(
            zone_id="test-zone",
            name="Zone de test",
            zone_type=ZoneType.INTRUSION,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        # Bbox à l'intérieur (centroïde à 50, 50)
        assert zone.contains_bbox([25, 25, 75, 75]) == True
        
        # Bbox à l'extérieur (centroïde à 150, 150)
        assert zone.contains_bbox([125, 125, 175, 175]) == False
    
    def test_to_dict_from_dict(self):
        """Test la sérialisation/désérialisation."""
        zone = Zone(
            zone_id="test-zone",
            name="Zone de test",
            zone_type=ZoneType.INTRUSION,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        data = zone.to_dict()
        assert data['zone_type'] == "intrusion"
        
        zone_restored = Zone.from_dict(data)
        assert zone_restored.zone_id == zone.zone_id
        assert zone_restored.zone_type == ZoneType.INTRUSION


class TestZoneManager:
    """Tests pour la classe ZoneManager."""
    
    def test_initialization(self):
        """Test l'initialisation du gestionnaire."""
        manager = ZoneManager()
        assert len(manager.zones) == 0
    
    def test_create_zone(self):
        """Test la création d'une zone."""
        manager = ZoneManager()
        
        zone = manager.create_zone(
            zone_id="zone-1",
            name="Zone 1",
            zone_type=ZoneType.INTRUSION,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        assert zone.zone_id == "zone-1"
        assert len(manager.zones) == 1
    
    def test_create_duplicate_zone(self):
        """Test la création d'une zone dupliquée (doit échouer)."""
        manager = ZoneManager()
        
        manager.create_zone(
            zone_id="zone-1",
            name="Zone 1",
            zone_type=ZoneType.INTRUSION,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        with pytest.raises(ValueError):
            manager.create_zone(
                zone_id="zone-1",
                name="Zone 1 bis",
                zone_type=ZoneType.INTRUSION,
                polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
            )
    
    def test_get_zone(self):
        """Test la récupération d'une zone."""
        manager = ZoneManager()
        
        manager.create_zone(
            zone_id="zone-1",
            name="Zone 1",
            zone_type=ZoneType.INTRUSION,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        zone = manager.get_zone("zone-1")
        assert zone is not None
        assert zone.zone_id == "zone-1"
        
        zone_not_found = manager.get_zone("zone-999")
        assert zone_not_found is None
    
    def test_get_zones_by_type(self):
        """Test la récupération des zones par type."""
        manager = ZoneManager()
        
        manager.create_zone(
            zone_id="zone-1",
            name="Zone 1",
            zone_type=ZoneType.INTRUSION,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        manager.create_zone(
            zone_id="zone-2",
            name="Zone 2",
            zone_type=ZoneType.CROWD,
            polygon=[(200, 200), (300, 200), (300, 300), (200, 300)]
        )
        
        manager.create_zone(
            zone_id="zone-3",
            name="Zone 3",
            zone_type=ZoneType.INTRUSION,
            polygon=[(400, 400), (500, 400), (500, 500), (400, 500)]
        )
        
        intrusion_zones = manager.get_zones_by_type(ZoneType.INTRUSION)
        assert len(intrusion_zones) == 2
        
        crowd_zones = manager.get_zones_by_type(ZoneType.CROWD)
        assert len(crowd_zones) == 1
    
    def test_update_zone(self):
        """Test la mise à jour d'une zone."""
        manager = ZoneManager()
        
        manager.create_zone(
            zone_id="zone-1",
            name="Zone 1",
            zone_type=ZoneType.INTRUSION,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        updated = manager.update_zone("zone-1", name="Zone 1 modifiée")
        assert updated.name == "Zone 1 modifiée"
        
        not_found = manager.update_zone("zone-999", name="Test")
        assert not_found is None
    
    def test_delete_zone(self):
        """Test la suppression d'une zone."""
        manager = ZoneManager()
        
        manager.create_zone(
            zone_id="zone-1",
            name="Zone 1",
            zone_type=ZoneType.INTRUSION,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        assert manager.delete_zone("zone-1") == True
        assert len(manager.zones) == 0
        
        assert manager.delete_zone("zone-999") == False
    
    def test_check_intrusion(self):
        """Test la détection d'intrusion."""
        manager = ZoneManager()
        
        manager.create_zone(
            zone_id="zone-1",
            name="Zone 1",
            zone_type=ZoneType.INTRUSION,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        # Bbox à l'intérieur
        assert manager.check_intrusion([25, 25, 75, 75], "zone-1") == True
        
        # Bbox à l'extérieur
        assert manager.check_intrusion([125, 125, 175, 175], "zone-1") == False
    
    def test_check_all_intrusions(self):
        """Test la détection d'intrusion dans toutes les zones."""
        manager = ZoneManager()
        
        manager.create_zone(
            zone_id="zone-1",
            name="Zone 1",
            zone_type=ZoneType.INTRUSION,
            polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        manager.create_zone(
            zone_id="zone-2",
            name="Zone 2",
            zone_type=ZoneType.INTRUSION,
            polygon=[(200, 200), (300, 200), (300, 300), (200, 300)]
        )
        
        manager.create_zone(
            zone_id="zone-3",
            name="Zone 3",
            zone_type=ZoneType.CROWD,
            polygon=[(400, 400), (500, 400), (500, 500), (400, 500)]
        )
        
        # Bbox dans zone-1
        intrusions = manager.check_all_intrusions([25, 25, 75, 75])
        assert "zone-1" in intrusions
        assert "zone-2" not in intrusions
        
        # Bbox dans zone-2
        intrusions = manager.check_all_intrusions([225, 225, 275, 275])
        assert "zone-2" in intrusions
        assert "zone-1" not in intrusions
    
    def test_save_load_file(self):
        """Test la sauvegarde et le chargement depuis un fichier."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            manager = ZoneManager(storage_path=temp_path)
            
            manager.create_zone(
                zone_id="zone-1",
                name="Zone 1",
                zone_type=ZoneType.INTRUSION,
                polygon=[(0, 0), (100, 0), (100, 100), (0, 100)]
            )
            
            manager.create_zone(
                zone_id="zone-2",
                name="Zone 2",
                zone_type=ZoneType.CROWD,
                polygon=[(200, 200), (300, 200), (300, 300), (200, 300)]
            )
            
            manager.save_to_file()
            
            # Créer un nouveau gestionnaire et charger
            manager2 = ZoneManager(storage_path=temp_path)
            manager2.load_from_file()
            
            assert len(manager2.zones) == 2
            assert manager2.get_zone("zone-1") is not None
            assert manager2.get_zone("zone-2") is not None
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
