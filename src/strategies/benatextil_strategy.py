from typing import Dict, Any, List
from clients.benatextil_client import BenatextilClient
from utils.logger import log
import pendulum

from strategies.abstract_collector import CollectorStrategy

class BenatextilMqttStrategy(CollectorStrategy):
    """MQTT collection strategy implementation."""

    def __init__(self, client: BenatextilClient, industry_id: str, config: Dict[str, Any]):
        self.client = client
        self.industry_id = industry_id
        self.config = config
        self.collected_data = []

    def collect_data(self) -> Dict[str, Any]:
        """Collect data from Benatextil MQTT broker."""
        with self.client:
            self.collected_data = []
            
            # Subscribe to all configured topics
            for topic in self.config['topics']:
                self.client.subscribe(topic, self._handle_message)
            
            # Wait for data collection (configured timeout)
            #sleep(self.config.get('collection_timeout', 5))
            
            return {
                'raw_values': self.collected_data,
                'quality': self._get_quality_values()
            }

    def process_data(self, data: Dict[str, Any], timestamp: pendulum.DateTime):
        """Process and store the collected data."""
        from utils.mongodb import get_database
        
        if self.validate_data(data):
            db = get_database(self.industry_id)
            collection = db['collections']
            
            document = {
                'industry_id': self.industry_id,
                'timestamp': timestamp,
                'raw_values': data['raw_values'],
                'quality': data['quality']
            }
            
            collection.insert_one(document)
        else:
            log.error(f"Invalid data collected for industry {self.industry_id}")

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate the collected data."""
        if not isinstance(data, dict):
            return False
            
        required_keys = {'raw_values', 'quality'}
        if not all(key in data for key in required_keys):
            return False
            
        if not isinstance(data['raw_values'], list):
            return False
            
        return True

    def _handle_message(self, topic: str, payload: Any):
        """Handle incoming Benatextil MQTT messages."""
        self.collected_data.append((topic, payload))

    def _get_quality_values(self) -> Dict[str, float]:
        """Get quality values from collected data."""
        quality_values = {
            'blaine': 0,
            'fineness': 0
        }
        
        # Extract quality values from collected data based on configured topics
        for topic, value in self.collected_data:
            if topic == self.config['quality_topics'].get('blaine'):
                quality_values['blaine'] = float(value)
            elif topic == self.config['quality_topics'].get('fineness'):
                quality_values['fineness'] = float(value)
                
        return quality_values