"""
The main client interface for controlling WLED devices.
"""

from .http_client import HTTPClient
from .serial_client import SerialClient


class WLEDClient:
    """
    High-level client for controlling WLED devices.
    
    This class provides a unified interface for controlling WLED devices
    through either HTTP or Serial connections.
    """
    
    @classmethod
    def http(cls, host, port=80, use_ssl=False):
        """
        Create a new client using HTTP connection.
        
        Args:
            host (str): Hostname or IP address of the WLED device
            port (int, optional): Port number. Defaults to 80.
            use_ssl (bool, optional): Whether to use HTTPS. Defaults to False.
            
        Returns:
            WLEDClient: A configured client instance
        """
        client = cls()
        client._client = HTTPClient(host, port, use_ssl)
        return client
    
    @classmethod
    def serial(cls, port, baudrate=115200):
        """
        Create a new client using Serial connection.
        
        Args:
            port (str): Serial port (e.g., '/dev/ttyUSB0', 'COM3')
            baudrate (int, optional): Baud rate. Defaults to 115200.
            
        Returns:
            WLEDClient: A configured client instance
        """
        client = cls()
        client._client = SerialClient(port, baudrate)
        return client
    
    def set_color(self, color):
        """
        Set the entire strip to a single color.
        
        Args:
            color (str or tuple): Color name, hex code, or RGB tuple
        """
        return self._client.set_color(color)
    
    def set_brightness(self, brightness):
        """
        Set the brightness of the LED strip.
        
        Args:
            brightness (int): Brightness level (0-255)
        """
        return self._client.set_brightness(brightness)
    
    def progress_bar(self, progress, color, reverse=False):
        """
        Display a progress bar on the LED strip.
        
        Args:
            progress (float): Progress value from 0.0 to 100.0
            color (str or tuple): Color name, hex code, or RGB tuple
            reverse (bool, optional): Reverse the direction. Defaults to False.
        """
        return self._client.progress_bar(progress, color, reverse)
    
    def advanced_progress_bar(self, progress, color, start_pct=0, mode=1):
        """
        Display an advanced progress bar with effects.
        
        Args:
            progress (float): Progress value from 0.0 to 100.0
            color (str or tuple): Color name, hex code, or RGB tuple
            start_pct (float, optional): Starting percentage. Defaults to 0.
            mode (int, optional): Effect mode (1: simple, 2: falling effect). Defaults to 1.
        """
        return self._client.advanced_progress_bar(progress, color, start_pct, mode)
    
    def clear(self):
        """Turn off all LEDs and clear any effects."""
        return self._client.clear()
    
    def power(self, state=True):
        """
        Power the LED strip on or off.
        
        Args:
            state (bool, optional): True for on, False for off. Defaults to True.
        """
        return self._client.power(state)
    
    def effect(self, effect_id, speed=128, intensity=128):
        """
        Activate a built-in WLED effect.
        
        Args:
            effect_id (int): Effect ID number
            speed (int, optional): Effect speed (0-255). Defaults to 128.
            intensity (int, optional): Effect intensity (0-255). Defaults to 128.
        """
        return self._client.effect(effect_id, speed, intensity)
    
    def get_info(self):
        """
        Get system information from the WLED device.
        
        Returns:
            dict: System information including temperature and WiFi details
        """
        return self._client.get_info()
