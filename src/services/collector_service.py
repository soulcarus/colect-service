import threading
import traceback
from time import sleep
import pendulum
from typing import Dict, Any
from strategies.abstract_collector import CollectorStrategy
from utils.logger import log

class CollectorService:
    """Service for managing data collection."""

    def __init__(self, strategy: CollectorStrategy, industry_id: str):
        self.strategy = strategy
        self.industry_id = industry_id
        self._running = False
        self._thread = None

    def start(self):
        """Start the collection service."""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._collection_loop)
            self._thread.daemon = True
            self._thread.start()

    def stop(self):
        """Stop the collection service."""
        self._running = False
        if self._thread:
            self._thread.join()

    def _collection_loop(self):
        """Main collection loop."""
        while self._running:
            try:
                self._collect_data()
                #sleep(30)  # Wait for 30 seconds before next collection
                # apply pendulum
            except Exception as e:
                log.error(f"Error in collection loop for industry {self.industry_id}: {str(e)}")
                log.error(traceback.format_exc())
                #sleep(5)  # Wait a bit before retrying
                # apply pendulum

    def _collect_data(self):
        """Collect and process data."""
        timestamp = pendulum.now()
        log.info(f"Starting collection for industry {self.industry_id}")
        
        try:
            data = self.strategy.collect_data()
            if data:
                self._process_data(data, timestamp)
            log.info(f"Collection finished for industry {self.industry_id}")
        except Exception as e:
            log.error(f"Collection failed for industry {self.industry_id}: {str(e)}")
            raise

    def _process_data(self, data: Dict[str, Any], timestamp: pendulum.DateTime):
        """Process collected data."""
        try:
            self.strategy.process_data(data, timestamp)
        except Exception as e:
            log.error(f"Data processing failed for industry {self.industry_id}: {str(e)}")
            raise