import json
from winter_supplement_engine.rules import (
    validate_input,
    calculate_supplement,
    process_supplement_request,
    WinterSupplementInput,
    WinterSupplementOutput
)

def test_validate_input_valid_case():
    """
    Test that validate doesn't return None on a valid case
    """
    valid_input = {
        "id": "test123",
        "numberOfChildren": 2,
        "familyComposition": "single",
        "familyUnitInPayForDecember": True
    }
    assert validate_input(valid_input) is not None

def test_validate_input_valid_case_family_insensitive():
    """
    Test that validate isn't case sensitive for familyComposition
    """
    valid_input = {
        "id": "test123",
        "numberOfChildren": 2,
        "familyComposition": "Single", # Uppercase "S"
        "familyUnitInPayForDecember": True
    }
    assert validate_input(valid_input) is not None

def test_validate_input_missing_field():
    """
    Test that validate returns None when input field is missing
    """
    invalid_input = {
        "id": "test123",
        "numberOfChildren": 2,
        "familyComposition": "single"
    }
    assert validate_input(invalid_input) is None

def test_validate_input_invalid_number_of_children():
    """
    Test that validate returns None when input field is missing
    """
    invalid_input = {
        "id": "test123",
        "numberOfChildren": -1,  # Less than 0 children
        "familyComposition": "single",
        "familyUnitInPayForDecember": True
    }
    assert validate_input(invalid_input) is None

def test_validate_input_invalid_family_composition():
    """
    Test that validate returns None when family composition is not "single" or "couple"
    """
    invalid_input = {
        "id": "test123",
        "numberOfChildren": 2,
        "familyComposition": "invalid",
        "familyUnitInPayForDecember": True
    }
    assert validate_input(invalid_input) is None

def test_validate_input_invalid_types():
    """
    Test that validate returns None input types are wrong
    """
    invalid_input = {
        "id": 123,  # should be string
        "numberOfChildren": "2",  # should be int
        "familyComposition": "single",
        "familyUnitInPayForDecember": "true"  # should be bool
    }
    assert validate_input(invalid_input) is None

def test_supplement_calculation_single_no_children():
    """
    Test that supplement calculation works for single person with no children
    """
    input_data: WinterSupplementInput = {
        "id": "test1",
        "numberOfChildren": 0,
        "familyComposition": "single",
        "familyUnitInPayForDecember": True
    }
    result = calculate_supplement(input_data)
    assert result["baseAmount"] == 60.0
    assert result["childrenAmount"] == 0.0
    assert result["supplementAmount"] == 60.0

def test_supplement_calculation_couple_no_children():
    """
    Test that supplement calculation works for couple with no children
    """
    input_data: WinterSupplementInput = {
        "id": "test2",
        "numberOfChildren": 0,
        "familyComposition": "couple",
        "familyUnitInPayForDecember": True
    }
    result: WinterSupplementOutput = calculate_supplement(input_data)
    assert result["baseAmount"] == 120.0
    assert result["childrenAmount"] == 0.0
    assert result["supplementAmount"] == 120.0

def test_supplement_calculation_single_children():
    """
    Test that supplement calculation works for single person with children
    """
    input_data: WinterSupplementInput = {
        "id": "test3",
        "numberOfChildren": 2,
        "familyComposition": "single",
        "familyUnitInPayForDecember": True
    }
    result: WinterSupplementOutput = calculate_supplement(input_data)
    assert result["baseAmount"] == 120.0
    assert result["childrenAmount"] == 40.0
    assert result["supplementAmount"] == 160.0

def test_supplement_calculation_couple_children():
    """
    Test that supplement calculation works for couple with children
    """
    input_data: WinterSupplementInput = {
        "id": "test4",
        "numberOfChildren": 3,
        "familyComposition": "couple",
        "familyUnitInPayForDecember": True
    }
    result: WinterSupplementOutput = calculate_supplement(input_data)
    assert result["baseAmount"] == 120.0
    assert result["childrenAmount"] == 60.0
    assert result["supplementAmount"] == 180.0

def test_supplement_calculation_ineligible():
    """
    Test that supplement calculation works for ineligible clients (familyUnitInPayForDecember = False)
    """
    input_data: WinterSupplementInput = {
        "id": "test5",
        "numberOfChildren": 2,
        "familyComposition": "single",
        "familyUnitInPayForDecember": False
    }
    result: WinterSupplementOutput = calculate_supplement(input_data)
    assert result["isEligible"] is False
    assert result["baseAmount"] == 0.0
    assert result["childrenAmount"] == 0.0
    assert result["supplementAmount"] == 0.0

def test_json_processing_valid_input():
    """
    Test that json processing works for valid inputs
    """
    valid_json = json.dumps({
        "id": "test1",
        "numberOfChildren": 2,
        "familyComposition": "single",
        "familyUnitInPayForDecember": True
    })
    result = process_supplement_request(valid_json)
    assert result is not None
    parsed_result = json.loads(result)
    assert parsed_result["baseAmount"] == 120.0
    assert parsed_result["childrenAmount"] == 40.0

def test_json_processing_invalid_json():
    """
    Test that json processing returns None for invalid json
    """
    invalid_json = "{ invalid json }"
    result = process_supplement_request(invalid_json)
    assert result is None

def test_json_processing_invalid_data_types():
    """
    Test that json processing returns None for invalid json data types
    """
    invalid_data_json = json.dumps({
        "id": 123,  # should be string
        "numberOfChildren": "2",  # should be int
        "familyComposition": "single",
        "familyUnitInPayForDecember": "true"  # should be bool
    })
    result = process_supplement_request(invalid_data_json)
    assert result is None
