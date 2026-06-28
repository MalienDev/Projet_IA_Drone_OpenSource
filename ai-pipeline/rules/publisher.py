"""
Event Publisher for publishing alerts to Redis message bus.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import redis

from .engine import AlertType, Severity


class EventPublisher:
    """
    Publishes alert events to Redis pub/sub channel.
    
    Events are published in the standardized JSON format defined in AGENTS.md section 9.
    """
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        channel: str = "alerts",
        drone_id: str = "drone-01"
    ):
        """
        Initialize the event publisher.
        
        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            channel: Redis pub/sub channel name
            drone_id: Default drone ID for events
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.channel = channel
        self.drone_id = drone_id
        self._redis_client: Optional[redis.Redis] = None
    
    def connect(self):
        """Connect to Redis server."""
        try:
            self._redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True
            )
            # Test connection
            self._redis_client.ping()
            print(f"Connected to Redis at {self.redis_host}:{self.redis_port}")
        except redis.ConnectionError as e:
            print(f"Failed to connect to Redis: {e}")
            self._redis_client = None
    
    def disconnect(self):
        """Disconnect from Redis server."""
        if self._redis_client:
            self._redis_client.close()
            self._redis_client = None
    
    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        if not self._redis_client:
            return False
        try:
            self._redis_client.ping()
            return True
        except redis.ConnectionError:
            return False
    
    def publish_alert(
        self,
        alert_type: AlertType,
        severity: Severity,
        confidence: float,
        bbox: List[float],
        track_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        geo_lat: Optional[float] = None,
        geo_lon: Optional[float] = None,
        snapshot_path: Optional[str] = None,
        clip_path: Optional[str] = None,
        requires_operator_ack: bool = False,
        drone_id: Optional[str] = None,
        timestamp: Optional[str] = None
    ) -> Optional[str]:
        """
        Publish an alert event to Redis.
        
        Args:
            alert_type: Type of alert
            severity: Severity level
            confidence: Detection confidence (0.0 to 1.0)
            bbox: Bounding box [x1, y1, x2, y2]
            track_id: Optional track identifier
            zone_id: Optional zone identifier
            geo_lat: Optional latitude
            geo_lon: Optional longitude
            snapshot_path: Optional path to snapshot image
            clip_path: Optional path to video clip
            requires_operator_ack: Whether operator acknowledgment is required
            drone_id: Drone ID (overrides default)
            timestamp: ISO 8601 timestamp (defaults to current time)
        
        Returns:
            Alert ID if published successfully, None otherwise
        """
        if not self.is_connected():
            print("Not connected to Redis, cannot publish alert")
            return None
        
        # Generate alert ID
        alert_id = str(uuid.uuid4())
        
        # Generate timestamp if not provided
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        
        # Build event payload according to AGENTS.md section 9
        event = {
            "alert_id": alert_id,
            "timestamp": timestamp,
            "drone_id": drone_id or self.drone_id,
            "type": alert_type.value,
            "severity": severity.value,
            "confidence": confidence,
            "bbox": bbox,
            "track_id": track_id,
            "zone_id": zone_id,
            "geo": {
                "lat": geo_lat,
                "lon": geo_lon
            },
            "snapshot_path": snapshot_path,
            "clip_path": clip_path,
            "requires_operator_ack": requires_operator_ack,
            "acknowledged_by": None,
            "acknowledged_at": None
        }
        
        try:
            # Publish to Redis channel
            self._redis_client.publish(self.channel, json.dumps(event))
            print(f"Published alert {alert_id} to channel {self.channel}")
            return alert_id
        except redis.RedisError as e:
            print(f"Failed to publish alert to Redis: {e}")
            return None
    
    def publish_batch_alerts(self, alerts: List[Dict[str, Any]]) -> int:
        """
        Publish multiple alerts in batch.
        
        Args:
            alerts: List of alert dictionaries with required fields
        
        Returns:
            Number of alerts successfully published
        """
        if not self.is_connected():
            print("Not connected to Redis, cannot publish alerts")
            return 0
        
        published_count = 0
        for alert in alerts:
            alert_id = self.publish_alert(**alert)
            if alert_id:
                published_count += 1
        
        return published_count
    
    def set_drone_id(self, drone_id: str):
        """
        Set the default drone ID for events.
        
        Args:
            drone_id: New drone ID
        """
        self.drone_id = drone_id
    
    def get_channel_name(self) -> str:
        """Get the current channel name."""
        return self.channel
