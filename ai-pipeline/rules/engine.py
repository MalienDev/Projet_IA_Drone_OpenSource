"""
Rule Engine for alert prioritization and severity classification.
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class AlertType(str, Enum):
    """Types of alerts that can be generated."""
    WEAPON_SUSPECTED = "weapon_suspected"
    INTRUSION = "intrusion"
    CROWD = "crowd"
    PERSON = "person"
    VEHICLE = "vehicle"
    MOVEMENT_MOTORBIKE = "movement_motorbike"
    MOVEMENT_FOOT = "movement_foot"


class Severity(str, Enum):
    """Severity levels for alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertPriority(str, Enum):
    """Priority levels for alert processing."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class AlertRule:
    """Rule configuration for a specific alert type."""
    alert_type: AlertType
    default_severity: Severity
    default_priority: AlertPriority
    requires_operator_ack: bool
    min_confidence: float
    cooldown_seconds: int


class RuleEngine:
    """
    Centralized business logic for alert classification and prioritization.
    
    This engine determines:
    - Severity of alerts based on type and context
    - Priority for processing
    - Whether operator acknowledgment is required
    - Cooldown periods to prevent spam
    """
    
    # Default rules configuration (can be overridden)
    DEFAULT_RULES: Dict[AlertType, AlertRule] = {
        AlertType.WEAPON_SUSPECTED: AlertRule(
            alert_type=AlertType.WEAPON_SUSPECTED,
            default_severity=Severity.CRITICAL,
            default_priority=AlertPriority.URGENT,
            requires_operator_ack=True,
            min_confidence=0.8,
            cooldown_seconds=300  # 5 minutes
        ),
        AlertType.INTRUSION: AlertRule(
            alert_type=AlertType.INTRUSION,
            default_severity=Severity.HIGH,
            default_priority=AlertPriority.HIGH,
            requires_operator_ack=True,
            min_confidence=0.6,
            cooldown_seconds=60  # 1 minute
        ),
        AlertType.CROWD: AlertRule(
            alert_type=AlertType.CROWD,
            default_severity=Severity.MEDIUM,
            default_priority=AlertPriority.MEDIUM,
            requires_operator_ack=False,
            min_confidence=0.5,
            cooldown_seconds=120  # 2 minutes
        ),
        AlertType.PERSON: AlertRule(
            alert_type=AlertType.PERSON,
            default_severity=Severity.LOW,
            default_priority=AlertPriority.LOW,
            requires_operator_ack=False,
            min_confidence=0.5,
            cooldown_seconds=30  # 30 seconds
        ),
        AlertType.VEHICLE: AlertRule(
            alert_type=AlertType.VEHICLE,
            default_severity=Severity.LOW,
            default_priority=AlertPriority.LOW,
            requires_operator_ack=False,
            min_confidence=0.5,
            cooldown_seconds=30  # 30 seconds
        ),
        AlertType.MOVEMENT_MOTORBIKE: AlertRule(
            alert_type=AlertType.MOVEMENT_MOTORBIKE,
            default_severity=Severity.MEDIUM,
            default_priority=AlertPriority.MEDIUM,
            requires_operator_ack=False,
            min_confidence=0.5,
            cooldown_seconds=60  # 1 minute
        ),
        AlertType.MOVEMENT_FOOT: AlertRule(
            alert_type=AlertType.MOVEMENT_FOOT,
            default_severity=Severity.LOW,
            default_priority=AlertPriority.LOW,
            requires_operator_ack=False,
            min_confidence=0.5,
            cooldown_seconds=60  # 1 minute
        ),
    }
    
    def __init__(self, custom_rules: Optional[Dict[AlertType, AlertRule]] = None):
        """
        Initialize the rule engine.
        
        Args:
            custom_rules: Optional custom rules to override defaults
        """
        self.rules = self.DEFAULT_RULES.copy()
        if custom_rules:
            self.rules.update(custom_rules)
    
    def get_rule(self, alert_type: AlertType) -> AlertRule:
        """Get the rule for a specific alert type."""
        return self.rules.get(alert_type, self.DEFAULT_RULES[AlertType.PERSON])
    
    def classify_alert(
        self,
        alert_type: AlertType,
        confidence: float,
        zone_id: Optional[str] = None,
        **context
    ) -> Dict[str, Any]:
        """
        Classify an alert with severity, priority, and requirements.
        
        Args:
            alert_type: Type of the alert
            confidence: Detection confidence (0.0 to 1.0)
            zone_id: Optional zone identifier
            **context: Additional context (e.g., crowd size, speed)
        
        Returns:
            Dictionary with classification results
        """
        rule = self.get_rule(alert_type)
        
        # Check minimum confidence threshold
        if confidence < rule.min_confidence:
            return {
                "should_alert": False,
                "reason": f"Confidence {confidence:.2f} below threshold {rule.min_confidence}"
            }
        
        # Adjust severity based on context
        severity = self._adjust_severity(rule.default_severity, alert_type, context)
        
        return {
            "should_alert": True,
            "severity": severity.value,
            "priority": rule.default_priority.value,
            "requires_operator_ack": rule.requires_operator_ack,
            "cooldown_seconds": rule.cooldown_seconds,
            "alert_type": alert_type.value,
        }
    
    def _adjust_severity(self, base_severity: Severity, alert_type: AlertType, context: Dict[str, Any]) -> Severity:
        """
        Adjust severity based on contextual factors.
        
        Args:
            base_severity: Base severity from rule
            alert_type: Type of alert
            context: Additional context
        
        Returns:
            Adjusted severity
        """
        # Crowd size adjustment
        if alert_type == AlertType.CROWD:
            crowd_size = context.get("crowd_size", 0)
            if crowd_size >= 20:
                return Severity.HIGH
            elif crowd_size >= 10:
                return Severity.MEDIUM
        
        # Movement speed adjustment
        if alert_type == AlertType.MOVEMENT_FOOT:
            speed = context.get("speed", 0)
            if speed > 10:  # Very fast movement
                return Severity.MEDIUM
        
        return base_severity
    
    def should_alert(
        self,
        alert_type: AlertType,
        confidence: float,
        zone_id: Optional[str] = None,
        **context
    ) -> bool:
        """
        Quick check if an alert should be generated.
        
        Args:
            alert_type: Type of the alert
            confidence: Detection confidence
            zone_id: Optional zone identifier
            **context: Additional context
        
        Returns:
            True if alert should be generated
        """
        classification = self.classify_alert(alert_type, confidence, zone_id, **context)
        return classification["should_alert"]
