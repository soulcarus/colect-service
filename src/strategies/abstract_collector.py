from abc import ABC, abstractmethod
from typing import Dict, Any
import pendulum

class AbstractStrategy(ABC):
    """Abstract base class for collection strategies."""

    @abstractmethod
    async def collect_data(self) -> Dict[str, Any]:
        """Collect data using the specific strategy."""
        pass

    @abstractmethod
    async def process_data(self, data: Dict[str, Any], timestamp: pendulum.DateTime):
        """Process the collected data."""
        pass

    @abstractmethod
    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate the collected data."""
        pass