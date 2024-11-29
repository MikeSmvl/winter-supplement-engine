import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from winter_supplement_engine.config import get_env_variable
from winter_supplement_engine.rules import process_supplement_request

# load environment variables from the .env file
load_dotenv()

# attempt to get all environment variables needed
try:
    MQTT_BROKER = get_env_variable("MQTT_BROKER")
    MQTT_BROKER_PORT = get_env_variable("MQTT_BROKER_PORT", int)
    MQTT_INPUT_TOPIC_PREFIX = get_env_variable("MQTT_INPUT_TOPIC_PREFIX")
    MQTT_OUTPUT_TOPIC_PREFIX = get_env_variable("MQTT_OUTPUT_TOPIC_PREFIX")
    # Optional
    MQTT_TOPIC_ID = get_env_variable("MQTT_TOPIC_ID", required=False)
except ValueError as e:
    print(f"Error loading environment variables: {e}")
    exit(1)

class WinterSupplementEngine:
    def __init__(self):
        # initialize client and topics
        self.client = mqtt.Client()

        self.use_specific_topic = MQTT_TOPIC_ID is not None
        if self.use_specific_topic:
            self.input_topic = f"{MQTT_INPUT_TOPIC_PREFIX}/{MQTT_TOPIC_ID}"
            self.output_topic = f"{MQTT_OUTPUT_TOPIC_PREFIX}/{MQTT_TOPIC_ID}"
        else:
            self.input_topic = f"{MQTT_INPUT_TOPIC_PREFIX}/+"

        # setup callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT broker: {MQTT_BROKER}:{MQTT_BROKER_PORT}")
            # subscribe to the input topic
            client.subscribe(self.input_topic)
            print(f"Subscribed to topic: {self.input_topic}")
        else:
            print(f"Failed to connect to MQTT broker with result code: {rc}")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            # print reason code for the disconnection
            print(f"Disconnected from MQTT broker: {rc}")

    # callback when message is received
    def on_message(self, client, userdata, message):
        try:
            print(f"Message received on topic {message.topic}: {message.payload.decode()}")

            # if topic ID is in env, use it
            if self.use_specific_topic:
                output_topic = self.output_topic
            # otherwise, extract it from the incoming message
            else:
                topic_parts = message.topic.split('/')
                if len(topic_parts) >= 3:
                    topic_id = topic_parts[-1]
                    output_topic = f"{MQTT_OUTPUT_TOPIC_PREFIX}/{topic_id}"
                else:
                    print(f"Invalid topic format: {message.topic}")
                    return

            # process the request using business rules
            result = process_supplement_request(message.payload.decode())

            # we only want to publish when there is a result
            # otherwise the validation failed
            if result is not None:
                # publish to the output topic
                client.publish(output_topic, result)
                print(f"Published result to topic {output_topic}: {result}")
            else:
                print("Failed to process request")

        except Exception as e:
            print(f"Error processing message: {e}")

    def start(self):
        """Start the MQTT client"""
        try:
            # connect to the broker
            print(f"Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_BROKER_PORT}")
            self.client.connect(MQTT_BROKER, MQTT_BROKER_PORT)

            # keep engine running
            self.client.loop_forever()

        except Exception as e:
            print(f"An error occurred: {e}")
            exit(1)

def main():
    engine = WinterSupplementEngine()
    engine.start()


if __name__ == "__main__":
    main()