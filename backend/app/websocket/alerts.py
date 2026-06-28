"""
Redis alert subscriber for WebSocket broadcasting.
"""

import asyncio
import json
import os
import redis.asyncio as redis
from typing import Callable
from .manager import manager


class AlertSubscriber:
    """Subscribes to Redis alert channel and broadcasts to WebSocket clients."""

    def __init__(
        self,
        redis_host: str = None,
        redis_port: int = None,
        channel: str = None
    ):
        """
        Initialize the alert subscriber.

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
            print(f"Subscribed to Redis channel: {self.channel}")
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
        print("Disconnected from Redis")

    async def listen(self):
        """
        Listen for messages on the Redis channel and broadcast to WebSocket clients.

        This method runs in a loop until stopped.
        """
        if not self.pubsub:
            await self.connect()

        self.running = True
        print(f"Listening for alerts on channel: {self.channel}")

        while self.running:
            try:
                message = await self.pubsub.get_message(timeout=1.0)
                if message and message["type"] == "message":
                    # Parse the alert data
                    alert_data = json.loads(message["data"])
                    print(f"Received alert: {alert_data.get('alert_id')}")

                    # Broadcast to all WebSocket clients
                    if manager.get_connection_count() > 0:
                        await manager.broadcast(alert_data)
                        print(f"Broadcasted alert to {manager.get_connection_count()} clients")
                    else:
                        print("No WebSocket clients connected, alert not broadcasted")

            except asyncio.CancelledError:
                print("Alert listener cancelled")
                break
            except Exception as e:
                print(f"Error in alert listener: {e}")
                # Reconnect after a delay
                await asyncio.sleep(5)
                try:
                    await self.connect()
                except Exception as reconnect_error:
                    print(f"Failed to reconnect: {reconnect_error}")

    async def stop(self):
        """Stop the listener."""
        self.running = False


# Global alert subscriber instance
alert_subscriber = AlertSubscriber()
