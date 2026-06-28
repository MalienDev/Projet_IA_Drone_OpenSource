"""
Alert Manager for cooldown and anti-spam mechanisms.
"""

import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from threading import Lock

from .engine import AlertType, Severity


@dataclass
class CooldownConfig:
    """Configuration for cooldown periods."""
    default_cooldown: int = 60  # seconds
    per_type_cooldown: Dict[AlertType, int] = field(default_factory=dict)
    per_zone_cooldown: Dict[str, int] = field(default_factory=dict)
    per_track_cooldown: int = 30  # seconds for same track_id


@dataclass
class AlertState:
    """State of a recent alert for cooldown tracking."""
    timestamp: float
    alert_type: AlertType
    zone_id: Optional[str]
    track_id: Optional[str]
    severity: Severity


class AlertManager:
    """
    Manages alert cooldown and anti-spam mechanisms.
    
    This prevents alert spam by:
    - Enforcing cooldown periods per alert type
    - Enforcing cooldown periods per zone
    - Enforcing cooldown periods per track_id (same object)
    - Tracking recent alerts for rate limiting
    """
    
    def __init__(self, cooldown_config: Optional[CooldownConfig] = None):
        """
        Initialize the alert manager.
        
        Args:
            cooldown_config: Configuration for cooldown periods
        """
        self.config = cooldown_config or CooldownConfig()
        self._recent_alerts: Dict[str, AlertState] = {}
        self._lock = Lock()
    
    def _get_alert_key(
        self,
        alert_type: AlertType,
        zone_id: Optional[str],
        track_id: Optional[str]
    ) -> str:
        """
        Generate a unique key for an alert.
        
        Args:
            alert_type: Type of alert
            zone_id: Zone identifier
            track_id: Track identifier
        
        Returns:
            Unique key string
        """
        parts = [alert_type.value]
        if zone_id:
            parts.append(f"zone:{zone_id}")
        if track_id:
            parts.append(f"track:{track_id}")
        return "|".join(parts)
    
    def get_cooldown_seconds(
        self,
        alert_type: AlertType,
        zone_id: Optional[str] = None
    ) -> int:
        """
        Get the cooldown period for a specific alert.
        
        Args:
            alert_type: Type of alert
            zone_id: Optional zone identifier
        
        Returns:
            Cooldown period in seconds
        """
        # Check per-type cooldown first
        if alert_type in self.config.per_type_cooldown:
            return self.config.per_type_cooldown[alert_type]
        
        # Check per-zone cooldown
        if zone_id and zone_id in self.config.per_zone_cooldown:
            return self.config.per_zone_cooldown[zone_id]
        
        # Default cooldown
        return self.config.default_cooldown
    
    def should_alert(
        self,
        alert_type: AlertType,
        zone_id: Optional[str] = None,
        track_id: Optional[str] = None,
        timestamp: Optional[float] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if an alert should be allowed (not in cooldown).
        
        Cooldown strategy:
        - If track_id is present: check per-track cooldown (allows different tracks in same zone)
        - If no track_id but zone_id: check per-type+zone cooldown
        - If no track_id and no zone_id: check per-type cooldown
        
        Args:
            alert_type: Type of alert
            zone_id: Optional zone identifier
            track_id: Optional track identifier
            timestamp: Current timestamp (defaults to time.time())
        
        Returns:
            Tuple of (should_alert, reason_if_blocked)
        """
        if timestamp is None:
            timestamp = time.time()
        
        with self._lock:
            # Check per-track cooldown first (highest priority)
            if track_id:
                track_key = f"track:{track_id}"
                if self._is_in_cooldown(track_key, timestamp, self.config.per_track_cooldown):
                    return False, f"Track {track_id} in cooldown"
            
            # If no track_id, check zone-based cooldown
            if zone_id:
                type_zone_key = f"type:{alert_type.value}|zone:{zone_id}"
                zone_cooldown = self.config.per_zone_cooldown.get(zone_id, self.get_cooldown_seconds(alert_type, zone_id))
                if self._is_in_cooldown(type_zone_key, timestamp, zone_cooldown):
                    return False, f"Alert type {alert_type.value} in zone {zone_id} in cooldown"
            else:
                # If no zone, check per-type cooldown
                type_key = f"type:{alert_type.value}"
                if self._is_in_cooldown(type_key, timestamp, self.get_cooldown_seconds(alert_type, zone_id)):
                    return False, f"Alert type {alert_type.value} in cooldown"
            
            return True, None
    
    def _is_in_cooldown(self, key: str, current_time: float, cooldown_seconds: int) -> bool:
        """
        Check if a specific key is in cooldown.
        
        Args:
            key: Alert key
            current_time: Current timestamp
            cooldown_seconds: Cooldown period in seconds
        
        Returns:
            True if in cooldown
        """
        if key not in self._recent_alerts:
            return False
        
        last_alert = self._recent_alerts[key]
        elapsed = current_time - last_alert.timestamp
        return elapsed < cooldown_seconds
    
    def record_alert(
        self,
        alert_type: AlertType,
        zone_id: Optional[str] = None,
        track_id: Optional[str] = None,
        severity: Severity = Severity.LOW,
        timestamp: Optional[float] = None
    ):
        """
        Record that an alert was sent.
        
        Args:
            alert_type: Type of alert
            zone_id: Optional zone identifier
            track_id: Optional track identifier
            severity: Severity of the alert
            timestamp: Timestamp (defaults to time.time())
        """
        if timestamp is None:
            timestamp = time.time()
        
        with self._lock:
            # If track_id is present, only record per-track (allows different tracks in same zone)
            if track_id:
                track_key = f"track:{track_id}"
                self._recent_alerts[track_key] = AlertState(
                    timestamp=timestamp,
                    alert_type=alert_type,
                    zone_id=zone_id,
                    track_id=track_id,
                    severity=severity
                )
            else:
                # If no track_id, record per-type+zone combination
                if zone_id:
                    type_zone_key = f"type:{alert_type.value}|zone:{zone_id}"
                    self._recent_alerts[type_zone_key] = AlertState(
                        timestamp=timestamp,
                        alert_type=alert_type,
                        zone_id=zone_id,
                        track_id=track_id,
                        severity=severity
                    )
                else:
                    # If no zone, record per-type only
                    type_key = f"type:{alert_type.value}"
                    self._recent_alerts[type_key] = AlertState(
                        timestamp=timestamp,
                        alert_type=alert_type,
                        zone_id=zone_id,
                        track_id=track_id,
                        severity=severity
                    )
    
    def cleanup_old_alerts(self, max_age_seconds: int = 3600):
        """
        Clean up old alert records to prevent memory bloat.
        
        Args:
            max_age_seconds: Maximum age of alerts to keep (default 1 hour)
        """
        current_time = time.time()
        
        with self._lock:
            keys_to_remove = []
            for key, alert_state in self._recent_alerts.items():
                age = current_time - alert_state.timestamp
                if age > max_age_seconds:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._recent_alerts[key]
    
    def get_recent_alerts_count(self, alert_type: Optional[AlertType] = None) -> int:
        """
        Get count of recent alerts (optionally filtered by type).
        
        Args:
            alert_type: Optional alert type filter
        
        Returns:
            Count of recent alerts
        """
        with self._lock:
            if alert_type is None:
                return len(self._recent_alerts)
            
            return sum(
                1 for state in self._recent_alerts.values()
                if state.alert_type == alert_type
            )
    
    def reset(self):
        """Reset all alert state (useful for testing)."""
        with self._lock:
            self._recent_alerts.clear()
