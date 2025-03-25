import json
import os
import threading
import time
import logging

# Mock Response class to mimic requests.Response for price_history
class MockResponse:
    def __init__(self, ok, data):
        self.ok = ok
        self._data = data

    def json(self):
        return self._data

class SimulatedStream:
    def __init__(self, data_path="./Automated_Trading_retry/Data Collection/stock_data/"):
        """Initialize the simulated stream with the path to the data directory."""
        self.data_path = data_path
        self.subscriptions = {}  # Tracks subscribed services and tickers: {service: {ticker: fields}}
        self.data_iterators = {}  # Maps tickers to iterators over their candle data
        self.receiver = None     # Function to receive simulated messages
        self.active = False      # Flag to control the simulation loop
        self.thread = None       # Background thread for simulation
        self.logger = logging.getLogger('SimulatedStream')
        if not self.logger.handlers:
            self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)

    def start(self, receiver, daemon=True):
        """Start the simulated stream in a background thread."""
        self.receiver = receiver
        self.active = True
        self.thread = threading.Thread(target=self._simulate_stream, daemon=daemon)
        self.thread.start()
        self.logger.info("Simulated stream started")

    def stop(self):
        """Stop the simulated stream."""
        self.active = False
        if self.thread:
            self.thread.join()
        self.logger.info("Simulated stream stopped")

    def _simulate_stream(self):
        """Background thread loop to simulate streaming data."""
        while self.active:
            for ticker in list(self.data_iterators.keys()):
                try:
                    candle = next(self.data_iterators[ticker])
                    message = self._construct_message(ticker, candle)
                    if self.receiver:
                        self.receiver(json.dumps(message))
                except StopIteration:
                    self.logger.info(f"No more data for {ticker}, unsubscribing")
                    del self.data_iterators[ticker]
            time.sleep(0.1)  # Simulate real-time with a 0.1-second delay

    def _construct_message(self, ticker, candle):
        """Construct a message mimicking Schwab's CHART_EQUITY stream format."""
        content = {
            "key": ticker,
            "1": candle["open"],
            "2": candle["high"],
            "3": candle["low"],
            "4": candle["close"],
            "5": candle["volume"],
            "7": candle["datetime"]
        }
        message = {
            "data": [
                {
                    "service": "CHART_EQUITY",
                    "timestamp": candle["datetime"],
                    "command": "SUBS",
                    "content": [content]
                }
            ]
        }
        return message

    def send(self, requests):
        """Handle subscription requests, starting or stopping data iterators."""
        if not isinstance(requests, list):
            requests = [requests]
        for request in requests:
            self._record_request(request)
            service = request.get("service")
            command = request.get("command")
            if service == "CHART_EQUITY":
                if command in ["ADD", "SUBS"]:
                    keys = request["parameters"]["keys"].split(",")
                    for ticker in keys:
                        if ticker not in self.data_iterators:
                            self._start_iterator(ticker)
                elif command == "UNSUBS":
                    keys = request["parameters"]["keys"].split(",")
                    for ticker in keys:
                        if ticker in self.data_iterators:
                            del self.data_iterators[ticker]

    def _start_iterator(self, ticker):
        """Load candle data for a ticker and start an iterator."""
        file_path = os.path.join(self.data_path, f"{ticker}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    candles = json.load(f)
                self.data_iterators[ticker] = iter(candles)
                self.logger.info(f"Started iterator for {ticker}")
            except json.JSONDecodeError:
                self.logger.error(f"Invalid JSON in {ticker}.json")
        else:
            self.logger.error(f"Data file for {ticker} not found at {file_path}")

    def chart_equity(self, keys, fields, command="ADD"):
        """Create a CHART_EQUITY subscription request dictionary."""
        return {
            "service": "CHART_EQUITY",
            "command": command,
            "parameters": {
                "keys": keys,    # Comma-separated ticker symbols
                "fields": fields # Comma-separated field numbers
            }
        }

    def price_history(self, symbol, **kwargs):
        """Retrieve historical data for a symbol from its JSON file."""
        file_path = os.path.join(self.data_path, f"{symbol}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    candles = json.load(f)
                return MockResponse(True, {"candles": candles})
            except json.JSONDecodeError:
                return MockResponse(False, {"error": "Invalid JSON format"})
        else:
            return MockResponse(False, {"error": f"Data not found for {symbol}"})

    def _record_request(self, request):
        """Update the subscriptions dictionary based on the request."""
        service = request.get("service")
        command = request.get("command")
        parameters = request.get("parameters", {})
        keys = parameters.get("keys", "").split(",")
        fields = parameters.get("fields", "").split(",")
        if service not in self.subscriptions:
            self.subscriptions[service] = {}
        if command in ["ADD", "SUBS"]:
            for key in keys:
                if key:
                    if key not in self.subscriptions[service]:
                        self.subscriptions[service][key] = fields
                    else:
                        # Merge fields if ticker already subscribed
                        self.subscriptions[service][key] = list(
                            set(self.subscriptions[service][key]) | set(fields)
                        )
        elif command == "UNSUBS":
            for key in keys:
                if key in self.subscriptions[service]:
                    del self.subscriptions[service][key]
            if not self.subscriptions[service]:
                del self.subscriptions[service]