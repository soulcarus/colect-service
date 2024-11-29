from typing import Dict, Any, List, Tuple
from clients.apodi_client import APODIClient
from utils.logger import log
import pendulum
from strategies.abstract_collector import CollectorStrategy

class ApodiOpcuaStrategy(CollectorStrategy):
    """Strategy for collecting data from an OPC UA server."""

    def __init__(self, client: APODIClient, industry_id: str, config: Dict[str, Any]):
        """
        Initialize the OPC UA strategy.

        Args:
            client (OPCUAClient): OPC UA client for communication.
            industry_id (str): Industry identifier.
            config (Dict[str, Any]): Configuration dictionary.
        """
        self.client = client
        self.industry_id = industry_id
        self.config = config

    @staticmethod
    def get_tag_id(tag: str) -> Tuple[str, str, str]:
        """
        Split a full tag ID into its hierarchical components.

        Args:
            tag (str): Full tag ID (e.g., "EIP.PLC04.CM2_PV_PRODUCT").

        Returns:
            Tuple[str, str, str]: Tuple containing the first, second, and remaining parts of the tag.
        """
        parts = tag.split(".")
        if len(parts) < 3:
            raise ValueError(f"Invalid tag format: {tag}")
        first_point, second_point, *remaining_parts = parts
        remaining_tag = ".".join(remaining_parts)
        return first_point, second_point, remaining_tag

    def collect_data(self) -> Dict[str, Any]:
        """
        Collect data from the OPC UA server.

        Returns:
            Dict[str, Any]: Dictionary containing the raw values.
        """
        if 'tags' not in self.config or not isinstance(self.config['tags'], list):
            raise ValueError("Configuração inválida: 'tags' deve ser uma lista de IDs de tags.")

        try:
            self.client.connect()
            raw_values = []
            root = self.client.get_objects_node()

            for tag_id in self.config['tags']:
                try:
                    first_point, second_point, remaining_tag = self.get_tag_id(tag_id)
                    log.debug(f"Resolving node for tag: {tag_id}")
                    node = self._get_node(root, first_point, second_point, remaining_tag)
                    value = node.get_value()
                    raw_values.append((tag_id, value))
                    log.info(f"Successfully collected data for tag: {tag_id}")
                except Exception as e:
                    log.error(f"Error collecting tag {tag_id}: {e}")

            return {'raw_values': raw_values}
        finally:
            self.client.disconnect()

    def process_data(self, data: Dict[str, Any], timestamp: pendulum.DateTime):
        """
        Process and store the collected data.

        Args:
            data (Dict[str, Any]): Collected data.
            timestamp (pendulum.DateTime): Timestamp for the collected data.
        """
        from utils.mongodb import get_database

        if self.validate_data(data):
            db = get_database(self.industry_id)
            collection = db['collections']

            document = {
                'industry_id': self.industry_id,
                'timestamp': timestamp,
                'raw_values': data['raw_values']
            }

            collection.insert_one(document)
            log.info(f"Data successfully stored for industry {self.industry_id}.")
        else:
            log.error(f"Invalid data collected for industry {self.industry_id}.")

    @staticmethod
    def validate_data(data: Dict[str, Any]) -> bool:
        """
        Validate the collected data.

        Args:
            data (Dict[str, Any]): Data to validate.

        Returns:
            bool: True if the data is valid, False otherwise.
        """
        if not isinstance(data, dict):
            return False

        required_keys = {'raw_values'}
        if not all(key in data for key in required_keys):
            return False

        return isinstance(data['raw_values'], list)

    def _get_node(self, root, first_point: str, second_point: str, tag_id: str):
        """
        Resolve a node in the OPC UA server.

        Args:
            root: Root node from which to start navigation.
            first_point (str): First level in the tag hierarchy.
            second_point (str): Second level in the tag hierarchy.
            tag_id (str): Remaining part of the tag ID.

        Returns:
            Node: Resolved OPC UA node.
        """
        log.debug(f"Attempting to resolve node for tag: {tag_id}")
        try:
            node = root.get_child([f"2:{first_point}", f"2:{second_point}", f"2:{tag_id}"])
            log.debug(f"Successfully resolved node for tag: {tag_id}")
            return node
        except Exception as e:
            log.error(f"Failed to resolve node for tag {tag_id}: {e}")
            raise