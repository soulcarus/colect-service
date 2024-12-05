from abc import ABC, abstractmethod

class AbstractClient(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def __enter__(self):
        pass

    @abstractmethod
    async def __exit__(self, exc_type, exc_val, exc_tb):
        pass
