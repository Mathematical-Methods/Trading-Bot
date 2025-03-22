import os
import logging
from dotenv import load_dotenv
from schwabdev import Client

load_dotenv()  # Load environment variables from .env file

class SchwabClientAdapter:
    def __init__(self):
        """
        Initialize the SchwabClientAdapter with API credentials and fetch account hashes.
        
        Raises:
            ValueError: If required environment variables are missing.
        """
        app_key = os.getenv('app_key')
        app_secret = os.getenv('app_secret')
        callback_url = os.getenv('callback_url')
        if not all([app_key, app_secret, callback_url]):
            raise ValueError("Missing required environment variables: app_key, app_secret, or callback_url")
        self.client = Client(app_key, app_secret, callback_url)
        self.account_hashes = self._fetch_account_hashes()
        logging.info("SchwabClientAdapter initialized")

    def _fetch_account_hashes(self):
        """
        Fetch account hashes using client.account_linked().

        Returns:
            dict: Mapping of account numbers to their hash values.
        """
        try:
            response = self.client.account_linked()
            if response.ok:
                accounts = response.json()
                # Create a dictionary mapping account numbers to hash values
                hashes = {account['accountNumber']: account['hashValue'] for account in accounts}
                logging.info(f"Fetched account hashes for accounts: {list(hashes.keys())}")
                return hashes
            else:
                logging.error(f"Failed to fetch account hashes: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logging.error(f"Exception fetching account hashes: {str(e)}")
            return {}

    def get_historical_data(self, symbol, period_type, period, frequency_type, frequency):
        """
        Fetch historical price data for a symbol.

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL').
            period_type (str): Type of period (e.g., 'day', 'month').
            period (int): Number of periods.
            frequency_type (str): Type of frequency (e.g., 'minute', 'daily').
            frequency (int): Frequency value.

        Returns:
            dict: Historical data response or None if failed.
        """
        try:
            response = self.client.price_history(
                symbol=symbol,
                periodType=period_type,
                period=period,
                frequencyType=frequency_type,
                frequency=frequency,
                needExtendedHoursData=False
            )
            if response.ok:
                logging.info(f"Fetched historical data for {symbol}")
                return response.json()
            else:
                logging.error(f"Failed to fetch historical data for {symbol}: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logging.error(f"Exception fetching historical data for {symbol}: {str(e)}")
            return None

    def get_account_details(self, account_number=None):
        """
        Retrieve account details for the specified account number.

        Args:
            account_number (str, optional): Account number to query. If None, uses the first available account.

        Returns:
            dict: Account details or None if failed.
        """
        if not account_number and self.account_hashes:
            account_number = list(self.account_hashes.keys())[0]
        if not account_number or account_number not in self.account_hashes:
            logging.error(f"Invalid or no account number provided. Available accounts: {list(self.account_hashes.keys())}")
            return None
        account_hash = self.account_hashes[account_number]
        try:
            response = self.client.account_details(account_hash)
            if response.ok:
                logging.info(f"Fetched account details for account {account_number}")
                return response.json()
            else:
                logging.error(f"Failed to fetch account details: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logging.error(f"Exception fetching account details for {account_number}: {str(e)}")
            return None

    def get_positions(self, account_number=None):
        """
        Retrieve current positions for the specified account number.

        Args:
            account_number (str, optional): Account number to query. If None, uses the first available account.

        Returns:
            list: List of positions or None if failed.
        """
        if not account_number and self.account_hashes:
            account_number = list(self.account_hashes.keys())[0]
        if not account_number or account_number not in self.account_hashes:
            logging.error(f"Invalid or no account number provided. Available accounts: {list(self.account_hashes.keys())}")
            return None
        account_hash = self.account_hashes[account_number]
        try:
            response = self.client.account_details(account_hash)
            if response.ok:
                data = response.json()
                positions = data.get('securitiesAccount', {}).get('positions', [])
                logging.info(f"Fetched {len(positions)} positions for account {account_number}")
                return positions
            else:
                logging.error(f"Failed to fetch positions: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logging.error(f"Exception fetching positions for {account_number}: {str(e)}")
            return None

    def place_order(self, order, account_number=None):
        """
        Place a buy or sell order for the specified account number.

        Args:
            order (dict): Order details.
            account_number (str, optional): Account number to place the order for. If None, uses the first available account.

        Returns:
            bool: True if order was placed successfully, False otherwise.
        """
        if not account_number and self.account_hashes:
            account_number = list(self.account_hashes.keys())[0]
        if not account_number or account_number not in self.account_hashes:
            logging.error(f"Invalid or no account number provided. Available accounts: {list(self.account_hashes.keys())}")
            return False
        account_hash = self.account_hashes[account_number]
        try:
            response = self.client.order_place(account_hash, order)
            if response.ok:
                logging.info(f"Order placed successfully for account {account_number}")
                return True
            else:
                logging.error(f"Failed to place order: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logging.error(f"Exception placing order for {account_number}: {str(e)}")
            return False