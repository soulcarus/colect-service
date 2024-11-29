from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pendulum

class CollectorStrategy(ABC):
    """Abstract base class for collection strategies."""

    @abstractmethod
    def collect_data(self) -> Dict[str, Any]:
        """Collect data using the specific strategy."""
        pass

    @abstractmethod
    def process_data(self, data: Dict[str, Any], timestamp: pendulum.DateTime):
        """Process the collected data."""
        pass

    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate the collected data."""
        pass
