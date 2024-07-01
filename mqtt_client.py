import paho.mqtt.client as mqtt

# Define the MQTT settings
MQTT_BROKER = "192.168.0.100"  # Change this to the broker's IP address
MQTT_PORT = 8883
MQTT_TOPIC = "notifications"

# Path to the certificate files
CA_CERTS = "keys/ca.crt"
CERTFILE = "keys/client.crt"
KEYFILE = "keys/client.key"

# Create an MQTT client instance
client = mqtt.Client()

# Set the TLS/SSL parameters
client.tls_set(ca_certs=CA_CERTS, certfile=CERTFILE, keyfile=KEYFILE)

# Disable SSL certificate verification for demo purposes
client.tls_insecure_set(True)

# Define the callback function for connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print(f"Connect failed with code {rc}")

# Define the callback function for log
def on_log(client, userdata, level, buf):
    print(f"log: {buf}")

# Define the callback function for message
def on_message(client, userdata, msg):
    print(f"Message received: Topic: {msg.topic}, Payload: {msg.payload.decode()}")

# Assign the callback functions
client.on_connect = on_connect
client.on_log = on_log
client.on_message = on_message

# Connect to the broker
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    print(f"Connection failed: {e}")

def publish_message(topic, message):
    try:
        result = client.publish(topic, message)
        status = result[0]
        if status == 0:
            print(f"Message sent to topic {topic}")
        else:
            print(f"Failed to send message to topic {topic}")
    except Exception as e:
        print(f"Publish failed: {e}")

