"""
Client for communicating with WLED devices.
"""
import json
import requests
import serial
import time
from .colors import COLOR_MAP, WLED_EFFECTS, WLED_PALETTES
from .exceptions import WLEDConnectionError, WLEDResponseError
from .utils import resolve_color, validate_brightness

class WLEDClient:
    """
    Client for communicating with WLED devices using either HTTP or Serial.
    """
    
    @classmethod
    def http(cls, host, port=80):
        """
        Create a new client that connects via HTTP.
        
        Args:
            host: The hostname or IP address of the WLED device
            port: The port number (default: 80)
        
        Returns:
            WLEDClient configured to use HTTP transport
        """
        return cls(transport='http', host=host, port=port)
    
    @classmethod
    def serial(cls, port, baudrate=115200):
        """
        Create a new client that connects via Serial.
        
        Args:
            port: The serial port to use
            baudrate: The baudrate to use (default: 115200)
        
        Returns:
            WLEDClient configured to use Serial transport
        """
        return cls(transport='serial', port=port, baudrate=baudrate)
    
    def __init__(self, transport, **kwargs):
        """
        Initialize a new WLEDClient.
        
        Args:
            transport: The transport method ('http' or 'serial')
            **kwargs: Transport-specific arguments
        """
        self.transport = transport
        self.led_count = 30  # Default LED count
        self.current_progress = 0  # Track current progress percentage
        self.progress_direction = True  # True = progress from start to end, False = reverse
        
        if transport == 'http':
            self.host = kwargs.get('host')
            self.port = kwargs.get('port', 80)
            self.api_url = f"http://{self.host}:{self.port}/json"
            self.serial = None
        elif transport == 'serial':
            self.serial_port = kwargs.get('port')
            self.baudrate = kwargs.get('baudrate', 115200)
            self.serial = serial.Serial(self.serial_port, self.baudrate, timeout=2)
            self.host = None
            self.port = None
        else:
            raise ValueError(f"Invalid transport method: {transport}")
        
        # Get initial LED count
        self._fetch_led_count()
    
    def _fetch_led_count(self):
        """
        Fetch the number of LEDs from the device info.
        """
        try:
            info = self.get_info()
            if 'leds' in info and 'count' in info['leds']:
                self.led_count = info['leds']['count']
        except Exception:
            # If there's any error, keep the default LED count
            pass
    
    def _send_command(self, data):
        """
        Send a command to the WLED device.
        
        Args:
            data: The command data to send
        
        Returns:
            Response from the device
        """
        if self.transport == 'http':
            try:
                response = requests.post(self.api_url, json=data)
                response.raise_for_status()
                return response.json() if response.text else {}
            except requests.RequestException as e:
                raise WLEDConnectionError(f"Error communicating with WLED device: {e}")
        else:  # serial
            if not self.serial or not self.serial.is_open:
                raise WLEDConnectionError("Serial connection is not open")
            
            # Convert to JSON string and add newline
            command = json.dumps(data) + "\n"
            
            try:
                self.serial.write(command.encode('utf-8'))
                # Read response until timeout or until a complete JSON is received
                response = self.serial.readline().decode('utf-8').strip()
                if response:
                    try:
                        return json.loads(response)
                    except json.JSONDecodeError as e:
                        raise WLEDResponseError(f"Invalid JSON response: {e}")
                return {}
            except serial.SerialException as e:
                raise WLEDConnectionError(f"Serial communication error: {e}")
    
    def get_info(self):
        """
        Get information about the WLED device.
        
        Returns:
            Dict containing device information
        """
        if self.transport == "http":
            # For HTTP, make a direct request to the info endpoint
            url = f"http://{self.host}:{self.port}/json/info"
            response = requests.get(url).json()
        else:
            # For serial, use the existing _send_command with the appropriate command
            response = self._send_command({"get": "info"})
        
        # Store LED count for reuse by other methods
        if 'info' in response and 'leds' in response['info'] and 'count' in response['info']['leds']:
            self.led_count = response['info']['leds']['count']
        
        return response


    
    def get_state(self):
        """
        Get the current state of the WLED device.
        
        Returns:
            Dict containing current device state
        """
        return self._send_command({"v": True})
    
    def turn_on(self):
        """
        Turn on the WLED device.
        
        Returns:
            Response from the device
        """
        data = {"on": True}
        return self._send_command(data)
    
    def turn_off(self):
        """
        Turn off the WLED device.
        
        Returns:
            Response from the device
        """
        data = {"on": False}
        return self._send_command(data)
    
    def set_brightness(self, brightness):
        """
        Set the brightness of the WLED device.
        
        Args:
            brightness: Brightness value (0-255) or percentage string (e.g. "50%")
        
        Returns:
            Response from the device
        """
        brightness_value = validate_brightness(brightness)
        data = {"bri": brightness_value}
        return self._send_command(data)
    
    def set_color(self, color):
        """
        Set the color of the WLED device.
        
        Args:
            color: Color name or RGB tuple
        
        Returns:
            Response from the device
        """
        rgb = resolve_color(color)
        data = {
            "seg": [{
                "col": [rgb]
            }]
        }
        return self._send_command(data)
    
    def set_effect(self, effect, speed=128, intensity=128, palette=None):
        """
        Set an effect on the WLED device.
        
        Args:
            effect: Effect name or ID
            speed: Effect speed (0-255)
            intensity: Effect intensity (0-255)
            palette: Optional palette name or ID
        
        Returns:
            Response from the device
        """
        # Resolve effect name or ID
        effect_id = effect
        if isinstance(effect, str):
            effect_id = next((idx for idx, name in enumerate(WLED_EFFECTS) if name.lower() == effect.lower()), effect)
        
        # Resolve palette name or ID if provided
        palette_id = palette
        if palette and isinstance(palette, str):
            palette_id = next((idx for idx, name in enumerate(WLED_PALETTES) if name.lower() == palette.lower()), palette)
        
        data = {
            "seg": [{
                "fx": effect_id,
                "sx": speed,
                "ix": intensity
            }]
        }
        
        if palette_id is not None:
            data["seg"][0]["pal"] = palette_id
        
        return self._send_command(data)
    
    def set_temperature(self, temperature):
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
    
    def set_on_percentage(self, percentage, color=None, background=None):
        """
        Set a percentage of the strip to be on.
        
        Args:
            percentage: Percentage of the strip to turn on (0-100)
            color: Color for the active portion (default: current color)
            background: Background color for inactive portion (default: off/black)
        
        Returns:
            Response from the device
        """
        percentage = max(0, min(100, percentage))
        self.current_progress = percentage
        
        active_leds = int(self.led_count * percentage / 100)
        
        # All LEDs are off
        if percentage == 0:
            return self.turn_off()
        
        # Define colors
        fg_color = resolve_color(color) if color else [255, 255, 255]  # Default to white if no color given
        bg_color = resolve_color(background) if background else [0, 0, 0]  # Default to black if no background given
        
        # Create a segment definition with the correct ranges
        if self.progress_direction:
            # Regular direction (left to right)
            data = {
                "on": True,
                "bri": 255,
                "seg": [{
                    "id": 0,
                    "start": 0,
                    "stop": active_leds,
                    "col": [fg_color],
                    "fx": 0
                }, {
                    "id": 1,
                    "start": active_leds,
                    "stop": self.led_count,
                    "col": [bg_color],
                    "fx": 0
                }]
            }
        else:
            # Reversed direction (right to left)
            inactive_leds = self.led_count - active_leds
            data = {
                "on": True,
                "bri": 255,
                "seg": [{
                    "id": 0,
                    "start": 0,
                    "stop": inactive_leds,
                    "col": [bg_color],
                    "fx": 0
                }, {
                    "id": 1,
                    "start": inactive_leds,
                    "stop": self.led_count,
                    "col": [fg_color],
                    "fx": 0
                }]
            }
        
        return self._send_command(data)

    
    def set_full_color(self, color):
        """
        Set the entire strip to a single color.
        
        Args:
            color: Color name or RGB tuple
        
        Returns:
            Response from the device
        """
        # First ensure 100% of the strip is active
        self.set_on_percentage(100)
        # Then set the color
        return self.set_color(color)
    
    def clear(self):
        """
        Clear the entire strip by turning it off.
        
        Returns:
            Response from the device
        """
        # Set 100% of the strip to be active, then turn it off
        self.set_on_percentage(100)
        return self.turn_off()
    
    def set_progress(self, start_percentage, end_percentage, color):
        """
        Set a progress bar between start and end percentages with the specified color.
        
        Args:
            start_percentage: Starting position as percentage (0-100)
            end_percentage: Ending position as percentage (0-100)
            color: Color for the progress segment
        
        Returns:
            Response from the device
        """
        start_percentage = max(0, min(100, start_percentage))
        end_percentage = max(0, min(100, end_percentage))
        
        # Ensure start is less than end
        if start_percentage > end_percentage:
            start_percentage, end_percentage = end_percentage, start_percentage
        
        self.current_progress = end_percentage
        
        # Calculate LED positions
        start_led = int(self.led_count * start_percentage / 100)
        end_led = int(self.led_count * end_percentage / 100)
        
        fg_color = resolve_color(color)
        bg_color = [0, 0, 0]  # Default background color is black/off
        
        # Create a segment definition with the correct ranges
        if self.progress_direction:
            # Regular direction (left to right)
            data = {
                "on": True,
                "bri": 255,
                "seg": [
                    {
                        "id": 0,
                        "start": 0,
                        "stop": start_led,
                        "col": [bg_color],
                        "fx": 0
                    },
                    {
                        "id": 1,
                        "start": start_led,
                        "stop": end_led,
                        "col": [fg_color],
                        "fx": 0
                    },
                    {
                        "id": 2,
                        "start": end_led,
                        "stop": self.led_count,
                        "col": [bg_color],
                        "fx": 0
                    }
                ]
            }
        else:
            # Reversed direction (right to left)
            inverse_start_led = self.led_count - end_led
            inverse_end_led = self.led_count - start_led
            
            data = {
                "on": True,
                "bri": 255,
                "seg": [
                    {
                        "id": 0,
                        "start": 0,
                        "stop": inverse_start_led,
                        "col": [bg_color],
                        "fx": 0
                    },
                    {
                        "id": 1,
                        "start": inverse_start_led,
                        "stop": inverse_end_led,
                        "col": [fg_color],
                        "fx": 0
                    },
                    {
                        "id": 2,
                        "start": inverse_end_led,
                        "stop": self.led_count,
                        "col": [bg_color],
                        "fx": 0
                    }
                ]
            }
        
        return self._send_command(data)
    
    def add_progress(self, percentage_to_add, color):
        """
        Add to the current progress with the specified color.
        
        Args:
            percentage_to_add: Percentage to add to current progress (can be negative)
            color: Color for the added progress segment
        
        Returns:
            Response from the device
        """
        start_percentage = self.current_progress
        end_percentage = start_percentage + percentage_to_add
        end_percentage = max(0, min(100, end_percentage))
        
        return self.set_progress(start_percentage, end_percentage, color)
    
    def set_progress_direction(self, direction=True):
        """
        Set the direction for progress display.
        
        Args:
            direction: True for left-to-right, False for right-to-left
        """
        self.progress_direction = bool(direction)
    
    def close(self):
        """
        Close the serial connection if using serial transport.
        """
        if self.serial and self.serial.is_open:
            self.serial.close()
