import sqlite3
import json
from mqtt_client import publish_message  
# SQLite Database
DB_PATH = 'sensor_data.db'
MQTT_TOPIC = 'pollution_data'  

def fetch_data_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sensor_readings")
    rows = cursor.fetchall()
    conn.close()
    return rows

def send_data_via_mqtt(data):
    for record in data:
        payload = {
            "timestamp": record[0],
            "day": record[1],
            "temperature": record[2],
            "humidity": record[3],
            "pm25": record[4],
            "pm10": record[6],
            "aqiLevel": record[5]
        }
        message = json.dumps(payload)
        publish_message(MQTT_TOPIC, message)

def main():
    data = fetch_data_from_db()
    if data:
        send_data_via_mqtt(data)
    else:
        print("No data to send")

if __name__ == "__main__":
    main()
