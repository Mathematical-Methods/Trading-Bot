import unittest
from unittest.mock import Mock, patch
import logging
from account import fetch_account_hash

class TestFetchAccountHash(unittest.TestCase):
    
    def setUp(self):
        # Clear logging handlers to avoid interference
        logging.getLogger().handlers = []
        logging.basicConfig(level=logging.INFO)
    
    def test_simulation_mode(self):
        # Arrange
        client = Mock()  # Client won't be used
        simulate = True
        
        # Act
        with self.assertLogs(level='INFO') as log:
            success, account_hash = fetch_account_hash(client, simulate)
        
        # Assert
        self.assertTrue(success)
        self.assertIsNone(account_hash)
        self.assertIn("Simulation mode enabled; no account hash retrieved", log.output[-1])
    
    def test_none_client(self):
        # Arrange
        client = None
        simulate = False
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, account_hash = fetch_account_hash(client, simulate)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(account_hash)
        self.assertIn("Client object is None; cannot fetch account hash", log.output[-1])
    
    def test_successful_fetch(self):
        # Arrange
        client = Mock()
        client.account_linked.return_value = Mock(
            ok=True,
            json=lambda: [{"hashValue": "test_hash_123"}]
        )
        simulate = False
        
        # Act
        with self.assertLogs(level='INFO') as log:
            success, account_hash = fetch_account_hash(client, simulate)
        
        # Assert
        self.assertTrue(success)
        self.assertEqual(account_hash, "test_hash_123")
        client.account_linked.assert_called_once()
        self.assertIn("Account hash retrieved successfully: test_hash_123", log.output[-1])
    
    def test_failed_response(self):
        # Arrange
        client = Mock()
        client.account_linked.return_value = Mock(
            ok=False,
            status_code=403,
            text="Forbidden"
        )
        simulate = False
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, account_hash = fetch_account_hash(client, simulate)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(account_hash)
        self.assertIn("Failed to fetch linked accounts: 403 - Forbidden", log.output[-1])
    
    def test_invalid_response_format(self):
        # Arrange
        client = Mock()
        client.account_linked.return_value = Mock(
            ok=True,
            json=lambda: [{}]  # No 'hashValue' key
        )
        simulate = False
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, account_hash = fetch_account_hash(client, simulate)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(account_hash)
        self.assertIn("No accounts found or invalid response format", log.output[-1])
    
    def test_exception_during_fetch(self):
        # Arrange
        client = Mock()
        client.account_linked.side_effect = Exception("Network error")
        simulate = False
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, account_hash = fetch_account_hash(client, simulate)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(account_hash)
        self.assertIn("Exception while fetching account hash: Network error", log.output[-1])

if __name__ == '__main__':
    unittest.main()