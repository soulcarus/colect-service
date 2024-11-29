from opcua import Client
from typing import List, Any

class APODIClient:
    def __init__(self, server_link: str):
        self.client = Client(server_link)
        self._connected = False

    def connect(self) -> None:
        """Connect to the APODI OPC UA server."""
        if not self._connected:
            self.client.connect()
            self._connected = True

    def disconnect(self) -> None:
        """Disconnect from the APODI OPC UA server."""
        if self._connected:
            self.client.disconnect()
            self._connected = False

    def get_objects_node(self):
        """Get the objects node from the server."""
        return self.client.get_objects_node()

    def get_values(self, nodes: List) -> List[Any]:
        """Get values from multiple nodes."""
        return self.client.get_values(nodes)

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()