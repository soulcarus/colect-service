import paho.mqtt.client as mqtt
from typing import Callable, Any
from clients.abstract_client import AbstractClient

class BenatextilClient(AbstractClient):
    def __init__(self, broker: str, port: int = 1883):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self._connected = False
        self._callbacks = {}

    async def connect(self) -> None:
        """Connect to the Benatextil MQTT broker."""
        if not self._connected:
            self.client.connect(self.broker, self.port)
            self.client.loop_start()
            self._connected = True

    async def disconnect(self) -> None:
        """Disconnect from the Benatextil MQTT broker."""
        if self._connected:
            self.client.loop_stop()
            self.client.disconnect()
            self._connected = False

    async def subscribe(self, topic: str, callback: Callable[[str, Any], None]) -> None:
        """Subscribe to a topic with a callback."""
        self._callbacks[topic] = callback
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, lambda client, userdata, message: 
            callback(message.topic, message.payload))

    async def publish(self, topic: str, payload: str) -> None:
        """Publish a message to a topic."""
        self.client.publish(topic, payload)

    async def __enter__(self):
        """Context manager entry."""
        await self.connect()
        return self

    async def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()
