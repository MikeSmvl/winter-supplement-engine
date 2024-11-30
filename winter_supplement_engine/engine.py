import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from dotenv import load_dotenv
from winter_supplement_engine.config import get_env_variable
from winter_supplement_engine.rules import process_supplement_request

class WinterSupplementEngine:
    def __init__(self):
        # load and get env variables
        load_dotenv()
        self.mqtt_broker = get_env_variable("MQTT_BROKER")
        self.mqtt_broker_port = get_env_variable("MQTT_BROKER_PORT", int)
        self.mqtt_input_topic_prefix = get_env_variable("MQTT_INPUT_TOPIC_PREFIX")
        self.mqtt_output_topic_prefix = get_env_variable("MQTT_OUTPUT_TOPIC_PREFIX")
        self.mqtt_topic_id = get_env_variable("MQTT_TOPIC_ID", required=False)

        # initialize client
        self.client = mqtt.Client(protocol=mqtt.MQTTv5, callback_api_version=CallbackAPIVersion.VERSION2)

        # setup topic based on whether MQTT_TOPIC_ID env variable is provided
        self.use_specific_topic = self.mqtt_topic_id is not None
        if self.use_specific_topic:
            self.input_topic = f"{self.mqtt_input_topic_prefix}/{self.mqtt_topic_id}"
            self.output_topic = f"{self.mqtt_output_topic_prefix}/{self.mqtt_topic_id}"
        else:
            self.input_topic = f"{self.mqtt_input_topic_prefix}/+"

        # setup callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print(f"Connected to MQTT broker: {self.mqtt_broker}:{self.mqtt_broker_port}")
            # subscribe to the input topic
            client.subscribe(self.input_topic)
            print(f"Subscribed to topic: {self.input_topic}")
        else:
            print(f"Failed to connect to MQTT broker with result code: {rc}")

    def on_disconnect(self, client, userdata, disconnect_flags, rc, properties):
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
                    output_topic = f"{self.mqtt_output_topic_prefix}/{topic_id}"
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
            print(f"Connecting to MQTT broker: {self.mqtt_broker}:{self.mqtt_broker_port}")
            self.client.connect(self.mqtt_broker, self.mqtt_broker_port)

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