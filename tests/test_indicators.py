import unittest
from domain.entities.indicators import Indicators  # Adjust import path as needed

class TestIndicators(unittest.TestCase):
    def test_update_and_get(self):
        """Test updating data and retrieving SMA values for 1-minute and 60-minute time frames."""
        timeframe_configs = {
            1: [('SMA', {'period': 3})],    # SMA over 3 minutes for tf=1
            60: [('SMA', {'period': 2})]    # SMA over 2 hours for tf=60
        }
        indicators = Indicators(timeframe_configs, max_history=10)
        
        # Feed 121 minutes of data (t=0 to t=7200 seconds, step=60)
        for n in range(121):  # Minutes 0 to 120 inclusive
            t = n * 60        # Timestamp in seconds
            close = 100 + n   # Close price increases by 1 each minute
            indicators.update_minute_data('AAPL', close, t)
        
        # For tf=60: periods finalize at t=3600 (close at t=3540=159) and t=7200 (close at t=7140=219)
        # closes=[159, 219], SMA(2) = (159 + 219) / 2 = 189
        self.assertEqual(indicators.get_indicator_value('AAPL', 60, 'SMA'), 189)
        
        # For tf=1: last 10 closes (due to max_history=10) are from t=6660 to t=7200
        # Last 3 closes: [218, 219, 220], SMA(3) = (218 + 219 + 220) / 3 = 219
        self.assertEqual(indicators.get_indicator_value('AAPL', 1, 'SMA'), 219)

    def test_insufficient_data(self):
        """Test that SMA returns None with insufficient data and computes correctly when sufficient."""
        timeframe_configs = {1: [('SMA', {'period': 3})]}
        indicators = Indicators(timeframe_configs)
        
        # Feed 1 minute: not enough data for SMA(3)
        indicators.update_minute_data('AAPL', 100, 0)
        self.assertIsNone(indicators.get_indicator_value('AAPL', 1, 'SMA'))
        
        # Feed 2 minutes: still not enough
        indicators.update_minute_data('AAPL', 101, 60)
        self.assertIsNone(indicators.get_indicator_value('AAPL', 1, 'SMA'))
        
        # Feed 3rd minute: now sufficient, SMA = (100 + 101 + 102) / 3 = 101
        indicators.update_minute_data('AAPL', 102, 120)
        self.assertEqual(indicators.get_indicator_value('AAPL', 1, 'SMA'), 101)

    def test_aggregation(self):
        """Test data aggregation and SMA computation for a 60-minute time frame."""
        timeframe_configs = {60: [('SMA', {'period': 2})]}
        indicators = Indicators(timeframe_configs)
        
        # Feed 60 minutes (t=0 to t=3540), constant close
        for n in range(60):  # Minutes 0 to 59
            t = n * 60
            indicators.update_minute_data('AAPL', 100, t)
        # No period finalized yet
        self.assertIsNone(indicators.get_indicator_value('AAPL', 60, 'SMA'))
        
        # Feed t=3600: finalizes first period with close at t=3540=100
        indicators.update_minute_data('AAPL', 100, 3600)
        # Only one close, not enough for SMA(2)
        self.assertIsNone(indicators.get_indicator_value('AAPL', 60, 'SMA'))
        
        # Feed t=3660 to t=7140 with close=101
        for n in range(61, 120):  # Minutes 61 to 119
            t = n * 60
            indicators.update_minute_data('AAPL', 101, t)
        # Second period not finalized yet
        self.assertIsNone(indicators.get_indicator_value('AAPL', 60, 'SMA'))
        
        # Feed t=7200: finalizes second period with close at t=7140=101
        indicators.update_minute_data('AAPL', 101, 7200)
        # closes=[100, 101], SMA(2) = (100 + 101) / 2 = 100.5
        self.assertEqual(indicators.get_indicator_value('AAPL', 60, 'SMA'), 100.5)

    def test_multiple_symbols(self):
        """Test that indicators are computed independently for multiple symbols."""
        timeframe_configs = {1: [('SMA', {'period': 3})]}
        indicators = Indicators(timeframe_configs)
        
        # Feed 3 minutes for two symbols with different closes
        for n in range(3):
            t = n * 60
            indicators.update_minute_data('AAPL', 100 + n, t)  # 100, 101, 102
            indicators.update_minute_data('GOOG', 200 + n, t)  # 200, 201, 202
        
        # AAPL: SMA(3) = (100 + 101 + 102) / 3 = 101
        self.assertEqual(indicators.get_indicator_value('AAPL', 1, 'SMA'), 101)
        # GOOG: SMA(3) = (200 + 201 + 202) / 3 = 201
        self.assertEqual(indicators.get_indicator_value('GOOG', 1, 'SMA'), 201)

    def test_no_data(self):
        """Test that get_indicator_value returns None for a symbol with no data."""
        timeframe_configs = {1: [('SMA', {'period': 3})]}
        indicators = Indicators(timeframe_configs)
        self.assertIsNone(indicators.get_indicator_value('AAPL', 1, 'SMA'))

if __name__ == '__main__':
    unittest.main()