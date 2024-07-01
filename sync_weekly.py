import sqlite3
import json
from mqtt_client import publish_message  
import math
from datetime import datetime, timedelta

# SQLite Database
DB_PATH = 'sensor_data.db'
MQTT_TOPIC = 'pollution_data'  
CHUNK_SIZE = 50  # Adjust the chunk size as needed

def fetch_data_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    one_week_ago = datetime.now() - timedelta(days=7)
    cursor.execute("SELECT * FROM sensor_readings WHERE timestamp >= ?", (one_week_ago,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def format_data(rows):
    formatted_data = []
    for row in rows:
        formatted_data.append({
            "dateTime": row[0],
            "temperature": row[1],
            "humidity": row[2],
            "PM25": row[3],
            "PM10": row[4],
            "aqiLevel": row[5],
            "dayOfWeek": row[6]
        })
    return formatted_data

def send_data_via_mqtt(data):
    total_chunks = math.ceil(len(data) / CHUNK_SIZE)
    for i in range(total_chunks):
        chunk = data[i*CHUNK_SIZE:(i+1)*CHUNK_SIZE]
        message = {"message": f"Sending chunk {i+1}/{total_chunks}", "data": chunk}
        publish_message(MQTT_TOPIC, json.dumps(message))

def main():
    data = fetch_data_from_db()
    if data:
        formatted_data = format_data(data)
        send_data_via_mqtt(formatted_data)
    else:
        print("No data to send")

if __name__ == "__main__":
    main()
