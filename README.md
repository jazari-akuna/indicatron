# Indicatron

A Python module for controlling WLED-powered LED strips via WLED's JSON API and serial connections.

## Installation

```bash
pip install indicatron
```

## Features

- Control WLED devices via HTTP or Serial connection
- Set colors, brightness, and effects
- Trigger built-in WLED effects with parameters
- Create progress bar visualizations
- Retrieve system information (temperature, WiFi details)
- Full support for segment control

## Usage

### HTTP Connection

```python
from indicatron import WLEDClient

# Connect to WLED device via HTTP
client = WLEDClient.http("192.168.1.100")  # Replace with your WLED IP address

# Turn on the LEDs
client.turn_on()

# Set color to red
client.set_color("red")

# Set a specific RGB color
client.set_color((255, 100, 0))

# Set brightness (0-255)
client.set_brightness(128)

# Set a built-in effect
client.set_effect("Rainbow")

# Get system information
info = client.get_info()
print(f"Temperature: {info.get('temperature')}°C")
print(f"WiFi strength: {info.get('wifi', {}).get('signal')}%")
```

### Serial Connection

```python
from indicatron import WLEDClient

# Connect to WLED device via Serial
client = WLEDClient.serial("/dev/ttyUSB0")  # Replace with your serial port

# Turn on the LEDs
client.turn_on()

# Set color to blue
client.set_color("blue")

# Don't forget to close the serial connection when done
client.close()
```

### Progress Bar Visualization

```python
from indicatron import WLEDClient
import time

client = WLEDClient.http("192.168.1.100")

# Create a progress bar effect (0-100%)
for i in range(101):
    client.set_progress(i, color="green", background="black")
    time.sleep(0.05)
```

### Advanced Features

```python
# Set advanced effect parameters
client.set_effect("Chase", speed=150, intensity=200)

# Create segments
client.set_segment(0, 0, 49, color="red")    # First 50 LEDs red
client.set_segment(1, 50, 99, color="green") # Next 50 LEDs green

# Set color temperature (0-255 or Kelvin value 1900-10091)
client.set_color_temperature(128)      # Mid-point (relative scale)
client.set_color_temperature(4500)     # 4500K (absolute scale)
```

## Available Colors

The following colors are available as string names:
- red, green, blue, yellow, cyan, magenta, white, black
- orange, purple, pink, brown, gray/grey, lime
- indigo, violet, gold, silver

You can also specify any color as an RGB tuple: (255, 0, 0)
