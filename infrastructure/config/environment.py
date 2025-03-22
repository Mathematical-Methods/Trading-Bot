import os
import logging
from dotenv import load_dotenv

def initialize_environment():
    """
    Sets up the runtime environment by loading configuration from a .env file and configuring logging.

    Returns:
        tuple: (bool, dict) - Success flag and dictionary of environment variables (app_key, app_secret, callback_url).
    """
    # Load environment variables from .env file
    load_success = load_dotenv()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Retrieve required environment variables
    env_vars = {
        'app_key': os.getenv('app_key'),
        'app_secret': os.getenv('app_secret'),
        'callback_url': os.getenv('callback_url')
    }
    
    # Check if loading succeeded and all variables are present
    if not load_success:
        logging.error("Failed to load .env file")
        return False, env_vars
    if not all(env_vars.values()):
        logging.error("Missing required environment variables in .env file")
        return False, env_vars
    
    logging.info("Environment initialized successfully")
    return True, env_vars