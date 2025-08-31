import json
import os

from src.config.config import UserConfiguration

def load_and_validate_config(config_path: str) -> UserConfiguration:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        SpectrometerFullConfig: The loaded configuration.

    Raises:
        ValueError in case the configuration file provided by the user was not found
        ValidationError in case the configuration file provided by the user is not valid
    """
    if not config_path:
        raise ValueError("No configuration file was provided")
    
    # Check if the file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError("No configuration file found")
    
    # Load the configuration from the file
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from the configuration file: {e}")
    
    # Create and return the configuration object using Pydantic.
    # This will raise ValidationError if the data is invalid!
    return UserConfiguration.model_validate(config_data)