"""
Serial client implementation for WLED JSON API over Serial.
"""

import json
import time
import serial
from .colors import parse_color
from .exceptions import ConnectionError, CommandError


class SerialClient:
    """
    Client for controlling WLED devices using the Serial JSON API.
    """
    
    def __init__(self, port, baudrate=115200):
        """
        Initialize Serial client.
        
        Args:
            port (str): Serial port (e.g., '/dev/ttyUSB0', 'COM3')
            baudrate (int, optional): Baud rate. Defaults to 115200.
        """
        try:
            self.serial = serial.Serial(port, baudrate, timeout=2)
            # Give the connection a moment to stabilize
            time.sleep(0.5)
            
            # Clear any pending data
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            
            # Try to get info to verify connection
            self.get_info()
        except serial.SerialException as e:
            raise ConnectionError(f"Could not connect to WLED device at {port}: {e}")

    def _send_command(self, data):
        """Send a command to the WLED device over serial."""
        try:
            # Convert to JSON and add newline
            json_data = json.dumps(data) + "\n"
            self.serial.write(json_data.encode())
            
            # Wait for a response (WLED sends "OK" or error message)
            response = self.serial.readline().decode().strip()
            
            if not response.startswith("OK"):
                raise CommandError(f"Command failed: {response}")
            
            return True
        except serial.SerialException as e:
            raise CommandError(f"Serial communication error: {e}")

    def _get_data(self, command):
        """Get data from the WLED device over serial."""
        try:
            # Clear buffer
            self.serial.reset_input_buffer()
            
            # Send the info command
            self.serial.write((command + "\n").encode())
            
            # Read response (may be multiple lines for complex data)
            response = ""
            start_time = time.time()
            
            # Read with timeout
            while time.time() - start_time < 2:
                if self.serial.in_waiting:
                    line = self.serial.readline().decode()
                    response += line
                    
                    # Check if we've received complete JSON
                    try:
                        json.loads(response)
                        break
                    except json.JSONDecodeError:
                        # Not complete yet, continue reading
                        continue
                else:
                    time.sleep(0.1)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                raise CommandError(f"Invalid JSON response: {response}")
                
        except serial.SerialException as e:
            raise CommandError(f"Serial communication error: {e}")

    def set_color(self, color):
        """Set the entire strip to a single color."""
        rgb = parse_color(color)
        data = {"seg": [{"col": [rgb]}], "on": True}
        return self._send_command(data)

    def set_brightness(self, brightness):
        """Set the brightness of the LED strip."""
        if not 0 <= brightness <= 255:
            raise ValueError("Brightness must be between 0 and 255")
        
        data = {"bri": brightness, "on": True if brightness > 0 else False}
        return self._send_command(data)

    def progress_bar(self, progress, color, reverse=False):
        """Display a simple progress bar."""
        if not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 and 100")
        
        rgb = parse_color(color)
        
        # First get the strip info to determine LED count
        info = self.get_info()
        leds = info.get("leds", {}).get("count", 30)  # Default to 30 if count not found
        
        # Calculate how many LEDs to light up
        segments_on = int((progress / 100) * leds)
        
        if segments_on == 0 and progress > 0:
            segments_on = 1  # Show at least one LED for non-zero progress
        
        # We need to create a segment array with specific colors for each LED
        segment_data = []
        
        for i in range(leds):
            if (not reverse and i < segments_on) or (reverse and i >= leds - segments_on):
                segment_data.append(rgb)
            else:
                segment_data.append([0, 0, 0])  # Off
        
        # Send command to set the LEDs
        data = {
            "on": True,
            "seg": [{
                "i": segment_data
            }]
        }
        
        return self._send_command(data)

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
            # Create an array of LED colors
            segment_data = []
            
            for i in range(leds):
                if start_led <= i < end_led:
                    segment_data.append(rgb)
                else:
                    segment_data.append([0, 0, 0])  # Off
            
            data = {
                "on": True,
                "seg": [{
                    "i": segment_data
                }]
            }
        else:  # Mode 2 - "falling blocks" effect
            # For mode 2 over serial, we'll simulate the effect by using built-in effects
            data = {
                "on": True,
                "seg": [{
                    "fx": 20,  # Meteor effect
                    "sx": 200,  # Speed
                    "ix": end_led * 8,  # Size based on progress
                    "col": [rgb]
                }]
            }
        
        return self._send_command(data)

    def clear(self):
        """Turn off all LEDs and clear effects."""
        data = {"on": False}
        return self._send_command(data)

    def power(self, state=True):
        """Power the LED strip on or off."""
        data = {"on": state}
        return self._send_command(data)

    def effect(self, effect_id, speed=128, intensity=128):
        """Activate a built-in WLED effect."""
        data = {
            "seg": [{
                "fx": effect_id,
                "sx": speed,
                "ix": intensity
            }],
            "on": True
        }
        return self._send_command(data)

    def get_info(self):
        """Get system information from the WLED device."""
        # In serial mode, we need to send "info" command
        return self._get_data("info")
    
    def __del__(self):
        """Cleanup when the object is deleted."""
        if hasattr(self, 'serial') and self.serial.is_open:
            self.serial.close()
