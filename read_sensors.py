import time
import sqlite3
import board
import serial  
import adafruit_dht
from datetime import datetime
from wifi_connect import connect_to_wifi, disconnect_from_wifi
from mqtt_client import publish_message  # Ensure mqtt_client.py is in the same directory

# Configuration
DHT_PIN = board.D4
UART_PORT = '/dev/ttyUSB0'
UART_BAUDRATE = 9600
READ_INTERVAL = 30  # seconds
MAX_RETRIES = 3  # Number of retries for sensor reading

# Initialize SQLite
conn = sqlite3.connect('sensor_data.db')

# Initialize Sensors
dhtDevice = adafruit_dht.DHT22(DHT_PIN)
ser = serial.Serial(UART_PORT, baudrate=UART_BAUDRATE, timeout=1)

# AQI Levels
AQI_LEVELS = ["Good", "Fair", "Moderate", "Poor", "Very Poor"]

def calculate_aqi(pm2_5, pm10):
    if pm2_5 is None or pm10 is None:
        return None
    
    if pm2_5 <= 25:
        aqi_pm25 = "Good"
    elif pm2_5 <= 50:
        aqi_pm25 = "Fair"
    elif pm2_5 <= 90:
        aqi_pm25 = "Moderate"
    elif pm2_5 <= 180:
        aqi_pm25 = "Poor"
    else:
        aqi_pm25 = "Very Poor"
    
    if pm10 <= 50:
        aqi_pm10 = "Good"
    elif pm10 <= 100:
        aqi_pm10 = "Fair"
    elif pm10 <= 250:
        aqi_pm10 = "Moderate"
    elif pm10 <= 350:
        aqi_pm10 = "Poor"
    else:
        aqi_pm10 = "Very Poor"
    
    aqi = max(aqi_pm25, aqi_pm10, key=lambda x: AQI_LEVELS.index(x))
    return aqi

def insert_into_db(temperature, humidity, pm2_5, pm10, aqi):
    day = datetime.now().strftime("%A")
    with conn:
        conn.execute('''INSERT INTO sensor_readings
                        (timestamp, day, temperature, humidity, pm25, pm10, aqi)
                        VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?)''', 
                     (day, temperature, humidity, pm2_5, pm10, aqi))

def read_sensors():
    for attempt in range(MAX_RETRIES):
        try:
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            data = ser.read(10)
            if len(data) == 10:
                pm2_5 = int.from_bytes(data[2:4], byteorder='little') / 10
                pm10 = int.from_bytes(data[4:6], byteorder='little') / 10
                return temperature, humidity, pm2_5, pm10
            else:
                print(f"Attempt {attempt+1}: Incomplete data received. Retrying...")
        except Exception as e:
            print(f"Attempt {attempt+1}: Error reading from sensor: {e}. Retrying...")
        time.sleep(1)  
    return None, None, None, None 

def main_loop():
    previous_aqi = None
    while True:
        temperature, humidity, pm2_5, pm10 = read_sensors()
        if None not in (temperature, humidity, pm2_5, pm10):
            print(f"Readings - Temp: {temperature:.1f} C, Humidity: {humidity:.1f}%, PM2.5: {pm2_5}, PM10: {pm10}")
            aqi = calculate_aqi(pm2_5, pm10)
            print(f"AQI Category: {aqi}")
            
            # Check if AQI has changed
            if aqi != previous_aqi:
                connect_to_wifi()  # Connect to WiFi
                publish_message("notifications", f"AQI Level Changed: {aqi}")
                #  disconnect_from_wifi()  # Disconnect from WiFi
                previous_aqi = aqi
            
            insert_into_db(temperature, humidity, pm2_5, pm10, aqi)
        else:
            print("All attempts failed. Skipping database insertion.")

        time.sleep(READ_INTERVAL)

if __name__ == "__main__":
    main_loop()
