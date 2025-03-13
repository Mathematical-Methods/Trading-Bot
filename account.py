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