from collections import deque
import logging

class Indicators:
    def __init__(self, timeframe_configs, max_history=100):
        """
        Initializes the Indicators class with time frame configurations.

        Args:
            timeframe_configs (dict): Dictionary where keys are time frames in minutes (int),
                                      and values are lists of tuples (indicator_name, params_dict).
                                      Example: {1: [('RSI', {'period': 14})], 60: [('SMA', {'period': 10})]}
            max_history (int): Maximum number of historical closes to keep per time frame.
        """
        self.timeframe_configs = timeframe_configs
        self.max_history = max_history
        self.data = {}  # Structure: {symbol: {tf: {'closes': deque, 'indicators': {name: value}, ...}}}

    def update_minute_data(self, symbol, close, timestamp):
        # Initialize data structure for new symbol
        if symbol not in self.data:
            self.data[symbol] = {}
            for tf in self.timeframe_configs:
                self.data[symbol][tf] = {
                    'closes': deque(maxlen=self.max_history),
                    'indicators': {ind[0]: None for ind in self.timeframe_configs[tf]},
                    'current_period_start': None,
                    'minute_closes_in_period': []
                }

        # Process each configured timeframe, skipping aggregation for tf=1
        for tf in self.timeframe_configs:
            if tf == 1:
                continue  # Skip aggregation logic for tf=1
            tf_data = self.data[symbol][tf]
            period_length = tf * 60
            period_start = (timestamp // period_length) * period_length
            if tf_data['current_period_start'] is None or period_start > tf_data['current_period_start']:
                if tf_data['minute_closes_in_period']:
                    period_close = tf_data['minute_closes_in_period'][-1]
                    tf_data['closes'].append(period_close)
                    self._compute_indicators(symbol, tf)
                tf_data['current_period_start'] = period_start
                tf_data['minute_closes_in_period'] = [close]
            else:
                tf_data['minute_closes_in_period'].append(close)

        # Special handling for tf=1
        if 1 in self.timeframe_configs:
            self.data[symbol][1]['closes'].append(close)
            self._compute_indicators(symbol, 1)

    def _compute_indicators(self, symbol, tf):
        """
        Computes indicators for a given symbol and time frame using accumulated closes.

        Args:
            symbol (str): Stock symbol.
            tf (int): Time frame in minutes.
        """
        tf_data = self.data[symbol][tf]
        closes = list(tf_data['closes'])
        for indicator_name, params in self.timeframe_configs[tf]:
            period = params.get('period')
            if period and len(closes) >= period:
                if indicator_name == 'RSI':
                    value = self.calculate_rsi(closes, period)
                elif indicator_name == 'SMA':
                    value = self.calculate_sma(closes, period)
                else:
                    logging.warning(f"Unsupported indicator: {indicator_name}")
                    value = None
                tf_data['indicators'][indicator_name] = value
            else:
                tf_data['indicators'][indicator_name] = None

    def get_indicator_value(self, symbol, timeframe, indicator_name):
        """
        Retrieves the current value of a specified indicator for a symbol and time frame.

        Args:
            symbol (str): Stock symbol.
            timeframe (int): Time frame in minutes.
            indicator_name (str): Name of the indicator (e.g., 'RSI', 'SMA').

        Returns:
            float or None: Current indicator value, or None if not available.
        """
        if symbol in self.data and timeframe in self.data[symbol]:
            indicators = self.data[symbol][timeframe]['indicators']
            return indicators.get(indicator_name)
        return None

    def calculate_rsi(self, closes, period):
        """
        Calculates the Relative Strength Index (RSI) for the given closing prices.

        Args:
            closes (list): List of closing prices.
            period (int): Number of periods for RSI calculation.

        Returns:
            float: RSI value, or None if insufficient data.
        """
        if len(closes) < period + 1:
            return None

        # Calculate price differences
        diffs = [closes[i] - closes[i - 1] for i in range(1, len(closes))]

        # Initialize average gain and loss
        avg_gain = sum(d for d in diffs[:period] if d > 0) / period
        avg_loss = -sum(d for d in diffs[:period] if d < 0) / period

        # Update averages for subsequent periods
        for i in range(period, len(diffs)):
            gain = diffs[i] if diffs[i] > 0 else 0
            loss = -diffs[i] if diffs[i] < 0 else 0
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period

        # Calculate RSI
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_sma(self, closes, period):
        """
        Calculates the Simple Moving Average (SMA) for the given closing prices.

        Args:
            closes (list): List of closing prices.
            period (int): Number of periods for SMA calculation.

        Returns:
            float: SMA value, or None if insufficient data.
        """
        if len(closes) < period:
            return None
        return sum(closes[-period:]) / period