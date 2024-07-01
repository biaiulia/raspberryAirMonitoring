import subprocess

# WiFi credentials
SSID = "your_wifi_ssid"
PASSWORD = "your_wifi_password"

def connect_to_wifi():
    try:
        subprocess.run(["nmcli", "d", "wifi", "connect", SSID, "password", PASSWORD], check=True)
        print('Connected to WiFi')
    except subprocess.CalledProcessError as e:
        print(f"Failed to connect to WiFi: {e}")

def disconnect_from_wifi():
    try:
        subprocess.run(["nmcli", "networking", "off"], check=True)
        print('Disconnected from WiFi')
        subprocess.run(["nmcli", "networking", "on"], check=True)  # Re-enable networking for future connections
    except subprocess.CalledProcessError as e:
        print(f"Failed to disconnect from WiFi: {e}")
