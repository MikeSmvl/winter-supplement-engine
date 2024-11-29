import json
from winter_supplement_engine.rules import (
    validate_input,
    calculate_supplement,
    process_supplement_request,
    WinterSupplementInput,
    WinterSupplementOutput
)

# Test inputs for validate_input
def test_validate_input_valid_case():
    valid_input = {
        "id": "test123",
        "numberOfChildren": 2,
        "familyComposition": "single",
        "familyUnitInPayForDecember": True
    }
    assert validate_input(valid_input) is not None

def test_validate_input_missing_field():
    invalid_input = {
        "id": "test123",
        "numberOfChildren": 2,
        "familyComposition": "single"
    }
    assert validate_input(invalid_input) is None

def test_validate_input_invalid_number_of_children():
    invalid_input = {
        "id": "test123",
        "numberOfChildren": -1,  # Less than 0 children
        "familyComposition": "single",
        "familyUnitInPayForDecember": True
    }
    assert validate_input(invalid_input) is None

def test_validate_input_invalid_family_composition():
    invalid_input = {
        "id": "test123",
        "numberOfChildren": 2,
        "familyComposition": "invalid",
        "familyUnitInPayForDecember": True
    }
    assert validate_input(invalid_input) is None

def test_validate_input_invalid_types():
    invalid_input = {
        "id": 123,  # should be string
        "numberOfChildren": "2",  # should be int
        "familyComposition": "single",
        "familyUnitInPayForDecember": "true"  # should be bool
    }
    assert validate_input(invalid_input) is None

# Test supplement calculations
def test_supplement_calculation_single_no_children():
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

# Test JSON processing
def test_json_processing_valid_input():
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
    invalid_json = "{ invalid json }"
    result = process_supplement_request(invalid_json)
    assert result is None

def test_json_processing_invalid_data_types():
    invalid_data_json = json.dumps({
        "id": 123,  # should be string
        "numberOfChildren": "2",  # should be int
        "familyComposition": "single",
        "familyUnitInPayForDecember": "true"  # should be bool
    })
    result = process_supplement_request(invalid_data_json)
    assert result is None
