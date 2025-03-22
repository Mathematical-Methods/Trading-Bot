import unittest
from unittest.mock import Mock, patch
import logging
from infrastructure.adapters.account import fetch_account_hash, request_account_details

class TestAccount(unittest.TestCase):
    
    def setUp(self):
        # Clear logging handlers to avoid interference
        logging.getLogger().handlers = []
        logging.basicConfig(level=logging.INFO)
    
    # Existing tests for fetch_account_hash
    def test_simulation_mode(self):
        client = Mock()
        simulate = True
        with self.assertLogs(level='INFO') as log:
            success, account_hash = fetch_account_hash(client, simulate)
        self.assertTrue(success)
        self.assertIsNone(account_hash)
        self.assertIn("Simulation mode enabled; no account hash retrieved", log.output[-1])
    
    def test_none_client_fetch(self):
        client = None
        simulate = False
        with self.assertLogs(level='ERROR') as log:
            success, account_hash = fetch_account_hash(client, simulate)
        self.assertFalse(success)
        self.assertIsNone(account_hash)
        self.assertIn("Client object is None; cannot fetch account hash", log.output[-1])
    
    def test_successful_fetch(self):
        client = Mock()
        client.account_linked.return_value = Mock(
            ok=True,
            json=lambda: [{"hashValue": "test_hash_123"}]
        )
        simulate = False
        with self.assertLogs(level='INFO') as log:
            success, account_hash = fetch_account_hash(client, simulate)
        self.assertTrue(success)
        self.assertEqual(account_hash, "test_hash_123")
        client.account_linked.assert_called_once()
        self.assertIn("Account hash retrieved successfully: test_hash_123", log.output[-1])
    
    def test_failed_response(self):
        client = Mock()
        client.account_linked.return_value = Mock(
            ok=False,
            status_code=403,
            text="Forbidden"
        )
        simulate = False
        with self.assertLogs(level='ERROR') as log:
            success, account_hash = fetch_account_hash(client, simulate)
        self.assertFalse(success)
        self.assertIsNone(account_hash)
        self.assertIn("Failed to fetch linked accounts: 403 - Forbidden", log.output[-1])
    
    def test_invalid_response_format(self):
        client = Mock()
        client.account_linked.return_value = Mock(
            ok=True,
            json=lambda: [{}]
        )
        simulate = False
        with self.assertLogs(level='ERROR') as log:
            success, account_hash = fetch_account_hash(client, simulate)
        self.assertFalse(success)
        self.assertIsNone(account_hash)
        self.assertIn("No accounts found or invalid response format", log.output[-1])
    
    def test_exception_during_fetch(self):
        client = Mock()
        client.account_linked.side_effect = Exception("Network error")
        simulate = False
        with self.assertLogs(level='ERROR') as log:
            success, account_hash = fetch_account_hash(client, simulate)
        self.assertFalse(success)
        self.assertIsNone(account_hash)
        self.assertIn("Exception while fetching account hash: Network error", log.output[-1])
    
    # New tests for request_account_details
    def test_successful_account_details(self):
        # Arrange
        client = Mock()
        client.account_details.return_value = Mock(
            ok=True,
            json=lambda: {"cashBalance": 5000.0, "accountNumber": "12345"}
        )
        account_hash = "test_hash_123"
        
        # Act
        with self.assertLogs(level='INFO') as log:
            success, details = request_account_details(client, account_hash)
        
        # Assert
        self.assertTrue(success)
        self.assertEqual(details, {"cashBalance": 5000.0, "accountNumber": "12345"})
        client.account_details.assert_called_once_with(account_hash)
        self.assertIn("Account details retrieved successfully for hash: test_hash_123", log.output[-1])
    
    def test_none_client_details(self):
        # Arrange
        client = None
        account_hash = "test_hash_123"
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, details = request_account_details(client, account_hash)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(details)
        self.assertIn("Client object is None; cannot fetch account details", log.output[-1])
    
    def test_invalid_account_hash(self):
        # Arrange
        client = Mock()
        account_hash = None
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, details = request_account_details(client, account_hash)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(details)
        self.assertIn("Invalid or missing account hash", log.output[-1])
    
    def test_failed_details_response(self):
        # Arrange
        client = Mock()
        client.account_details.return_value = Mock(
            ok=False,
            status_code=404,
            text="Not Found"
        )
        account_hash = "test_hash_123"
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, details = request_account_details(client, account_hash)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(details)
        self.assertIn("Failed to fetch account details: 404 - Not Found", log.output[-1])
    
    def test_empty_details_response(self):
        # Arrange
        client = Mock()
        client.account_details.return_value = Mock(
            ok=True,
            json=lambda: {}
        )
        account_hash = "test_hash_123"
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, details = request_account_details(client, account_hash)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(details)
        self.assertIn("Empty account details response", log.output[-1])
    
    def test_exception_during_details_fetch(self):
        # Arrange
        client = Mock()
        client.account_details.side_effect = Exception("API error")
        account_hash = "test_hash_123"
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, details = request_account_details(client, account_hash)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(details)
        self.assertIn("Exception while fetching account details: API error", log.output[-1])

if __name__ == '__main__':
    unittest.main()