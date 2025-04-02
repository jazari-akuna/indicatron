"""
HTTP client for communicating with WLED devices.
"""
import json
import requests
from .colors import COLOR_MAP, WLED_EFFECTS, WLED_PALETTES
from .exceptions import WLEDConnectionError, WLEDResponseError
from .utils import resolve_color, validate_brightness

class HTTPClient:
    """
    Client for communicating with WLED devices using HTTP.
    """
    
    def __init__(self, host, port=80):
        """
        Initialize a new HTTPClient.
        
        Args:
            host: The hostname or IP address of the WLED device
            port: The port number (default: 80)
        """
        self.host = host
        self.port = port
        self.api_url = f"http://{host}:{port}/json"
        self.led_count = None
        # Get initial LED count
        self._fetch_led_count()
    
    def _fetch_led_count(self):
        """
        Fetch the number of LEDs from the device.
        """
        try:
            info = self.get_info()
            self.led_count = info.get('leds', {}).get('count', 0)
        except Exception:
            # Default to 30 if unable to fetch
            self.led_count = 30
    
    def _send_command(self, data, endpoint="state"):
        """
        Send a command to the WLED device.
        
        Args:
            data: The data to send
            endpoint: The API endpoint ('state' or 'info')
            
        Returns:
            Response from the device
            
        Raises:
            WLEDConnectionError: If there's an error connecting to the device
            WLEDResponseError: If there's an error in the response from the device
        """
        url = f"{self.api_url}/{endpoint}"
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            raise WLEDConnectionError(f"Error connecting to WLED device at {url}: {e}")
        except json.JSONDecodeError as e:
            raise WLEDResponseError(f"Error decoding response from WLED device: {e}")
    
    def get_state(self):
        """
        Get the current state of the WLED device.
        
        Returns:
            Current state of the device
        """
        try:
            return requests.get(f"{self.api_url}/state").json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            raise WLEDConnectionError(f"Error getting WLED state: {e}")
    
    def get_info(self):
        """
        Get information about the WLED device.
        
        Returns:
            Information about the device
        """
        try:
            response = requests.get(f"{self.api_url}/info")
            info = response.json()
            # Update LED count
            self.led_count = info.get('leds', {}).get('count', self.led_count)
            return info
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            raise WLEDConnectionError(f"Error getting WLED info: {e}")
    
    def turn_on(self):
        """
        Turn the WLED device on.
        
        Returns:
            Response from the device
        """
        return self._send_command({"on": True})
    
    def turn_off(self):
        """
        Turn the WLED device off.
        
        Returns:
            Response from the device
        """
        return self._send_command({"on": False})
    
    def toggle(self):
        """
        Toggle the WLED device on/off.
        
        Returns:
            Response from the device
        """
        return self._send_command({"T": 1})
    
    def set_brightness(self, brightness):
        """
        Set the brightness of the WLED device.
        
        Args:
            brightness: The brightness to set (0-255)
            
        Returns:
            Response from the device
        """
        brightness = validate_brightness(brightness)
        return self._send_command({"bri": brightness})
    
    def set_color(self, color):
        """
        Set the color of the WLED device.
        
        Args:
            color: The color to set (name or RGB tuple)
            
        Returns:
            Response from the device
        """
        rgb = resolve_color(color)
        return self._send_command({"seg": [{"col": [rgb]}]})
    
    def set_effect(self, effect_name, speed=128, intensity=128, palette=None):
        """
        Set the effect of the WLED device.
        
        Args:
            effect_name: The name of the effect
            speed: The speed of the effect (0-255, default 128)
            intensity: The intensity of the effect (0-255, default 128)
            palette: The palette to use (name)
            
        Returns:
            Response from the device
        """
        if effect_name.isdigit():
            effect_id = int(effect_name)
        else:
            effect_name = effect_name.lower()
            if effect_name not in WLED_EFFECTS:
                raise ValueError(f"Unknown effect: {effect_name}")
            effect_id = WLED_EFFECTS[effect_name]
        
        data = {
            "seg": [{
                "fx": effect_id,
                "sx": speed,
                "ix": intensity
            }]
        }
        
        if palette:
            if palette.isdigit():
                palette_id = int(palette)
            else:
                palette = palette.lower()
                if palette not in WLED_PALETTES:
                    raise ValueError(f"Unknown palette: {palette}")
                palette_id = WLED_PALETTES[palette]
            
            data["seg"][0]["pal"] = palette_id
        
        return self._send_command(data)
    
    def show_progress(self, percentage, color="red", background="black"):
        """
        Show a progress bar effect using LEDs.
        
        Args:
            percentage: The percentage to show (0-100)
            color: The color of the progress bar
            background: The background color
            
        Returns:
            Response from the device
        """
        if not self.led_count:
            self._fetch_led_count()
        
        percentage = max(0, min(100, percentage))
        active_leds = int(self.led_count * percentage / 100)
        
        # Create a segment for the entire strip with background color
        fg_color = resolve_color(color)
        bg_color = resolve_color(background)
        
        # If percentage is 0, all background
        if percentage == 0:
            return self._send_command({
                "seg": [{
                    "id": 0,
                    "start": 0,
                    "stop": self.led_count,
                    "col": [bg_color],
                    "fx": 0  # Static effect
                }]
            })
        
        # If percentage is 100, all foreground
        if percentage == 100:
            return self._send_command({
                "seg": [{
                    "id": 0,
                    "start": 0,
                    "stop": self.led_count,
                    "col": [fg_color],
                    "fx": 0  # Static effect
                }]
            })
        
        # Otherwise split into two segments
        return self._send_command({
            "seg": [
                {
                    "id": 0,
                    "start": 0,
                    "stop": active_leds,
                    "col": [fg_color],
                    "fx": 0  # Static effect
                },
                {
                    "id": 1,
                    "start": active_leds,
                    "stop": self.led_count,
                    "col": [bg_color],
                    "fx": 0  # Static effect
                }
            ]
        })
    
    def set_color_temperature(self, temperature):
        """
        Set the color temperature of the WLED device.
        
        Args:
            temperature: Either a relative value (0-255) where 0 is warmest and 255 is coldest,
                        or an absolute Kelvin value (1900-10091)
        
        Returns:
            Response from the device
        """
        # Ensure temperature is within valid range
        if temperature <= 255:
            # Relative value
            temperature = max(0, min(255, temperature))
        else:
            # Kelvin value
            temperature = max(1900, min(10091, temperature))
        
        data = {
            "seg": [{
                "cct": temperature
            }]
        }
        return self._send_command(data)
