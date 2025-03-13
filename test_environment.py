import os
import logging
import unittest
from unittest.mock import patch
from environment import initialize_environment

class TestInitializeEnvironment(unittest.TestCase):
    
    def setUp(self):
        # Clear any existing logging handlers to avoid interference
        logging.getLogger().handlers = []
    
    @patch('os.getenv')
    @patch('dotenv.load_dotenv')
    def test_successful_initialization(self, mock_load_dotenv, mock_getenv):
        # Arrange
        mock_load_dotenv.return_value = True
        mock_getenv.side_effect = lambda key: {
            'app_key': 'test_key',
            'app_secret': 'test_secret',
            'callback_url': 'http://test.com'
        }.get(key)
        
        # Act
        success, env_vars = initialize_environment()
        
        # Assert
        self.assertTrue(success)
        self.assertEqual(env_vars, {
            'app_key': 'test_key',
            'app_secret': 'test_secret',
            'callback_url': 'http://test.com'
        })
        self.assertEqual(logging.getLogger().level, logging.INFO)
    
    @patch('os.getenv')
    @patch('dotenv.load_dotenv')
    def test_missing_variables(self, mock_load_dotenv, mock_getenv):
        # Arrange
        mock_load_dotenv.return_value = True
        mock_getenv.side_effect = lambda key: {
            'app_key': 'test_key',
            'app_secret': None,  # Missing variable
            'callback_url': 'http://test.com'
        }.get(key)
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, env_vars = initialize_environment()
        
        # Assert
        self.assertFalse(success)
        self.assertIn('app_secret', env_vars)
        self.assertIsNone(env_vars['app_secret'])
        self.assertIn("Missing required environment variables", log.output[0])
    
    @patch('os.getenv')
    @patch('dotenv.load_dotenv')
    def test_dotenv_failure(self, mock_load_dotenv, mock_getenv):
        # Arrange
        mock_load_dotenv.return_value = False
        mock_getenv.return_value = None  # Simulate no variables in environment
        
        # Act
        success, env_vars = initialize_environment()
        
        # Assert
        self.assertFalse(success)  # Should fail due to missing variables
        self.assertIsNone(env_vars['app_key'])
        self.assertIsNone(env_vars['app_secret'])
        self.assertIsNone(env_vars['callback_url'])

if __name__ == '__main__':
    unittest.main()