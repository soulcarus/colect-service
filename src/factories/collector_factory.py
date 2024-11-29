from abc import ABC, abstractmethod
from clients.apodi_client import APODIClient
from clients.benatextil_client import BenatextilClient
from strategies.benatextil_strategy import BenatextilMqttStrategy
from strategies.apodi_strategy import ApodiOpcuaStrategy
from typing import Dict, Any

class IndustryFactory(ABC):
    """Abstract factory for creating collector components."""
    
    @abstractmethod
    def create_client(self):
        """Create a client instance."""
        pass

    @abstractmethod
    def create_strategy(self):
        """Create a collection strategy instance."""
        pass

class ApodiOpcuaFactory(IndustryFactory):
    """Factory for creating Apodi OPC UA collector components."""

    def __init__(self, industry_id: str, config: Dict[str, Any]):
        self.industry_id = industry_id
        self.config = config

    def create_client(self) -> APODIClient:
        """Create an Apodi OPC UA client instance."""
        return APODIClient(self.config['server_link'])

    def create_strategy(self) -> ApodiOpcuaStrategy:
        """Create an Apodi OPC UA collection strategy instance."""
        client = self.create_client()
        return ApodiOpcuaStrategy(client, self.industry_id, self.config)

class BenatextilMQTTFactory(IndustryFactory):
    """Factory for creating Benatextil MQTT collector components."""

    def __init__(self, industry_id: str, config: Dict[str, Any]):
        self.industry_id = industry_id
        self.config = config

    def create_client(self) -> BenatextilClient:
        """Create an Benatextil MQTT client instance."""
        return BenatextilClient(self.config['broker'], self.config.get('port', 1883))

    def create_strategy(self) -> BenatextilMqttStrategy:
        """Create an Benatextil MQTT collection strategy instance."""
        client = self.create_client()
        return BenatextilMqttStrategy(client, self.industry_id, self.config)