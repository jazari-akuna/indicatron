"""
Client for communicating with WLED devices.
"""

from .http_client import HTTPClient
from .serial_client import SerialClient

class WLEDClient:
    """
    Client for communicating with WLED devices through either HTTP or Serial.
    """
    
    @classmethod
    def http(cls, host, port=80):
        """
        Create a new HTTP client.
        
        Args:
            host: The hostname or IP address of the WLED device
            port: The port number (default: 80)
        
        Returns:
            HTTPClient configured with the given host and port
        """
        return HTTPClient(host, port)
    
    @classmethod
    def serial(cls, port, baudrate=115200):
        """
        Create a new Serial client.
        
        Args:
            port: The serial port to use
            baudrate: The baudrate to use (default: 115200)
        
        Returns:
            SerialClient configured with the given port and baudrate
        """
        return SerialClient(port, baudrate)
