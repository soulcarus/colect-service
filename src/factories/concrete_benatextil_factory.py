from factories.abstract_industry_factory import IndustryFactory
from typing import Dict, Any
from clients.benatextil_client import BenatextilClient
from strategies.concrete_mqtt_strategy import MqttStrategy
from clients.abstract_client import AbstractClient
from strategies.abstract_collector import AbstractStrategy

class BenatextilFactory(IndustryFactory):
    """Factory for creating Benatextil MQTT collector components."""

    def __init__(self, industry_id: str, config: Dict[str, Any]):
        self.industry_id = industry_id
        self.config = config

    def create_client(self) -> AbstractClient:
        """Create an Benatextil MQTT client instance."""
        return BenatextilClient(self.config['broker'], self.config.get('port', 1883))

    def create_strategy(self) -> AbstractStrategy:
        """Create an Benatextil MQTT collection strategy instance."""
        client = self.create_client()
        return MqttStrategy(client, self.industry_id, self.config)
