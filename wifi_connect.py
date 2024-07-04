import subprocess
from dotenv import load_dotenv
import os

load_dotenv()

SSID = os.getenv('WIFI_SSID')
PASSWORD = os.getenv('WIFI_PASSWORD')

def is_wifi_connected():
    result = subprocess.run(["nmcli", "-t", "-f", "DEVICE,STATE", "d"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if 'connected' in line:
            return True
    return False

def connect_to_wifi():
    if not is_wifi_connected():
        try:
            subprocess.run(["nmcli", "d", "wifi", "connect", SSID, "password", PASSWORD], check=True)
            print('Connected to WiFi')
        except subprocess.CalledProcessError as e:
            print(f"Failed to connect to WiFi: {e}")
    else:
        print("Already connected to WiFi")

def disconnect_from_wifi():
    if is_wifi_connected():
        try:
            subprocess.run(["nmcli", "networking", "off"], check=True)
            print('Disconnected from WiFi')
            subprocess.run(["nmcli", "networking", "on"], check=True)  # Re-enable networking for future connections
        except subprocess.CalledProcessError as e:
            print(f"Failed to disconnect from WiFi: {e}")
    else:
        print("Not connected to any WiFi")
