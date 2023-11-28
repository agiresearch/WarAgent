import json, json5, ast
import re

def re_format_to_json(data_string):
    # Remove non-JSON compliant leading and trailing characters (e.g., backticks)
    data_string = data_string.strip("` \n\r\t")

    # replace "s
    data_string = data_string.replace('"s ', "'s ")

    # Add double quotes around keys (assuming they are simple words)
    # This regex avoids replacing inside already quoted strings
    data_string = re.sub(r'(?<!")(\b\w+\b)(?!"): ', r'"\1": ', data_string)

    # Remove any trailing commas in objects or arrays
    data_string = re.sub(r',\s*([}\]])', r'\1', data_string)

    # Remove anything before the first opening brace
    data_string = re.sub(r'^[^{]*', '', data_string)

    return data_string


def parse_JSON_string(json_string):
    """Parse a string into a JSON object.

    Args:
        json_string (str): The string representation of a JSON object.

    Returns:
        dict: Parsed JSON object.

    Raises:
        ValueError: If the string is not a valid JSON.
    """
    try: # json
        return json.loads(json_string)
    except:
        try: # json5
            return json5.loads(json_string)
        except:
            try: # re
                return json.loads(re_format_to_json(json_string))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {e}")

def parse_dict_string(dict_string):
    # dict_string = re_format_to_json(dict_string)
    try:
        dict_object = ast.literal_eval(dict_string)
        if not isinstance(dict_object, dict):
            raise ValueError("Provided string does not evaluate to a dictionary.")
        return dict_object
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Error parsing dictionary string: {e}")