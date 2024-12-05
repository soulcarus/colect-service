from abc import ABC, abstractmethod
from clients.abstract_client import AbstractClient
from strategies.abstract_collector import AbstractStrategy

class IndustryFactory(ABC):
    """Abstract factory for creating collector components."""
    
    @abstractmethod
    def create_client(self) -> AbstractClient:
        """Create a client instance."""
        pass

    @abstractmethod
    def create_strategy(self) -> AbstractStrategy:
        """Create a collection strategy instance."""
        pass
