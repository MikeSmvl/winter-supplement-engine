import os

# function to raise errors if environment variables are missing
def get_env_variable(var_name, var_type=str, default=None):
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {var_name}")
    try:
        return var_type(value)
    except ValueError as e:
        raise ValueError(f"Invalid value for {var_name}: {e}")