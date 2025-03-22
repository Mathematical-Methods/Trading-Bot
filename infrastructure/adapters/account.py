import logging

def fetch_account_hash(client, simulate):
    """
    Retrieves the account hash for real trading if simulation is disabled.

    Args:
        client (schwabdev.Client): Initialized Schwab API client object.
        simulate (bool): Flag indicating if trading is in simulation mode.

    Returns:
        tuple: (bool, str or None) - Success flag and account hash if retrieved, None if simulating or failed.
    """
    if simulate:
        logging.info("Simulation mode enabled; no account hash retrieved")
        return True, None
    
    if client is None:
        logging.error("Client object is None; cannot fetch account hash")
        return False, None
    
    try:
        response = client.account_linked()
        if not response.ok:
            logging.error(f"Failed to fetch linked accounts: {response.status_code} - {response.text}")
            return False, None
        
        accounts = response.json()
        if not accounts or "hashValue" not in accounts[0]:
            logging.error("No accounts found or invalid response format")
            return False, None
        
        account_hash = accounts[0]["hashValue"]
        logging.info(f"Account hash retrieved successfully: {account_hash}")
        return True, account_hash
    
    except Exception as e:
        logging.error(f"Exception while fetching account hash: {str(e)}")
        return False, None

def request_account_details(client, account_hash):
    """
    Fetches detailed account information from Schwab for the specified account.

    Args:
        client (schwabdev.Client): Initialized Schwab API client object.
        account_hash (str): Hash of the account to query.

    Returns:
        tuple: (bool, dict or None) - Success flag and account details if retrieved, None if failed.
    """
    if client is None:
        logging.error("Client object is None; cannot fetch account details")
        return False, None
    
    if not account_hash or not isinstance(account_hash, str):
        logging.error("Invalid or missing account hash")
        return False, None
    
    try:
        response = client.account_details(account_hash)
        if not response.ok:
            logging.error(f"Failed to fetch account details: {response.status_code} - {response.text}")
            return False, None
        
        account_details = response.json()
        if not account_details:
            logging.error("Empty account details response")
            return False, None
        
        logging.info(f"Account details retrieved successfully for hash: {account_hash}")
        return True, account_details
    
    except Exception as e:
        logging.error(f"Exception while fetching account details: {str(e)}")
        return False, None

def request_account_positions(client, account_hash):
    """
    Retrieves current positions (e.g., stock holdings) for the Schwab account.

    Args:
        client (schwabdev.Client): Initialized Schwab API client object.
        account_hash (str): Hash of the account to query.

    Returns:
        tuple: (bool, list or None) - Success flag and list of position dictionaries if retrieved, None if failed.
    """
    if client is None:
        logging.error("Client object is None; cannot fetch account positions")
        return False, None
    
    if not account_hash or not isinstance(account_hash, str):
        logging.error("Invalid or missing account hash")
        return False, None
    
    try:
        response = client.account_positions(account_hash)
        if not response.ok:
            logging.error(f"Failed to fetch account positions: {response.status_code} - {response.text}")
            return False, None
        
        positions_data = response.json()
        positions = positions_data.get('positions', [])
        
        if not positions:
            logging.info("No positions found for the account")
            return True, []
        
        logging.info(f"Account positions retrieved successfully for hash: {account_hash}")
        return True, positions
    
    except Exception as e:
        logging.error(f"Exception while fetching account positions: {str(e)}")
        return False, None