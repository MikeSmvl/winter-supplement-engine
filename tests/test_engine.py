import pytest
from unittest.mock import Mock, patch
import os
from winter_supplement_engine.config import get_env_variable

@pytest.fixture(autouse=True)
def mock_env_vars():
    """
    Mock both environment variables and dotenv loading
    """
    env_vars = {
        "MQTT_BROKER": "test.mosquitto.org",
        "MQTT_BROKER_PORT": "1883",
        "MQTT_INPUT_TOPIC_PREFIX": "test/input/",
        "MQTT_OUTPUT_TOPIC_PREFIX": "test/output/",
        "MQTT_TOPIC_ID": "test123"
    }
    with patch.dict(os.environ, env_vars, clear=True), \
         patch('winter_supplement_engine.engine.load_dotenv'):
        yield env_vars

@pytest.fixture
def mock_mqtt_client():
    """
    Mock the MQTT client
    """
    with patch('paho.mqtt.client.Client', autospec=True) as mock_client:
        client_instance = Mock()
        mock_client.return_value = client_instance
        yield client_instance

def test_environment_variable_loading():
    """Test that environment variables are loaded correctly"""
    from winter_supplement_engine.config import get_env_variable
    assert get_env_variable("MQTT_BROKER") == "test.mosquitto.org"
    assert get_env_variable("MQTT_BROKER_PORT", int) == 1883
    assert get_env_variable("MQTT_INPUT_TOPIC_PREFIX") == "test/input/"
    assert get_env_variable("MQTT_OUTPUT_TOPIC_PREFIX") == "test/output/"
    assert get_env_variable("MQTT_TOPIC_ID") == "test123"

def test_missing_environment_variable():
    """Test that missing environment variables raise ValueError"""
    with pytest.raises(ValueError) as exc_info:
        get_env_variable("NON_EXISTENT_VAR")
    assert "Missing required environment variable" in str(exc_info.value)

def test_invalid_environment_variable_type():
    """Test that invalid environment variable types raise ValueError"""
    os.environ["INVALID_PORT"] = "not_a_number"
    with pytest.raises(ValueError) as exc_info:
        get_env_variable("INVALID_PORT", int)
    assert "Invalid value" in str(exc_info.value)

def test_on_message():
    """Test the on_message callback function"""
    from winter_supplement_engine.engine import on_message
    client = Mock()
    userdata = None
    message = Mock()
    message.topic = "test/topic"
    message.payload = b"test message"

    with patch('builtins.print') as mock_print:
        on_message(client, userdata, message)
        mock_print.assert_called_once_with(
            "Message received on topic test/topic: test message"
        )

def test_start_successful_connection(mock_mqtt_client, mock_env_vars):
    """Test successful MQTT client connection and subscription"""
    from winter_supplement_engine.engine import start

    with patch('builtins.print') as mock_print:

        # avoid infinite loop
        mock_mqtt_client.loop_forever.side_effect = KeyboardInterrupt()

        try:
            start()
        except KeyboardInterrupt:
            pass

        # make sure connection is using right broker envs
        mock_mqtt_client.connect.assert_called_once_with(
            mock_env_vars["MQTT_BROKER"],
            int(mock_env_vars["MQTT_BROKER_PORT"])
        )

        # check that subscription is made to correct topic
        expected_topic = f"{mock_env_vars['MQTT_INPUT_TOPIC_PREFIX']}{mock_env_vars['MQTT_TOPIC_ID']}"
        mock_mqtt_client.subscribe.assert_called_once_with(expected_topic)

def test_start_connection_failure(mock_mqtt_client):
    """Test MQTT client connection failure handling"""
    from winter_supplement_engine.engine import start

    mock_mqtt_client.connect.side_effect = Exception("Connection failed")

    with patch('builtins.print') as mock_print:
        start()

        # make sure error message is printed
        mock_print.assert_called_with("An error occurred: Connection failed")