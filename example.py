#!/usr/bin/env python3
"""
Example script demonstrating use of the indicatron module.
"""

import time
from indicatron import WLEDClient

# Connect to WLED via HTTP
client = WLEDClient.http("tofusaber-1.local")  # Replace with your WLED IP

print("Setting color to blue")
client.set_color("blue")
time.sleep(2)

print("Creating a progress bar")
for i in range(0, 101, 5):
    client.progress_bar(i, "green")
    time.sleep(0.1)
time.sleep(1)

print("Setting brightness to 50%")
client.set_brightness(128)
time.sleep(2)

client.clear()

print("Running advanced progress bar with effect")
client.advanced_progress_bar(75, "#ff9900", mode=2)
time.sleep(3)

print("Activating built-in effect")
client.effect(12, speed=150, intensity=200)  # Rainbow effect
time.sleep(3)

print("Getting system info")
info = client.get_info()
print(f"Temperature: {info.get('temperature', 'N/A')}")
print(f"WiFi signal: {info.get('wifi', {}).get('signal', 'N/A')}")

print("Turning off the strip")
client.clear()
