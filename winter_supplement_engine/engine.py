import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from winter_supplement_engine.config import get_env_variable

# load environment variables from the .env file
load_dotenv()

# attempt to get all environment variables needed
try:
    MQTT_BROKER = get_env_variable("MQTT_BROKER")
    MQTT_BROKER_PORT = get_env_variable("MQTT_BROKER_PORT", int)
    MQTT_INPUT_TOPIC_PREFIX = get_env_variable("MQTT_INPUT_TOPIC_PREFIX")
    MQTT_OUTPUT_TOPIC_PREFIX = get_env_variable("MQTT_OUTPUT_TOPIC_PREFIX")
    MQTT_TOPIC_ID = get_env_variable("MQTT_TOPIC_ID")
except ValueError as e:
    print(f"Error loading environment variables: {e}")
    exit(1)

# create the full input topic name using the prefix and topic ID
input_topic = f"{MQTT_INPUT_TOPIC_PREFIX}{MQTT_TOPIC_ID}"

# receive PUBLISH message from the server
def on_message(client, userdata, message):
    print(f"Message received on topic {message.topic}: {message.payload.decode()}")

# function to start the MQTT client
def start():
    # initialize the MQTT client
    client = mqtt.Client()

    # assign the message handler
    client.on_message = on_message

    try:
        # connect to the broker
        print(f"Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_BROKER_PORT}")
        client.connect(MQTT_BROKER, MQTT_BROKER_PORT)
        print(f"Connected to MQTT broker: {MQTT_BROKER}:{MQTT_BROKER_PORT}")

        # subscribe to the topic
        print(f"Subscribing to topic: {input_topic}")
        client.subscribe(input_topic)
        print(f"Subscribed to topic: {input_topic}")

        # listen for messages on a loop
        client.loop_forever()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    start()