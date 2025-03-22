import os
import unittest
from unittest.mock import patch, Mock
from dotenv import load_dotenv
from infrastructure.adapters import schwab_client_adapter  # Import the module containing SchwabClientAdapter

# Load environment variables from .env file
load_dotenv()

class TestSchwabClientAdapter(unittest.TestCase):
    def setUp(self):
        """Set up the test environment with a mocked Client and initialized adapter."""
        # Patch the Client class in the schwab_client_adapter module's namespace
        self.patcher = patch('infrastructure.adapters.schwab_client_adapter.Client')
        self.mock_client_class = self.patcher.start()
        
        # Define test account number and hash value
        self.account_number = '50410887'
        self.hash_value = os.getenv('hash_value')
        
        # Set up the mock client instance
        self.mock_client = Mock()
        self.mock_client_class.return_value = self.mock_client
        
        # Mock the account_linked response for initialization
        self.mock_client.account_linked.return_value = Mock(ok=True)
        self.mock_client.account_linked.return_value.json.return_value = [
            {'accountNumber': self.account_number, 'hashValue': self.hash_value}
        ]
        
        # Initialize the adapter with the mocked client
        self.adapter = schwab_client_adapter.SchwabClientAdapter()

    def tearDown(self):
        """Clean up by stopping the patch."""
        self.patcher.stop()

    def test_initialization(self):
        """Test that the adapter initializes correctly and stores account hashes."""
        self.assertEqual(self.adapter.account_hashes, {self.account_number: self.hash_value})

    def test_get_account_details_success(self):
        """Test successful retrieval of account details for a valid account."""
        mock_response = Mock(ok=True)
        mock_response.json.return_value = {
            'securitiesAccount': {'accountNumber': self.account_number, 'type': 'MARGIN'}
        }
        self.mock_client.account_details.return_value = mock_response
        details = self.adapter.get_account_details(self.account_number)
        self.assertEqual(details['securitiesAccount']['accountNumber'], self.account_number)

    def test_get_account_details_failure(self):
        """Test account details retrieval fails gracefully for an invalid account."""
        details = self.adapter.get_account_details('invalid_account')
        self.assertIsNone(details)
        self.mock_client.account_details.assert_not_called()

    def test_get_account_details_no_hash(self):
        """Test account details retrieval uses the default account when no hash is provided."""
        mock_response = Mock(ok=True)
        mock_response.json.return_value = {
            'securitiesAccount': {'accountNumber': self.account_number, 'type': 'MARGIN'}
        }
        self.mock_client.account_details.return_value = mock_response
        details = self.adapter.get_account_details()
        self.assertEqual(details['securitiesAccount']['accountNumber'], self.account_number)
        self.mock_client.account_details.assert_called_once_with(self.hash_value)

    def test_get_historical_data_success(self):
        """Test successful retrieval of historical data."""
        mock_response = Mock(ok=True)
        mock_response.json.return_value = {'candles': [{'close': 100.0}], 'symbol': 'AAPL'}
        self.mock_client.price_history.return_value = mock_response
        data = self.adapter.get_historical_data('AAPL', 'day', 1, 'minute', 1)
        self.assertEqual(data['candles'][0]['close'], 100.0)

    def test_get_historical_data_failure(self):
        """Test historical data retrieval fails gracefully on API error."""
        mock_response = Mock(ok=False, status_code=500, text='Server error')
        self.mock_client.price_history.return_value = mock_response
        data = self.adapter.get_historical_data('AAPL', 'day', 1, 'minute', 1)
        self.assertIsNone(data)

    def test_get_positions_success(self):
        """Test successful retrieval of positions for a valid account."""
        mock_response = Mock(ok=True)
        mock_response.json.return_value = {
            'securitiesAccount': {'positions': [{'symbol': 'AAPL'}]}
        }
        self.mock_client.account_details.return_value = mock_response
        positions = self.adapter.get_positions(self.account_number)
        self.assertEqual(positions[0]['symbol'], 'AAPL')

    def test_get_positions_failure(self):
        """Test positions retrieval fails gracefully for an invalid account."""
        positions = self.adapter.get_positions('invalid_account')
        self.assertIsNone(positions)
        self.mock_client.account_details.assert_not_called()

    def test_place_order_success(self):
        """Test successful placement of an order."""
        mock_response = Mock(ok=True)
        self.mock_client.order_place.return_value = mock_response
        order = {'symbol': 'AAPL', 'quantity': 10, 'instruction': 'BUY'}
        success = self.adapter.place_order(order, self.account_number)
        self.assertTrue(success)
        self.mock_client.order_place.assert_called_once_with(self.hash_value, order)

    def test_place_order_failure(self):
        """Test order placement fails gracefully on API error."""
        mock_response = Mock(ok=False, status_code=400, text='{"message": "A validation error occurred"}')
        self.mock_client.order_place.return_value = mock_response
        order = {'symbol': 'AAPL', 'quantity': 10, 'instruction': 'BUY'}
        success = self.adapter.place_order(order, self.account_number)
        self.assertFalse(success)
        self.mock_client.order_place.assert_called_once_with(self.hash_value, order)

    def test_place_order_invalid_account(self):
        """Test order placement fails gracefully for an invalid account."""
        order = {'symbol': 'AAPL', 'quantity': 10, 'instruction': 'BUY'}
        success = self.adapter.place_order(order, 'invalid_account')
        self.assertFalse(success)
        self.mock_client.order_place.assert_not_called()

if __name__ == '__main__':
    unittest.main()