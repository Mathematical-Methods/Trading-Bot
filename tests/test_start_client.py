import unittest
from unittest.mock import patch, Mock
import logging
from infrastructure.adapters.start_client import start_client

class TestStartClient(unittest.TestCase):
    
    def setUp(self):
        # Clear logging handlers to avoid interference
        logging.getLogger().handlers = []
        logging.basicConfig(level=logging.INFO)
    
    @patch('schwabdev.Client')
    def test_successful_initialization(self, mock_client_class):
        # Arrange
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance
        app_key = "test_key"
        app_secret = "test_secret"
        callback_url = "http://test.com"
        
        # Act
        with self.assertLogs(level='INFO') as log:
            success, client = start_client(app_key, app_secret, callback_url)
        
        # Assert
        self.assertTrue(success)
        self.assertEqual(client, mock_client_instance)
        mock_client_class.assert_called_once_with(app_key, app_secret, callback_url)
        self.assertIn("Schwab client initialized successfully", log.output[-1])
    
    def test_missing_credentials(self):
        # Arrange
        app_key = "test_key"
        app_secret = None  # Missing secret
        callback_url = "http://test.com"
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, client = start_client(app_key, app_secret, callback_url)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(client)
        self.assertIn("One or more client credentials are missing", log.output[-1])
    
    @patch('schwabdev.Client')
    def test_initialization_exception(self, mock_client_class):
        # Arrange
        mock_client_class.side_effect = Exception("Network error")
        app_key = "test_key"
        app_secret = "test_secret"
        callback_url = "http://test.com"
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, client = start_client(app_key, app_secret, callback_url)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(client)
        self.assertIn("Failed to initialize Schwab client: Network error", log.output[-1])

if __name__ == '__main__':
    unittest.main()