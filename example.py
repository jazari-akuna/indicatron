"""
Example usage of the Indicatron module.
"""
import time
from indicatron import WLEDClient

def run_example(client):
    print("Getting device info...")
    info = client.get_info()
    
    # Extract LED count from the correct path in the response
    if 'info' in info and 'leds' in info['info'] and 'count' in info['info']['leds']:
        led_count = info['info']['leds']['count']
    else:
        print("Could not determine LED count from info response")
        print(f"Info response structure: {info}")
        led_count = "unknown number of"
    
    print(f"Connected to WLED device with {led_count} LEDs")
    
    # Rest of the example remains unchanged...

    print("Clearing the strip...")
    client.clear()
    # Turn on the entire strip with a single color
    print("Setting full strip to green...")
    client.set_full_color("green")
    time.sleep(2)
    
    # Set progress from 0% to 30%
    print("Setting progress from 0% to 30% (blue)...")
    client.set_progress(0, 30, color="blue")
    time.sleep(2)
    
    # Add progress from 30% to 60%
    print("Adding 30% progress (red)...")
    client.add_progress(30, color="red") 
    time.sleep(1)
    
    # Add progress from 60% to 100%
    print("Adding 40% progress (purple)...")
    client.add_progress(40, color="purple")
    time.sleep(1)
    
    # Change direction and do it again
    print("Changing progress direction to right-to-left...")
    client.set_progress_direction(False)
    
    # Reset progress indicator
    print("Clearing the strip...")
    client.clear()
    time.sleep(1)
    
    # Set reverse progress from 0% to 30%
    print("Setting reverse progress from 0% to 30% (yellow)...")
    client.set_progress(0, 30, color="yellow")
    time.sleep(1)
    
    # Add reverse progress from 30% to 70%
    print("Adding 40% reverse progress (cyan)...")
    client.add_progress(40, color="cyan") 
    time.sleep(1)
    
    # Set specific percentage of strip active
    print("Setting 50% of LEDs active...")
    client.set_on_percentage(50, color="orange", background="black")
    time.sleep(2)
    
    # Turn on full strip and set an effect
    print("Setting full strip to white...")
    client.set_full_color("white")
    time.sleep(1)
    
    print("Running rainbow effect...")
    client.set_effect("rainbow", speed=200)
    time.sleep(3)
    
    # Clear everything in the end
    print("Clearing the strip...")
    client.clear()

if __name__ == "__main__":
    # Choose your connection method:
    
    # For HTTP connection:
    client = WLEDClient.http("tofusaber-1.local")
    
    # For Serial connection (uncomment to use):
    # client = WLEDClient.serial("/dev/ttyUSB0")
    
    try:
        run_example(client)
    finally:
        # Always close the connection when done
        client.close()
