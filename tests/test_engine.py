import pytest
from unittest.mock import Mock, patch
import os
from winter_supplement_engine.config import get_env_variable
from winter_supplement_engine.engine import WinterSupplementEngine

@pytest.fixture()
def mock_env_vars_with_topic_id():
    """
    Mock environment variables with a TOPIC ID
    """
    env_vars = {
        "MQTT_BROKER": "test.mosquitto.org",
        "MQTT_BROKER_PORT": "1883",
        "MQTT_INPUT_TOPIC_PREFIX": "BRE/calculateWinterSupplementInput",
        "MQTT_OUTPUT_TOPIC_PREFIX": "BRE/calculateWinterSupplementOutput",
        "MQTT_TOPIC_ID": "test123"
    }
    with patch.dict(os.environ, env_vars, clear=True), \
         patch('winter_supplement_engine.engine.load_dotenv'):
        yield env_vars

@pytest.fixture()
def mock_env_vars_without_topic_id():
    """
    Mock environment variables with a TOPIC ID
    """
    env_vars = {
        "MQTT_BROKER": "test.mosquitto.org",
        "MQTT_BROKER_PORT": "1883",
        "MQTT_INPUT_TOPIC_PREFIX": "BRE/calculateWinterSupplementInput",
        "MQTT_OUTPUT_TOPIC_PREFIX": "BRE/calculateWinterSupplementOutput",
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

def test_environment_variable_loading_with_topic_id(mock_env_vars_with_topic_id):
    """
    Test that environment variables are loaded correctly with Topic ID
    """
    with patch.dict(os.environ, mock_env_vars_with_topic_id, clear=True):
        assert get_env_variable("MQTT_BROKER") == "test.mosquitto.org"
        assert get_env_variable("MQTT_BROKER_PORT", int) == 1883
        assert get_env_variable("MQTT_INPUT_TOPIC_PREFIX") == "BRE/calculateWinterSupplementInput"
        assert get_env_variable("MQTT_OUTPUT_TOPIC_PREFIX") == "BRE/calculateWinterSupplementOutput"
        assert get_env_variable("MQTT_TOPIC_ID", required=False) == "test123"

def test_environment_variable_loading_without_topic_id(mock_env_vars_without_topic_id):
    """
    Test that environment variables are loaded correctly without Topic ID
    """
    with patch.dict(os.environ, mock_env_vars_without_topic_id, clear=True):
        assert get_env_variable("MQTT_BROKER") == "test.mosquitto.org"
        assert get_env_variable("MQTT_BROKER_PORT", int) == 1883
        assert get_env_variable("MQTT_INPUT_TOPIC_PREFIX") == "BRE/calculateWinterSupplementInput"
        assert get_env_variable("MQTT_OUTPUT_TOPIC_PREFIX") == "BRE/calculateWinterSupplementOutput"
        assert get_env_variable("MQTT_TOPIC_ID", required=False) is None

def test_missing_environment_variable():
    """
    Test that missing environment variables raise ValueError
    """
    with pytest.raises(ValueError) as exc_info:
        get_env_variable("NON_EXISTENT_VAR")
    assert "Missing required environment variable" in str(exc_info.value)

def test_invalid_environment_variable_type():
    """
    Test that invalid environment variable types raise ValueError
    """
    os.environ["INVALID_PORT"] = "not_a_number"
    with pytest.raises(ValueError) as exc_info:
        get_env_variable("INVALID_PORT", int)
    assert "Invalid value" in str(exc_info.value)

def test_on_message_with_topic_id(mock_env_vars_with_topic_id, mock_mqtt_client):
    """
    Test the on_message callback function with a Topic ID
    """
    with patch.dict(os.environ, mock_env_vars_with_topic_id, clear=True), \
         patch('winter_supplement_engine.engine.load_dotenv'), \
         patch('winter_supplement_engine.engine.process_supplement_request') as mock_process:

        engine = WinterSupplementEngine()
        message = Mock()
        message.topic = "BRE/calculateWinterSupplementInput/test123"
        message.payload = b'{"test": "data"}'
        mock_process.return_value = '{"test": "123"}'

        engine.on_message(mock_mqtt_client, None, message)
        mock_mqtt_client.publish.assert_called_once_with(
            "BRE/calculateWinterSupplementOutput/test123",
            '{"test": "123"}'
        )

def test_engine_initialization_without_topic_id(mock_env_vars_without_topic_id):
    """
    Test engine initialization without Topic ID
    """
    with patch.dict(os.environ, mock_env_vars_without_topic_id, clear=True), \
         patch('winter_supplement_engine.engine.load_dotenv'):
        engine = WinterSupplementEngine()
        assert engine.use_specific_topic is False
        assert engine.input_topic == "BRE/calculateWinterSupplementInput/+"
        assert not hasattr(engine, 'output_topic')

def test_start_successful_connection(mock_mqtt_client, mock_env_vars_with_topic_id):
    """
    Test successful MQTT client connection and subscription
    """
    with patch.dict(os.environ, mock_env_vars_with_topic_id, clear=True), \
         patch('winter_supplement_engine.engine.load_dotenv'), \
         patch('builtins.print') as mock_print:

        engine = WinterSupplementEngine()
        engine.use_specific_topic = True
        engine.input_topic = f"{mock_env_vars_with_topic_id['MQTT_INPUT_TOPIC_PREFIX']}/{mock_env_vars_with_topic_id['MQTT_TOPIC_ID']}"
        # avoid infinite loop
        mock_mqtt_client.loop_forever.side_effect = KeyboardInterrupt()

        try:
            engine.on_connect(mock_mqtt_client, None, None, 0)
            engine.start()
        except KeyboardInterrupt:
            pass

        # make sure connection is using right broker envs
        mock_mqtt_client.connect.assert_called_once_with(
            mock_env_vars_with_topic_id["MQTT_BROKER"],
            int(mock_env_vars_with_topic_id["MQTT_BROKER_PORT"])
        )

        # check that subscription is made to correct topic
        expected_topic = f"{mock_env_vars_with_topic_id['MQTT_INPUT_TOPIC_PREFIX']}/{mock_env_vars_with_topic_id['MQTT_TOPIC_ID']}"
        mock_mqtt_client.subscribe.assert_called_once_with(expected_topic)

def test_start_connection_failure(mock_mqtt_client, mock_env_vars_with_topic_id):
    """
    Test MQTT client connection failure handling
    """

    mock_mqtt_client.connect.side_effect = Exception("Connection failed")

    with patch.dict(os.environ, mock_env_vars_with_topic_id, clear=True), \
         patch('winter_supplement_engine.engine.load_dotenv'), \
         patch('builtins.print') as mock_print, \
         patch('winter_supplement_engine.engine.exit') as mock_exit:

        engine = WinterSupplementEngine()
        mock_mqtt_client.connect.side_effect = Exception("Connection failed")

        engine.start()

        mock_exit.assert_called_once_with(1)
        # make sure error message is printed
        mock_print.assert_called_with("An error occurred: Connection failed")