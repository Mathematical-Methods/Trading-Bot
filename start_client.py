import schwabdev
import logging

def start_client(app_key, app_secret, callback_url):
    """
    Creates and configures a Schwab API client instance using provided credentials.

    Args:
        app_key (str): Schwab API application key.
        app_secret (str): Schwab API application secret.
        callback_url (str): Callback URL for OAuth authentication.

    Returns:
        tuple: (bool, schwabdev.Client or None) - Success flag and the client instance if successful, None if failed.
    """
    if not all([app_key, app_secret, callback_url]):
        logging.error("One or more client credentials are missing or invalid")
        return False, None
    
    try:
        client = schwabdev.Client(app_key, app_secret, callback_url)
        logging.info("Schwab client initialized successfully")
        return True, client
    except Exception as e:
        logging.error(f"Failed to initialize Schwab client: {str(e)}")
        return False, None