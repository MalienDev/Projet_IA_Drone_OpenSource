"""
Integration tests for rules engine (burst events, anti-spam).
"""

import pytest
import time
import sys
from pathlib import Path

# Add ai-pipeline to path for imports
ai_pipeline_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ai_pipeline_path))

from rules.engine import RuleEngine, AlertType, Severity
from rules.alert_manager import AlertManager, CooldownConfig


class TestBurstEvents:
    """Tests for handling burst of events."""
    
    def test_burst_same_type_no_cooldown(self):
        """Test that burst of same type without cooldown is handled."""
        engine = RuleEngine()
        manager = AlertManager()
        
        # Disable cooldown for this test
        manager.config.default_cooldown = 0
        
        alerts_generated = 0
        for i in range(10):
            classification = engine.classify_alert(
                alert_type=AlertType.PERSON,
                confidence=0.7
            )
            if classification["should_alert"]:
                should_alert, _ = manager.should_alert(
                    alert_type=AlertType.PERSON
                )
                if should_alert:
                    manager.record_alert(
                        alert_type=AlertType.PERSON,
                        severity=Severity(classification["severity"])
                    )
                    alerts_generated += 1
        
        assert alerts_generated == 10
    
    def test_burst_same_type_with_cooldown(self):
        """Test that burst of same type with cooldown is throttled."""
        engine = RuleEngine()
        manager = AlertManager()
        
        # Set short cooldown
        manager.config.default_cooldown = 1
        
        alerts_generated = 0
        for i in range(10):
            classification = engine.classify_alert(
                alert_type=AlertType.PERSON,
                confidence=0.7
            )
            if classification["should_alert"]:
                should_alert, _ = manager.should_alert(
                    alert_type=AlertType.PERSON
                )
                if should_alert:
                    manager.record_alert(
                        alert_type=AlertType.PERSON,
                        severity=Severity(classification["severity"])
                    )
                    alerts_generated += 1
        
        # Only first alert should pass (others blocked by cooldown)
        assert alerts_generated == 1
    
    def test_burst_different_tracks_same_zone(self):
        """Test that different tracks in same zone can alert."""
        engine = RuleEngine()
        manager = AlertManager()
        
        alerts_generated = 0
        for i in range(5):
            classification = engine.classify_alert(
                alert_type=AlertType.PERSON,
                confidence=0.7,
                zone_id="zone-1"
            )
            if classification["should_alert"]:
                should_alert, _ = manager.should_alert(
                    alert_type=AlertType.PERSON,
                    zone_id="zone-1",
                    track_id=f"track-{i}"
                )
                if should_alert:
                    manager.record_alert(
                        alert_type=AlertType.PERSON,
                        zone_id="zone-1",
                        track_id=f"track-{i}",
                        severity=Severity(classification["severity"])
                    )
                    alerts_generated += 1
        
        # All 5 different tracks should alert
        assert alerts_generated == 5
    
    def test_burst_same_track_different_zones(self):
        """Test that same track in different zones can alert."""
        engine = RuleEngine()
        manager = AlertManager()
        
        alerts_generated = 0
        for i in range(3):
            classification = engine.classify_alert(
                alert_type=AlertType.INTRUSION,
                confidence=0.7,
                zone_id=f"zone-{i}"
            )
            if classification["should_alert"]:
                should_alert, _ = manager.should_alert(
                    alert_type=AlertType.INTRUSION,
                    zone_id=f"zone-{i}",
                    track_id="track-123"
                )
                if should_alert:
                    manager.record_alert(
                        alert_type=AlertType.INTRUSION,
                        zone_id=f"zone-{i}",
                        track_id="track-123",
                        severity=Severity(classification["severity"])
                    )
                    alerts_generated += 1
        
        # Same track should be blocked by per-track cooldown
        assert alerts_generated == 1


class TestAntiSpam:
    """Tests for anti-spam mechanisms."""
    
    def test_weapon_alert_high_cooldown(self):
        """Test that weapon alerts have high cooldown (5 min)."""
        engine = RuleEngine()
        manager = AlertManager()
        
        # First weapon alert
        classification = engine.classify_alert(
            alert_type=AlertType.WEAPON_SUSPECTED,
            confidence=0.85
        )
        assert classification["should_alert"]
        assert classification["cooldown_seconds"] == 300
        
        should_alert, _ = manager.should_alert(
            alert_type=AlertType.WEAPON_SUSPECTED
        )
        assert should_alert is True
        
        manager.record_alert(
            alert_type=AlertType.WEAPON_SUSPECTED,
            severity=Severity.CRITICAL
        )
        
        # Immediate second weapon alert should be blocked
        should_alert, _ = manager.should_alert(
            alert_type=AlertType.WEAPON_SUSPECTED
        )
        assert should_alert is False
    
    def test_low_confidence_blocked(self):
        """Test that low confidence detections are blocked."""
        engine = RuleEngine()
        manager = AlertManager()
        
        # Weapon with low confidence
        classification = engine.classify_alert(
            alert_type=AlertType.WEAPON_SUSPECTED,
            confidence=0.5  # Below 0.8 threshold
        )
        assert classification["should_alert"] is False
        assert "below threshold" in classification["reason"]
    
    def test_crowd_size_upgrade(self):
        """Test that large crowds get higher severity."""
        engine = RuleEngine()
        
        # Small crowd
        classification_small = engine.classify_alert(
            alert_type=AlertType.CROWD,
            confidence=0.6,
            crowd_size=5
        )
        assert classification_small["severity"] == Severity.MEDIUM.value
        
        # Large crowd
        classification_large = engine.classify_alert(
            alert_type=AlertType.CROWD,
            confidence=0.6,
            crowd_size=25
        )
        assert classification_large["severity"] == Severity.HIGH.value
    
    def test_movement_speed_upgrade(self):
        """Test that fast foot movement gets higher severity."""
        engine = RuleEngine()
        
        # Normal walking
        classification_normal = engine.classify_alert(
            alert_type=AlertType.MOVEMENT_FOOT,
            confidence=0.6,
            speed=2
        )
        assert classification_normal["severity"] == Severity.LOW.value
        
        # Fast movement
        classification_fast = engine.classify_alert(
            alert_type=AlertType.MOVEMENT_FOOT,
            confidence=0.6,
            speed=15
        )
        assert classification_fast["severity"] == Severity.MEDIUM.value
    
    def test_operator_ack_required_for_critical(self):
        """Test that critical alerts require operator acknowledgment."""
        engine = RuleEngine()
        
        # Weapon alert
        classification = engine.classify_alert(
            alert_type=AlertType.WEAPON_SUSPECTED,
            confidence=0.85
        )
        assert classification["requires_operator_ack"] is True
        
        # Intrusion alert
        classification = engine.classify_alert(
            alert_type=AlertType.INTRUSION,
            confidence=0.7
        )
        assert classification["requires_operator_ack"] is True
        
        # Person alert
        classification = engine.classify_alert(
            alert_type=AlertType.PERSON,
            confidence=0.7
        )
        assert classification["requires_operator_ack"] is False


class TestMemoryManagement:
    """Tests for memory management in alert manager."""
    
    def test_cleanup_old_alerts(self):
        """Test that old alerts are cleaned up."""
        manager = AlertManager()
        
        # Record some alerts
        for i in range(10):
            manager.record_alert(
                alert_type=AlertType.PERSON,
                track_id=f"track-{i}",
                timestamp=time.time() - 4000  # Very old
            )
        
        count_before = manager.get_recent_alerts_count()
        manager.cleanup_old_alerts(max_age_seconds=3600)
        count_after = manager.get_recent_alerts_count()
        
        assert count_after < count_before
        assert count_after == 0  # All should be cleaned
    
    def test_memory_bloat_prevention(self):
        """Test that memory doesn't grow indefinitely."""
        manager = AlertManager()
        
        # Simulate many alerts over time
        for i in range(100):
            manager.record_alert(
                alert_type=AlertType.PERSON,
                track_id=f"track-{i % 10}",  # Only 10 unique tracks
                timestamp=time.time()
            )
        
        # Cleanup should keep memory in check
        manager.cleanup_old_alerts(max_age_seconds=3600)
        
        # Should have at most 10 entries (one per track)
        assert manager.get_recent_alerts_count() <= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
