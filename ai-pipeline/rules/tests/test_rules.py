"""
Unit tests for the rules engine module.
"""

import pytest
import time
import sys
from pathlib import Path

# Add ai-pipeline to path for imports
ai_pipeline_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ai_pipeline_path))

from rules.engine import RuleEngine, AlertType, Severity, AlertRule
from rules.alert_manager import AlertManager, CooldownConfig


class TestRuleEngine:
    """Tests for RuleEngine."""
    
    def test_initialization(self):
        """Test engine initialization with default rules."""
        engine = RuleEngine()
        assert len(engine.rules) == 7  # 7 alert types
        assert AlertType.WEAPON_SUSPECTED in engine.rules
    
    def test_custom_rules(self):
        """Test engine initialization with custom rules."""
        custom_rule = AlertRule(
            alert_type=AlertType.WEAPON_SUSPECTED,
            default_severity=Severity.HIGH,
            default_priority="high",
            requires_operator_ack=True,
            min_confidence=0.9,
            cooldown_seconds=600
        )
        engine = RuleEngine(custom_rules={AlertType.WEAPON_SUSPECTED: custom_rule})
        rule = engine.get_rule(AlertType.WEAPON_SUSPECTED)
        assert rule.min_confidence == 0.9
        assert rule.cooldown_seconds == 600
    
    def test_classify_weapon_alert(self):
        """Test classification of weapon alert."""
        engine = RuleEngine()
        result = engine.classify_alert(
            alert_type=AlertType.WEAPON_SUSPECTED,
            confidence=0.85
        )
        assert result["should_alert"] is True
        assert result["severity"] == Severity.CRITICAL.value
        assert result["requires_operator_ack"] is True
        assert result["cooldown_seconds"] == 300
    
    def test_classify_weapon_low_confidence(self):
        """Test weapon alert with low confidence is blocked."""
        engine = RuleEngine()
        result = engine.classify_alert(
            alert_type=AlertType.WEAPON_SUSPECTED,
            confidence=0.5
        )
        assert result["should_alert"] is False
        assert "below threshold" in result["reason"]
    
    def test_classify_intrusion_alert(self):
        """Test classification of intrusion alert."""
        engine = RuleEngine()
        result = engine.classify_alert(
            alert_type=AlertType.INTRUSION,
            confidence=0.7,
            zone_id="zone-perimeter"
        )
        assert result["should_alert"] is True
        assert result["severity"] == Severity.HIGH.value
        assert result["requires_operator_ack"] is True
    
    def test_classify_crowd_alert_small(self):
        """Test classification of small crowd."""
        engine = RuleEngine()
        result = engine.classify_alert(
            alert_type=AlertType.CROWD,
            confidence=0.6,
            crowd_size=5
        )
        assert result["should_alert"] is True
        assert result["severity"] == Severity.MEDIUM.value
    
    def test_classify_crowd_alert_large(self):
        """Test classification of large crowd (severity upgrade)."""
        engine = RuleEngine()
        result = engine.classify_alert(
            alert_type=AlertType.CROWD,
            confidence=0.6,
            crowd_size=20
        )
        assert result["should_alert"] is True
        assert result["severity"] == Severity.HIGH.value
    
    def test_should_alert_quick_check(self):
        """Test quick should_alert check."""
        engine = RuleEngine()
        assert engine.should_alert(AlertType.WEAPON_SUSPECTED, 0.9) is True
        assert engine.should_alert(AlertType.WEAPON_SUSPECTED, 0.5) is False
    
    def test_movement_foot_fast(self):
        """Test fast foot movement severity upgrade."""
        engine = RuleEngine()
        result = engine.classify_alert(
            alert_type=AlertType.MOVEMENT_FOOT,
            confidence=0.6,
            speed=15
        )
        assert result["should_alert"] is True
        assert result["severity"] == Severity.MEDIUM.value


class TestAlertManager:
    """Tests for AlertManager."""
    
    def test_initialization(self):
        """Test manager initialization."""
        manager = AlertManager()
        assert manager.config.default_cooldown == 60
        assert manager.config.per_track_cooldown == 30
    
    def test_custom_cooldown_config(self):
        """Test manager with custom cooldown config."""
        config = CooldownConfig(
            default_cooldown=120,
            per_track_cooldown=60
        )
        manager = AlertManager(cooldown_config=config)
        assert manager.config.default_cooldown == 120
        assert manager.config.per_track_cooldown == 60
    
    def test_first_alert_allowed(self):
        """Test first alert is always allowed."""
        manager = AlertManager()
        should_alert, reason = manager.should_alert(
            alert_type=AlertType.INTRUSION,
            zone_id="zone-1"
        )
        assert should_alert is True
        assert reason is None
    
    def test_cooldown_after_alert(self):
        """Test alert is blocked during cooldown."""
        manager = AlertManager()
        
        # First alert
        manager.record_alert(
            alert_type=AlertType.INTRUSION,
            zone_id="zone-1",
            timestamp=time.time()
        )
        
        # Immediate second alert should be blocked
        should_alert, reason = manager.should_alert(
            alert_type=AlertType.INTRUSION,
            zone_id="zone-1"
        )
        assert should_alert is False
        assert "cooldown" in reason.lower()
    
    def test_cooldown_expiry(self):
        """Test alert is allowed after cooldown expires."""
        manager = AlertManager()
        
        # Record alert 2 seconds ago
        old_time = time.time() - 2
        manager.record_alert(
            alert_type=AlertType.PERSON,
            zone_id="zone-1",
            timestamp=old_time
        )
        
        # Person has 30s cooldown, so should still be blocked
        should_alert, _ = manager.should_alert(
            alert_type=AlertType.PERSON,
            zone_id="zone-1"
        )
        assert should_alert is False
        
        # But with a very old timestamp (beyond cooldown)
        very_old_time = time.time() - 100
        manager.record_alert(
            alert_type=AlertType.PERSON,
            zone_id="zone-1",
            timestamp=very_old_time
        )
        
        should_alert, _ = manager.should_alert(
            alert_type=AlertType.PERSON,
            zone_id="zone-1"
        )
        assert should_alert is True
    
    def test_per_type_cooldown(self):
        """Test cooldown per alert type (when no zone)."""
        manager = AlertManager()
        
        manager.record_alert(
            alert_type=AlertType.WEAPON_SUSPECTED,
            timestamp=time.time()
        )
        
        # Same type should be blocked (no zone)
        should_alert, _ = manager.should_alert(
            alert_type=AlertType.WEAPON_SUSPECTED
        )
        assert should_alert is False
        
        # Different type should be allowed
        should_alert, _ = manager.should_alert(
            alert_type=AlertType.INTRUSION
        )
        assert should_alert is True
    
    def test_per_track_cooldown(self):
        """Test cooldown per track ID."""
        manager = AlertManager()
        
        manager.record_alert(
            alert_type=AlertType.PERSON,
            track_id="track-123",
            zone_id="zone-1",
            timestamp=time.time()
        )
        
        # Same track should be blocked
        should_alert, _ = manager.should_alert(
            alert_type=AlertType.PERSON,
            track_id="track-123",
            zone_id="zone-1"
        )
        assert should_alert is False
        
        # Different track should be allowed (same zone, different track)
        should_alert, _ = manager.should_alert(
            alert_type=AlertType.PERSON,
            track_id="track-456",
            zone_id="zone-1"
        )
        assert should_alert is True
    
    def test_per_zone_cooldown(self):
        """Test cooldown per zone."""
        manager = AlertManager()
        
        manager.record_alert(
            alert_type=AlertType.INTRUSION,
            zone_id="zone-north",
            timestamp=time.time()
        )
        
        # Same zone should be blocked
        should_alert, _ = manager.should_alert(
            alert_type=AlertType.INTRUSION,
            zone_id="zone-north"
        )
        assert should_alert is False
        
        # Different zone should be allowed
        should_alert, _ = manager.should_alert(
            alert_type=AlertType.INTRUSION,
            zone_id="zone-south"
        )
        assert should_alert is True
    
    def test_cleanup_old_alerts(self):
        """Test cleanup of old alert records."""
        manager = AlertManager()
        
        # Record some alerts
        manager.record_alert(
            alert_type=AlertType.PERSON,
            track_id="track-1",
            timestamp=time.time()
        )
        manager.record_alert(
            alert_type=AlertType.PERSON,
            track_id="track-2",
            timestamp=time.time() - 4000  # Very old
        )
        
        count_before = manager.get_recent_alerts_count()
        manager.cleanup_old_alerts(max_age_seconds=3600)
        count_after = manager.get_recent_alerts_count()
        
        assert count_after < count_before
    
    def test_reset(self):
        """Test reset of alert state."""
        manager = AlertManager()
        
        manager.record_alert(
            alert_type=AlertType.PERSON,
            track_id="track-1",
            timestamp=time.time()
        )
        
        assert manager.get_recent_alerts_count() > 0
        
        manager.reset()
        
        assert manager.get_recent_alerts_count() == 0
    
    def test_get_cooldown_seconds(self):
        """Test getting cooldown period."""
        config = CooldownConfig(
            default_cooldown=60,
            per_type_cooldown={AlertType.WEAPON_SUSPECTED: 300}
        )
        manager = AlertManager(cooldown_config=config)
        
        cooldown = manager.get_cooldown_seconds(AlertType.WEAPON_SUSPECTED)
        assert cooldown == 300
        
        cooldown = manager.get_cooldown_seconds(AlertType.PERSON)
        assert cooldown == 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
