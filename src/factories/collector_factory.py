from abc import ABC, abstractmethod
from clients.opc_ua_client import OPCUAClient
from clients.mqtt_client import MQTTClient
from strategies.mqtt_strategy import MQTTClient, MQTTStrategy
from strategies.opcua_strategy import OPCUAClient, OPCUAStrategy
from typing import Dict, Any

class CollectorFactory(ABC):
    """Abstract factory for creating collector components."""
    
    @abstractmethod
    def create_client(self):
        """Create a client instance."""
        pass

    @abstractmethod
    def create_strategy(self):
        """Create a collection strategy instance."""
        pass

class OPCUACollectorFactory(CollectorFactory):
    """Factory for creating OPC UA collector components."""

    def __init__(self, industry_id: str, config: Dict[str, Any]):
        self.industry_id = industry_id
        self.config = config

    def create_client(self) -> OPCUAClient:
        """Create an OPC UA client instance."""
        return OPCUAClient(self.config['server_link'])

    def create_strategy(self) -> OPCUAStrategy:
        """Create an OPC UA collection strategy instance."""
        client = self.create_client()
        return OPCUAStrategy(client, self.industry_id, self.config)

class MQTTCollectorFactory(CollectorFactory):
    """Factory for creating MQTT collector components."""

    def __init__(self, industry_id: str, config: Dict[str, Any]):
        self.industry_id = industry_id
        self.config = config

    def create_client(self) -> MQTTClient:
        """Create an MQTT client instance."""
        return MQTTClient(self.config['broker'], self.config.get('port', 1883))

    def create_strategy(self) -> MQTTStrategy:
        """Create an MQTT collection strategy instance."""
        client = self.create_client()
        return MQTTStrategy(client, self.industry_id, self.config)