# Indicatron

A Python module to control WLED-powered LED strips for visualizing process states and progress.

## Installation

```bash
pip install indicatron
```

## Usage
### Basic Usage

```python
from indicatron import WLEDClient

# Connect to a WLED device via HTTP
client = WLEDClient.http("192.168.1.100")

# Set the entire strip to green
client.set_color("green")

# Create a progress bar (50% complete, blue color)
client.progress_bar(50, "blue")

# Turn off the strip
client.clear()
```

### Serial Connection

```python
from indicatron import WLEDClient

# Connect to a WLED device via Serial
client = WLEDClient.serial("/dev/ttyUSB0", baudrate=115200)

# Set the strip to 75% brightness
client.set_brightness(75)

# Advanced progress bar with moving block effect
client.advanced_progress_bar(65, "#ff9900", mode=2)
```

## Features

* Set the entire strip to a single color
* Adjust brightness
* Simple progress bar mode
* Advanced progress bar with special effects
* Control WLED built-in lighting effects
* Monitor system information (temperature, WiFi details)
* Support for both HTTP and Serial connections
