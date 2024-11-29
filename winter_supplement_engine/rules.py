from typing import TypedDict, Literal, Annotated, Optional
from dataclasses import dataclass
import json

# the type of the messages the engine should receive
class WinterSupplementInput(TypedDict):
    id: str
    numberOfChildren: Annotated[int, "Must be 0 or greater"]
    familyComposition: Literal["single", "couple"]
    familyUnitInPayForDecember: bool

# the type of the messages the engine will send
class WinterSupplementOutput(TypedDict):
    id: str
    isEligible: bool
    baseAmount: float
    childrenAmount: float
    supplementAmount: float

# function to validate the messages the engine receives
def validate_input(data: dict) -> Optional[WinterSupplementInput]:
    try:
        # make sure all fields are present
        required_fields = {'id', 'numberOfChildren', 'familyComposition', 'familyUnitInPayForDecember'}
        if not all(field in data for field in required_fields):
            missing = required_fields - set(data.keys())
            raise ValueError(f"Missing required fields: {missing}")

        # validate id
        if not isinstance(data['id'], str):
            raise ValueError("id must be a string")

        # validate numberOfChildren
        if not isinstance(data['numberOfChildren'], int) or data['numberOfChildren'] < 0:
            raise ValueError("numberOfChildren must be a non-negative integer")

        # validate familyComposition
        if data['familyComposition'] not in ["single", "couple"]:
            raise ValueError("familyComposition must be either 'single' or 'couple'")

        # validate familyUnitInPayForDecember
        if not isinstance(data['familyUnitInPayForDecember'], bool):
            raise ValueError("familyUnitInPayForDecember must be a boolean")

        return data
    except Exception as e:
        print(f"Input validation error: {str(e)}")
        return None


# calculates supplement given a valid input and returns a valid output
def calculate_supplement(data: WinterSupplementInput) -> WinterSupplementOutput:
    try:
        # Extract input values
        client_id = data['id']
        is_eligible = data['familyUnitInPayForDecember']
        num_children = data['numberOfChildren']
        family_type = data['familyComposition']

        # If not eligible, return zeros
        if not is_eligible:
            return {
                "id": client_id,
                "isEligible": False,
                "baseAmount": 0.0,
                "childrenAmount": 0.0,
                "supplementAmount": 0.0
            }

        # Calculate base amount
        base_amount = 60.0 if family_type == "single" and num_children == 0 else 120.0

        # Calculate children amount
        children_amount = 20.0 * num_children if num_children > 0 else 0.0

        # Calculate total
        total_amount = base_amount + children_amount

        # Create and validate output
        output: WinterSupplementOutput = {
            "id": client_id,
            "isEligible": True,
            "baseAmount": float(base_amount),
            "childrenAmount": float(children_amount),
            "supplementAmount": float(total_amount)
        }

        return output

    except Exception as e:
        # If any calculation fails, return an error result
        print(f"Calculation error: {str(e)}")
        return {
            "id": data['id'],
            "isEligible": False,
            "baseAmount": 0.0,
            "childrenAmount": 0.0,
            "supplementAmount": 0.0
        }

# process valid json string and return a json output
def process_supplement_request(json_input: str) -> Optional[str]:
    try:
        # Parse JSON
        data = json.loads(json_input)

        # Validate input
        validated_input = validate_input(data)
        if validated_input is None:
            return None

        # Calculate supplement
        result = calculate_supplement(validated_input)

        # Return JSON string
        return json.dumps(result)

    except json.JSONDecodeError:
        print("Invalid JSON input")
        return None
    except Exception as e:
        print(f"Processing error: {str(e)}")
        return None