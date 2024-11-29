from typing import Dict, Any, List
from clients.benatextil_client import BenatextilClient
from utils.logger import log
import pendulum
import asyncio

from strategies.abstract_collector import CollectorStrategy

class BenatextilMqttStrategy(CollectorStrategy):
    """MQTT collection strategy implementation."""

    def __init__(self, client: BenatextilClient, industry_id: str, config: Dict[str, Any]):
        self.client = client
        self.industry_id = industry_id
        self.config = config
        self.collected_data = []

    async def collect_data(self) -> Dict[str, Any]:
        self.collected_data = []
        await self.client.connect()

        async def message_handler(topic: str, payload: Any):
            self.collected_data.append((topic, payload))

        for topic in self.config['topics']:
            await self.client.subscribe(topic, message_handler)

        await asyncio.sleep(self.config.get('collection_timeout', 5))
        await self.client.disconnect()

        return {
            'raw_values': self.collected_data,
            'quality': self._get_quality_values()
        }

    async def process_data(self, data: Dict[str, Any], timestamp: pendulum.DateTime):
        from utils.mongodb import get_database

        if await self.validate_data(data):
            db = get_database(self.industry_id)
            collection = db['collections']

            document = {
                'industry_id': self.industry_id,
                'timestamp': timestamp,
                'raw_values': data['raw_values'],
                'quality': data['quality']
            }

            await collection.insert_one(document)
        else:
            log.error(f"Invalid data collected for industry {self.industry_id}")

    async def validate_data(self, data: Dict[str, Any]) -> bool:
        if not isinstance(data, dict):
            return False

        required_keys = {'raw_values', 'quality'}
        if not all(key in data for key in required_keys):
            return False

        if not isinstance(data['raw_values'], list):
            return False

        return True

    def _get_quality_values(self) -> Dict[str, float]:
        quality_values = {
            'blaine': 0,
            'fineness': 0
        }

        for topic, value in self.collected_data:
            if topic == self.config['quality_topics'].get('blaine'):
                quality_values['blaine'] = float(value)
            elif topic == self.config['quality_topics'].get('fineness'):
                quality_values['fineness'] = float(value)

        return quality_values
