from datetime import datetime
import asyncio
import traceback
from typing import Dict, Any
import pendulum
from strategies.abstract_collector import CollectorStrategy
from utils.logger import log

class CollectorService:
    """Service for managing data collection."""

    def __init__(self, strategy: CollectorStrategy, industry_id: str):
        self.strategy = strategy
        self.industry_id = industry_id
        self._running = False
        self._task = None

    async def start(self):
        """Start the collection service."""
        if not self._running:
            self._running = True
            if self._task is None:
                self._task = asyncio.create_task(self.execution_loop())

    async def stop(self):
        """Stop the collection service."""
        if self._running:
            self._running = False
            if self._task:
                await self._task
                self._task = None

    async def stopwatch(self, interval_seconds: int) -> int:
        """Calculate the time remaining until the next execution."""
        current_time = pendulum.now().second
        seconds_to_next = interval_seconds - (current_time % interval_seconds)
        return seconds_to_next if seconds_to_next > 0 else 0

    async def execution_loop(self):
        """Core loop for triggering actions every 30 seconds."""
        while self._running:
            wait_time = await self.stopwatch(30)

            if wait_time > 0:
                await asyncio.sleep(wait_time)

            try:
                current_time = pendulum.now().replace(microsecond=0)  # Ignore milliseconds
                formatted_time = f"{current_time.hour:02}:{current_time.minute:02}:{current_time.second:02}"
                log.info(f"Triggered action at: {formatted_time}")
                try:
                    await self._collect_data()
                except Exception as e:
                    log.error(f"Error during scheduled data collection: {str(e)}")
                    log.error(traceback.format_exc())
            except Exception as e:
                log.error(f"Error in stopwatch: {str(e)}")
                log.error(traceback.format_exc())

    async def _collect_data(self):
        """Collect and process data."""
        timestamp = pendulum.now().replace(microsecond=0)  # Ignore milliseconds
        log.info(f"Starting collection for industry {self.industry_id} at {timestamp}")

        try:
            data = await self.strategy.collect_data()
            if data:
                await self._process_data(data, timestamp)
            log.info(f"Collection finished for industry {self.industry_id}")
        except Exception as e:
            log.error(f"Collection failed for industry {self.industry_id}: {str(e)}")
            log.error(traceback.format_exc())
            raise

    async def _process_data(self, data: Dict[str, Any], timestamp: pendulum.DateTime):
        """Process collected data."""
        try:
            await self.strategy.process_data(data, timestamp)
        except Exception as e:
            log.error(f"Data processing failed for industry {self.industry_id}: {str(e)}")
            log.error(traceback.format_exc())
            raise
