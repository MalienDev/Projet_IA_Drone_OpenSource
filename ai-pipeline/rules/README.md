# Rules Engine Module

This module contains the business logic for alert classification, prioritization, and anti-spam mechanisms.

## Components

### 1. RuleEngine (`engine.py`)
Centralized business logic for alert classification and prioritization.

**Features:**
- Alert type classification (weapon, intrusion, crowd, person, vehicle, movement)
- Severity assignment based on type and context
- Priority determination
- Operator acknowledgment requirements
- Minimum confidence thresholds
- Cooldown period configuration

**Alert Types:**
- `WEAPON_SUSPECTED`: Critical, requires operator confirmation
- `INTRUSION`: High, requires operator acknowledgment
- `CROWD`: Medium, severity upgrades with crowd size
- `PERSON`: Low, informational
- `VEHICLE`: Low, informational
- `MOVEMENT_MOTORBIKE`: Medium
- `MOVEMENT_FOOT`: Low, upgrades with speed

**Usage:**
```python
from ai_pipeline.rules.engine import RuleEngine, AlertType, Severity

engine = RuleEngine()
result = engine.classify_alert(
    alert_type=AlertType.WEAPON_SUSPECTED,
    confidence=0.85,
    zone_id="zone-perimeter"
)
# Returns: {"should_alert": True, "severity": "critical", ...}
```

### 2. AlertManager (`alert_manager.py`)
Manages alert cooldown and anti-spam mechanisms.

**Features:**
- Per-track cooldown (same object won't spam)
- Per-zone cooldown (same zone won't spam)
- Per-type cooldown (global for alerts without zone/track)
- Configurable cooldown periods
- Automatic cleanup of old records
- Thread-safe operations

**Cooldown Strategy:**
- If `track_id` is present: check per-track cooldown (allows different tracks in same zone)
- If no `track_id` but `zone_id`: check per-type+zone cooldown
- If no `track_id` and no `zone_id`: check per-type cooldown

**Usage:**
```python
from ai_pipeline.rules.alert_manager import AlertManager, CooldownConfig

config = CooldownConfig(
    default_cooldown=60,
    per_track_cooldown=30
)
manager = AlertManager(cooldown_config=config)

should_alert, reason = manager.should_alert(
    alert_type=AlertType.INTRUSION,
    zone_id="zone-north",
    track_id="track-123"
)

if should_alert:
    manager.record_alert(
        alert_type=AlertType.INTRUSION,
        zone_id="zone-north",
        track_id="track-123",
        severity=Severity.HIGH
    )
```

### 3. EventPublisher (`publisher.py`)
Publishes alert events to Redis pub/sub channel.

**Features:**
- Standardized JSON format (per AGENTS.md section 9)
- Redis connection management
- Batch alert publishing
- Automatic timestamp generation
- UUID generation for alert IDs

**Event Format:**
```json
{
  "alert_id": "uuid-v4",
  "timestamp": "2026-06-28T10:15:30Z",
  "drone_id": "drone-01",
  "type": "weapon_suspected",
  "severity": "critical",
  "confidence": 0.85,
  "bbox": [0, 0, 0, 0],
  "track_id": "track-123",
  "zone_id": "zone-perimeter",
  "geo": {"lat": null, "lon": null},
  "snapshot_path": "/media/snapshots/....jpg",
  "clip_path": "/media/clips/....mp4",
  "requires_operator_ack": true,
  "acknowledged_by": null,
  "acknowledged_at": null
}
```

**Usage:**
```python
from ai_pipeline.rules.publisher import EventPublisher
from ai_pipeline.rules.engine import AlertType, Severity

publisher = EventPublisher(
    redis_host="localhost",
    redis_port=6379,
    channel="alerts",
    drone_id="drone-01"
)
publisher.connect()

alert_id = publisher.publish_alert(
    alert_type=AlertType.WEAPON_SUSPECTED,
    severity=Severity.CRITICAL,
    confidence=0.85,
    bbox=[100, 100, 200, 200],
    track_id="track-123",
    zone_id="zone-perimeter",
    requires_operator_ack=True
)
```

## Installation

```bash
cd ai-pipeline/rules
pip install -r requirements.txt
```

## Testing

```bash
cd ai-pipeline/rules
python -m pytest tests/test_rules.py -v
```

## Default Cooldown Periods

| Alert Type | Cooldown (seconds) |
|------------|-------------------|
| WEAPON_SUSPECTED | 300 (5 min) |
| INTRUSION | 60 (1 min) |
| CROWD | 120 (2 min) |
| PERSON | 30 (30 sec) |
| VEHICLE | 30 (30 sec) |
| MOVEMENT_MOTORBIKE | 60 (1 min) |
| MOVEMENT_FOOT | 60 (1 min) |
| Per-track | 30 (30 sec) |

## License

- **Redis client**: BSD-3
- **Module code**: MIT (project license)
