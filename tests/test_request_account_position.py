import unittest
from unittest import mock
from infrastructure.adapters.account import request_account_positions

class TestRequestAccountPositions(unittest.TestCase):
    
    @mock.patch('schwabdev.Client')
    def test_successful_retrieval(self, mock_client):
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {'positions': [{'symbol': 'AAPL', 'quantity': 10, 'price': 150.0}]}
        mock_client.account_positions.return_value = mock_response
        
        success, positions = request_account_positions(mock_client, 'valid_hash')
        self.assertTrue(success)
        self.assertEqual(positions, [{'symbol': 'AAPL', 'quantity': 10, 'price': 150.0}])
    
    def test_client_none(self):
        with mock.patch('logging.error') as mock_error:
            success, positions = request_account_positions(None, 'valid_hash')
            mock_error.assert_called_with("Client object is None; cannot fetch account positions")
            self.assertFalse(success)
            self.assertIsNone(positions)
    
    def test_invalid_account_hash(self):
        with mock.patch('logging.error') as mock_error:
            success, positions = request_account_positions(mock.Mock(), None)
            mock_error.assert_called_with("Invalid or missing account hash")
            self.assertFalse(success)
            self.assertIsNone(positions)
    
    @mock.patch('schwabdev.Client')
    def test_api_error(self, mock_client):
        mock_response = mock.Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_client.account_positions.return_value = mock_response
        
        with mock.patch('logging.error') as mock_error:
            success, positions = request_account_positions(mock_client, 'valid_hash')
            mock_error.assert_called_with("Failed to fetch account positions: 500 - Internal Server Error")
            self.assertFalse(success)
            self.assertIsNone(positions)
    
    @mock.patch('schwabdev.Client')
    def test_no_positions(self, mock_client):
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {'positions': []}
        mock_client.account_positions.return_value = mock_response
        
        with mock.patch('logging.info') as mock_info:
            success, positions = request_account_positions(mock_client, 'valid_hash')
            mock_info.assert_called_with("No positions found for the account")
            self.assertTrue(success)
            self.assertEqual(positions, [])

if __name__ == '__main__':
    unittest.main()