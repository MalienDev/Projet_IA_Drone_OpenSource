"""
Event persister service - subscribes to Redis and persists events to database.
"""

import asyncio
import json
import os
import redis.asyncio as redis
from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from ..api.schemas import EventCreate
from ..models.event import Event as EventModel


class EventPersister:
    """Subscribes to Redis alert channel and persists events to database."""

    def __init__(
        self,
        redis_host: str = None,
        redis_port: int = None,
        channel: str = None
    ):
        """
        Initialize the event persister.

        Args:
            redis_host: Redis host (default from env or "redis")
            redis_port: Redis port (default from env or 6379)
            channel: Redis channel to subscribe to (default from env or "alerts")
        """
        self.redis_host = redis_host or os.getenv("REDIS_HOST", "redis")
        self.redis_port = redis_port or int(os.getenv("REDIS_PORT", "6379"))
        self.channel = channel or os.getenv("REDIS_CHANNEL", "alerts")
        self.redis_client: redis.Redis = None
        self.pubsub = None
        self.running = False

    async def connect(self):
        """Connect to Redis and subscribe to the alert channel."""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True
            )
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe(self.channel)
            print(f"Event persister subscribed to Redis channel: {self.channel}")
        except Exception as e:
            print(f"Error connecting to Redis: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis."""
        self.running = False
        if self.pubsub:
            await self.pubsub.unsubscribe(self.channel)
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
        print("Event persister disconnected from Redis")

    def _persist_event(self, event_data: dict):
        """
        Persist an event to the database.

        Args:
            event_data: Event data from Redis (JSON dict)
        """
        db: Session = SessionLocal()
        try:
            # Check if event already exists
            existing = db.query(EventModel).filter(
                EventModel.alert_id == event_data.get("alert_id")
            ).first()
            if existing:
                print(f"Event {event_data.get('alert_id')} already exists, skipping")
                return

            # Create event from data
            event_create = EventCreate(**event_data)
            db_event = EventModel(**event_create.model_dump())
            db.add(db_event)
            db.commit()
            db.refresh(db_event)
            print(f"Persisted event {event_data.get('alert_id')} to database")
        except Exception as e:
            print(f"Error persisting event: {e}")
            db.rollback()
        finally:
            db.close()

    async def listen(self):
        """
        Listen for messages on the Redis channel and persist to database.

        This method runs in a loop until stopped.
        """
        if not self.pubsub:
            await self.connect()

        self.running = True
        print(f"Event persister listening on channel: {self.channel}")

        while self.running:
            try:
                message = await self.pubsub.get_message(timeout=1.0)
                if message and message["type"] == "message":
                    # Parse the alert data
                    event_data = json.loads(message["data"])
                    print(f"Received event for persistence: {event_data.get('alert_id')}")

                    # Persist to database (run in thread pool to avoid blocking)
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self._persist_event, event_data)

            except asyncio.CancelledError:
                print("Event persister cancelled")
                break
            except Exception as e:
                print(f"Error in event persister: {e}")
                # Reconnect after a delay
                await asyncio.sleep(5)
                try:
                    await self.connect()
                except Exception as reconnect_error:
                    print(f"Failed to reconnect: {reconnect_error}")

    async def stop(self):
        """Stop the listener."""
        self.running = False


# Global event persister instance
event_persister = EventPersister()
