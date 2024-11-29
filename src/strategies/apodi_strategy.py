import traceback
from typing import Dict, Any, List, Tuple
from clients.apodi_client import APODIClient
from utils.logger import log
import pendulum
from strategies.abstract_collector import CollectorStrategy

class ApodiOpcuaStrategy(CollectorStrategy):
    """Strategy for collecting data from an OPC UA server."""

    def __init__(self, client: APODIClient, industry_id: str, config: Dict[str, Any]):
        self.client = client
        self.industry_id = industry_id
        self.config = config

    @staticmethod
    def get_tag_id(tag: str) -> Tuple[str, str, str]:
        parts = tag.split(".")
        if len(parts) < 3:
            raise ValueError(f"Invalid tag format: {tag}")
        first_point, second_point, *remaining_parts = parts
        remaining_tag = ".".join(remaining_parts)
        return first_point, second_point, remaining_tag

    async def collect_data(self) -> Dict[str, Any]:
        if 'tags' not in self.config or not isinstance(self.config['tags'], list):
            raise ValueError("Configuração inválida: 'tags' deve ser uma lista de IDs de tags.")

        try:
            await self.client.connect()
            raw_values = []
            root = await self.client.get_objects_node()

            for tag_id in self.config['tags']:
                try:
                    first_point, second_point, remaining_tag = self.get_tag_id(tag_id)
                    node = await self._get_node(root, first_point, second_point, remaining_tag)
                    value = node.get_value()
                    raw_values.append((tag_id, value))
                except Exception as e:
                    log.error(f"Error collecting tag {tag_id}: {e}")
                    log.error(traceback.format_exc())

            return {'raw_values': raw_values}
        finally:
            await self.client.disconnect()

    async def process_data(self, data: Dict[str, Any], timestamp: pendulum.DateTime):
        from utils.mongodb import get_database

        if await self.validate_data(data):
            db = get_database(self.industry_id)
            collection = db['collections']

            document = {
                'industry_id': self.industry_id,
                'timestamp': timestamp,
                'raw_values': data['raw_values']
            }

            collection.insert_one(document)
        else:
            log.error(f"Invalid data collected for industry {self.industry_id}.")

    @staticmethod
    async def validate_data(data: Dict[str, Any]) -> bool:
        if not isinstance(data, dict):
            return False

        required_keys = {'raw_values'}
        if not all(key in data for key in required_keys):
            return False

        return isinstance(data['raw_values'], list)

    async def _get_node(self, root, first_point: str, second_point: str, tag_id: str):
        try:
            node = root.get_child([f"2:{first_point}", f"2:{second_point}", f"2:{tag_id}"])
            return node
        except Exception as e:
            log.error(f"Failed to resolve node for tag {tag_id}: {e}")