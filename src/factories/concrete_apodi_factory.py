from factories.abstract_industry_factory import IndustryFactory
from typing import Dict, Any
from clients.apodi_client import APODIClient
from strategies.concrete_opcua_strategy import OpcuaStrategy
from clients.abstract_client import AbstractClient
from strategies.abstract_collector import AbstractStrategy

class ApodiFactory(IndustryFactory):
    """Factory for creating Apodi OPC UA collector components."""

    def __init__(self, industry_id: str, config: Dict[str, Any]):
        self.industry_id = industry_id
        self.config = config

    def create_client(self) -> AbstractClient:
        """Create an Apodi OPC UA client instance."""
        return APODIClient(self.config['server_link'])

    def create_strategy(self) -> AbstractStrategy:
        """Create an Apodi OPC UA collection strategy instance."""
        client = self.create_client()
        return OpcuaStrategy(client, self.industry_id, self.config)
