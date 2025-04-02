#!/usr/bin/env python3
"""
Example script demonstrating the Indicatron module.
"""

import time
from indicatron import WLEDClient

# Example with HTTP connection
def http_example():
    # Replace with your WLED device's IP address
    client = WLEDClient.http("tofusaber-1.local")

    print("Turning on...")
    client.turn_on()
    time.sleep(1)
    print(client.get_info())
    print("Setting to red...")
    client.set_color("red")
    time.sleep(1)
    
    print("Setting to green...")
    client.set_color("green")
    time.sleep(1)
    
    print("Setting to blue...")
    client.set_color("blue")
    time.sleep(1)
    
    print("Setting brightness to 50%...")
    client.set_brightness(128)  # 0-255 scale
    time.sleep(1)
    
    print("Running rainbow effect...")
    client.set_effect("rainbow", speed=200)
    time.sleep(3)
    
    print("Showing progress bar (50%)...")
    client.show_progress(50, color="blue", background="black")
    time.sleep(2)
    
    print("Turning off...")
    client.turn_off()

# Example with Serial connection
def serial_example():
    # Replace with your WLED device's serial port
    client = WLEDClient.serial("/dev/ttyUSB0")
    
    print("Turning on...")
    client.turn_on()
    time.sleep(1)
    
    print("Setting to red...")
    client.set_color("red")
    time.sleep(1)
    
    print("Setting to blue...")
    client.set_color("blue")
    time.sleep(1)
    
    print("Running rainbow effect...")
    client.set_effect("rainbow")
    time.sleep(3)
    
    print("Turning off...")
    client.turn_off()
    
    # Make sure to close the serial connection
    client.close()

if __name__ == "__main__":
    # Uncomment the example you want to run:
    http_example()
    # serial_example()
