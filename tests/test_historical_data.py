import unittest
from unittest import mock

# Assuming Indicators class is defined in domain.indicators
from domain.entities.indicators import Indicators
from infrastructure.adapters.historical_data import load_initial_historical_data

class TestLoadInitialHistoricalData(unittest.TestCase):
    
    @mock.patch('schwabdev.Client')
    @mock.patch('domain.entities.indicators.Indicators')
    def test_successful_loading(self, mock_indicators, mock_client):
        # Mock API response with two candles for each symbol
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'candles': [
                {'close': 100.0, 'volume': 1000, 'datetime': 1609459200000},
                {'close': 101.0, 'volume': 1100, 'datetime': 1609459260000}
            ]
        }
        mock_client.price_history.return_value = mock_response
        
        # Mock Indicators instance
        mock_indicators_instance = mock_indicators.return_value
        
        # Call the function with two symbols
        success = load_initial_historical_data(mock_client, ["AAPL", "GOOG"], mock_indicators_instance)
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(mock_client.price_history.call_count, 2)
        self.assertEqual(mock_indicators_instance.update_minute_data.call_count, 4)  # 2 candles per symbol
        mock_indicators_instance.update_minute_data.assert_any_call("AAPL", 100.0, 1000, 1609459200000)
        mock_indicators_instance.update_minute_data.assert_any_call("AAPL", 101.0, 1100, 1609459260000)
        mock_indicators_instance.update_minute_data.assert_any_call("GOOG", 100.0, 1000, 1609459200000)
        mock_indicators_instance.update_minute_data.assert_any_call("GOOG", 101.0, 1100, 1609459260000)
    
    @mock.patch('schwabdev.Client')
    @mock.patch('domain.entities.indicators.Indicators')
    def test_api_error(self, mock_indicators, mock_client):
        # Mock API response: success for AAPL, error for GOOG
        mock_response_aapl = mock.Mock()
        mock_response_aapl.ok = True
        mock_response_aapl.json.return_value = {'candles': [{'close': 100.0, 'volume': 1000, 'datetime': 1609459200000}]}
        mock_response_goog = mock.Mock()
        mock_response_goog.ok = False
        mock_response_goog.status_code = 500
        mock_response_goog.text = "Internal Server Error"
        mock_client.price_history.side_effect = [mock_response_aapl, mock_response_goog]
        
        # Call the function
        success = load_initial_historical_data(mock_client, ["AAPL", "GOOG"], mock_indicators.return_value)
        
        # Assertions
        self.assertFalse(success)
        self.assertEqual(mock_client.price_history.call_count, 2)
        self.assertEqual(mock_indicators.return_value.update_minute_data.call_count, 1)  # Only AAPL's candle
    
    @mock.patch('schwabdev.Client')
    @mock.patch('domain.entities.indicators.Indicators')
    def test_empty_symbols(self, mock_indicators, mock_client):
        # Call with an empty symbols list
        success = load_initial_historical_data(mock_client, [], mock_indicators.return_value)
        
        # Assertions
        self.assertTrue(success)
        mock_client.price_history.assert_not_called()
        mock_indicators.return_value.update_minute_data.assert_not_called()
    
    @mock.patch('schwabdev.Client')
    @mock.patch('domain.entities.indicators.Indicators')
    def test_no_candles(self, mock_indicators, mock_client):
        # Mock API response with no candles
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {'candles': []}
        mock_client.price_history.return_value = mock_response
        
        # Call the function
        success = load_initial_historical_data(mock_client, ["AAPL"], mock_indicators.return_value)
        
        # Assertions
        self.assertTrue(success)  # Still True, as no data is not an error
        mock_indicators.return_value.update_minute_data.assert_not_called()

if __name__ == '__main__':
    unittest.main()