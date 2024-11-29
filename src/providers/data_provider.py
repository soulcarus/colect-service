from abc import ABC, abstractmethod
from typing import Dict, Any, List
from clients.apodi_client import APODIClient
from clients.benatextil_client import BenatextilClient

class DataProvider(ABC):
    """Abstract base class for data providers."""

    @abstractmethod
    def collect_data(self) -> List[Dict[str, Any]]:
        """Collect data from the source."""
        pass

    @abstractmethod
    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """Validate collected data."""
        pass

class ApodiOpcuaProvider(DataProvider):
    """OPC UA data provider implementation."""

    def __init__(self, client: APODIClient, config: Dict[str, Any]):
        self.client = client
        self.config = config

    def collect_data(self) -> List[Dict[str, Any]]:
        """Collect data from Apodi OPC UA server."""
        with self.client:
            nodes = self._get_nodes()
            values = self.client.get_values(nodes)
            return self._format_data(values)

    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """Validate Apodi OPC UA data."""
        return all(self._validate_entry(entry) for entry in data)

    def _get_nodes(self):
        """Get nodes to collect data from."""
        root = self.client.get_objects_node()
        return [root.get_child(["2:"+node]) for node in self.config['nodes']]

    def _format_data(self, values: List[Any]) -> List[Dict[str, Any]]:
        """Format collected values into structured data."""
        return [{'node': node, 'value': value} 
                for node, value in zip(self.config['nodes'], values)]

    def _validate_entry(self, entry: Dict[str, Any]) -> bool:
        """Validate a single data entry."""
        return 'node' in entry and 'value' in entry

class BenatextilMqttProvider(DataProvider):
    """Benatextil MQTT data provider implementation."""

    def __init__(self, client: BenatextilClient, config: Dict[str, Any]):
        self.client = client
        self.config = config
        self.collected_data = []

    def collect_data(self) -> List[Dict[str, Any]]:
        """Collect data from Benatextil MQTT broker."""
        with self.client:
            self._subscribe_to_topics()
            # Wait for data collection
            return self.collected_data

    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """Validate BenatextilMQTT data."""
        return all(self._validate_entry(entry) for entry in data)

    def _subscribe_to_topics(self):
        """Subscribe to configured topics."""
        for topic in self.config['topics']:
            self.client.subscribe(topic, self._handle_message)

    def _handle_message(self, topic: str, payload: Any):
        """Handle incoming Benatextil MQTT messages."""
        self.collected_data.append({
            'topic': topic,
            'value': payload
        })

    def _validate_entry(self, entry: Dict[str, Any]) -> bool:
        """Validate a single data entry."""
        return 'topic' in entry and 'value' in entry