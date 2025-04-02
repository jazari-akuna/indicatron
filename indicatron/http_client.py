"""
HTTP client implementation for WLED JSON API.
"""

import json
import requests
from .colors import parse_color
from .exceptions import ConnectionError, CommandError


class HTTPClient:
    """
    Client for controlling WLED devices using the HTTP JSON API.
    """
    
    def __init__(self, host, port=80, use_ssl=False):
        """
        Initialize HTTP client.
        
        Args:
            host (str): Hostname or IP address of the WLED device
            port (int, optional): Port number. Defaults to 80.
            use_ssl (bool, optional): Whether to use HTTPS. Defaults to False.
        """
        protocol = "https" if use_ssl else "http"
        self.base_url = f"{protocol}://{host}:{port}/json"
        self.session = requests.Session()
        
        # Test the connection
        try:
            self.get_info()
        except requests.RequestException as e:
            raise ConnectionError(f"Could not connect to WLED device at {self.base_url}: {e}")

    def _send_command(self, endpoint, data):
        """Send a command to the WLED device."""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json() if response.text.strip() else {}
        except requests.RequestException as e:
            raise CommandError(f"Command failed: {e}")

    def _get_data(self, endpoint):
        """Get data from the WLED device."""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise CommandError(f"Data retrieval failed: {e}")

    def set_color(self, color):
        """Set the entire strip to a single color."""
        rgb = parse_color(color)
        data = {
            "seg": [
                {"col": [rgb, [0, 0, 0], [0, 0, 0]], "fx": 0, "sx": 128, "ix": 128}
            ],
            "on": True
        }
        return self._send_command("state", data)

    def set_brightness(self, brightness):
        """Set the brightness of the LED strip."""
        if not 0 <= brightness <= 255:
            raise ValueError("Brightness must be between 0 and 255")
        
        data = {"bri": brightness, "on": True if brightness > 0 else False}
        return self._send_command("state", data)

    def progress_bar(self, progress, color, reverse=False):
        """Display a simple progress bar."""
        if not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 and 100")
        
        rgb = parse_color(color)
        
        # We'll use a segment to create the progress bar
        data = {"on": True, "bri": 255}
        
        # Get the current strip info to determine LED count
        info = self.get_info()
        leds = info.get("leds", {}).get("count", 30)  # Default to 30 if count not found
        
        # Calculate how many LEDs to light up
        segments_on = int((progress / 100) * leds)
        
        if segments_on == 0 and progress > 0:
            segments_on = 1  # Show at least one LED for non-zero progress
        
        # Create a segment effect
        if reverse:
            # Start from the end, we need to adjust the stop position
            stop = leds
            start = leds - segments_on
        else:
            # Start from the beginning
            start = 0
            stop = segments_on
        
        data["seg"] = [
            {
                "id": 0,
                "start": start,
                "stop": stop,
                "col": [rgb, [0, 0, 0], [0, 0, 0]],
                "fx": 0,  # Solid color effect
                "sx": 128,
                "ix": 128,
                "on": True
            }
        ]
        
        if segments_on < leds:
            # Add a second segment for the "off" part
            off_seg = {
                "id": 1,
                "start": stop,
                "stop": leds if not reverse else start,
                "col": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],  # All off
                "fx": 0,
                "on": True
            }
            data["seg"].append(off_seg)
        
        return self._send_command("state", data)

    def advanced_progress_bar(self, progress, color, start_pct=0, mode=1):
        """Display an advanced progress bar with effects."""
        if not 0 <= progress <= 100 or not 0 <= start_pct <= 100:
            raise ValueError("Progress and start_pct must be between 0 and 100")
        
        if not 1 <= mode <= 2:
            raise ValueError("Mode must be 1 or 2")
        
        rgb = parse_color(color)
        
        # Get the current strip info to determine LED count
        info = self.get_info()
        leds = info.get("leds", {}).get("count", 30)  # Default to 30 if count not found
        
        # Calculate LED positions
        start_led = int((start_pct / 100) * leds)
        end_led = int((progress / 100) * leds)
        
        if mode == 1:  # Simple mode - just light up the segment
            data = {
                "on": True,
                "bri": 255,
                "seg": [
                    {
                        "id": 0,
                        "start": 0,
                        "stop": start_led,
                        "col": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                        "fx": 0,
                        "on": True
                    },
                    {
                        "id": 1,
                        "start": start_led,
                        "stop": end_led,
                        "col": [rgb, [0, 0, 0], [0, 0, 0]],
                        "fx": 0,
                        "on": True
                    },
                    {
                        "id": 2,
                        "start": end_led,
                        "stop": leds,
                        "col": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                        "fx": 0,
                        "on": True
                    }
                ]
            }
        else:  # Mode 2 - "falling blocks" effect
            # For mode 2, we'll use the "Meteor" effect with custom settings
            data = {
                "on": True,
                "bri": 255,
                "seg": [
                    {
                        "id": 0,
                        "start": 0,
                        "stop": leds,
                        "col": [rgb, [0, 0, 0], [0, 0, 0]],
                        "fx": 20,  # Meteor effect
                        "sx": 200,  # Speed - faster
                        "ix": end_led * 8,  # Size of the meteor based on progress
                        "pal": 0,
                        "on": True
                    }
                ]
            }
        
        return self._send_command("state", data)

    def clear(self):
        """Turn off all LEDs and clear effects."""
        data = {"on": False}
        return self._send_command("state", data)

    def power(self, state=True):
        """Power the LED strip on or off."""
        data = {"on": state}
        return self._send_command("state", data)

    def effect(self, effect_id, speed=128, intensity=128):
        """Activate a built-in WLED effect."""
        data = {
            "seg": [
                {
                    "fx": effect_id,
                    "sx": speed,
                    "ix": intensity
                }
            ],
            "on": True
        }
        return self._send_command("state", data)

    def get_info(self):
        """Get system information from the WLED device."""
        return self._get_data("")  # Root endpoint returns full info
