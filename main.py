import schwabdev
import os
import logging
import json
import zoneinfo
import datetime
from dotenv import load_dotenv
from time import sleep
from time import time
from collections import deque
import math

# Define the Indicators class
class Indicators:
    def __init__(self):
        """
        Initialize the Indicators class with dictionaries to store data per symbol.
        """
        self.current_hour = {}       # {symbol: datetime of current hour start}
        self.accum_volume = {}       # {symbol: float, accumulated volume}
        self.last_close = {}         # {symbol: float, last close price}
        self.hourly_data = {}        # {symbol: list of (close, volume, timestamp)}
        self.indicators = {}         # {symbol: dict of indicator values}
        self.ema_values = {}         # {symbol: {period: float}}

    def update_minute_data(self, symbol, close, volume, timestamp):
        """
        Aggregate minute-level data into hourly data and update indicators when a new hour starts.

        Args:
            symbol (str): Stock symbol.
            close (float): Closing price for the minute.
            volume (float): Volume for the minute.
            timestamp (int): Timestamp in milliseconds since epoch.

        Returns:
            bool: True if a new hour’s indicators were calculated, False otherwise.
        """
        dt = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        hour_start = dt.replace(minute=0, second=0, microsecond=0)
        if symbol not in self.current_hour or self.current_hour[symbol] != hour_start:
            # New hour detected, finalize previous hour if it exists
            if symbol in self.current_hour:
                hourly_close = self.last_close[symbol]
                hourly_volume = self.accum_volume[symbol]
                if symbol not in self.hourly_data:
                    self.hourly_data[symbol] = []
                self.hourly_data[symbol].append((hourly_close, hourly_volume, self.current_hour[symbol]))
                self.calculate_indicators(symbol)
            # Start new hour
            self.current_hour[symbol] = hour_start
            self.accum_volume[symbol] = volume
            self.last_close[symbol] = close
            return True  # Indicators updated for the new hour
        else:
            # Same hour, accumulate volume and update last close
            self.accum_volume[symbol] += volume
            self.last_close[symbol] = close
            return False

    def calculate_indicators(self, symbol):
        """
        Calculate all technical indicators for the symbol based on hourly data.
        """
        if symbol not in self.indicators:
            self.indicators[symbol] = {
                'ma_short_history': [],    # Last 2 short MAs (10-period)
                'ma_long_history': [],     # Last 2 long MAs (20-period)
                'rsi_history': [],         # Last RSI value (14-period)
                'macd_history': [],        # Last 5 (macd_line, signal_line) tuples
                'bollinger_history': [],   # Last Bollinger Bands tuple
                'volume_history': []       # Last 6 hourly volumes
            }

        # Moving Averages (10 and 20 periods)
        ma_short = self.calculate_SMA(symbol, 10)
        ma_long = self.calculate_SMA(symbol, 20)
        if ma_short is not None and ma_long is not None:
            self.indicators[symbol]['ma_short_history'].append(ma_short)
            self.indicators[symbol]['ma_long_history'].append(ma_long)
            if len(self.indicators[symbol]['ma_short_history']) > 2:
                self.indicators[symbol]['ma_short_history'].pop(0)
                self.indicators[symbol]['ma_long_history'].pop(0)

        # RSI (14 periods)
        rsi = self.calculate_RSI(symbol, 14)
        if rsi is not None:
            self.indicators[symbol]['rsi_history'].append(rsi)
            if len(self.indicators[symbol]['rsi_history']) > 1:
                self.indicators[symbol]['rsi_history'].pop(0)

        # MACD (12, 26, 9)
        macd_line, signal_line = self.calculate_MACD(symbol)
        if macd_line is not None and signal_line is not None:
            self.indicators[symbol]['macd_history'].append((macd_line, signal_line))
            if len(self.indicators[symbol]['macd_history']) > 5:
                self.indicators[symbol]['macd_history'].pop(0)

        # Bollinger Bands (20 periods, 2 std deviations)
        bollinger = self.calculate_Bollinger_Bands(symbol, 20, 2)
        if bollinger[0] is not None:
            self.indicators[symbol]['bollinger_history'].append(bollinger)
            if len(self.indicators[symbol]['bollinger_history']) > 1:
                self.indicators[symbol]['bollinger_history'].pop(0)

        # Volume
        hourly_volume = self.hourly_data[symbol][-1][1]
        self.indicators[symbol]['volume_history'].append(hourly_volume)
        if len(self.indicators[symbol]['volume_history']) > 6:
            self.indicators[symbol]['volume_history'].pop(0)

    def calculate_SMA(self, symbol, length):
        """
        Calculate Simple Moving Average over the last 'length' hourly closes.
        """
        if symbol in self.hourly_data and len(self.hourly_data[symbol]) >= length:
            closes = [close for close, _, _ in self.hourly_data[symbol][-length:]]
            return sum(closes) / length
        return None

    def calculate_RSI(self, symbol, length=14):
        """
        Calculate RSI over the last 'length' hourly closes.
        """
        if symbol not in self.hourly_data or len(self.hourly_data[symbol]) < length + 1:
            return None
        closes = [close for close, _, _ in self.hourly_data[symbol][-length-1:]]
        gains, losses = [], []
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
            else:
                losses.append(-change)
        if not gains:
            return 0.0
        if not losses:
            return 100.0
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses) if losses else 0
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_EMA(self, symbol, period):
        """
        Calculate Exponential Moving Average for a given period.
        """
        alpha = 2 / (period + 1)
        if symbol not in self.ema_values:
            self.ema_values[symbol] = {}
        if period not in self.ema_values[symbol]:
            if len(self.hourly_data[symbol]) >= period:
                closes = [close for close, _, _ in self.hourly_data[symbol][:period]]
                self.ema_values[symbol][period] = sum(closes) / period
            else:
                return None
        prev_ema = self.ema_values[symbol][period]
        new_close = self.hourly_data[symbol][-1][0]
        new_ema = (new_close - prev_ema) * alpha + prev_ema
        self.ema_values[symbol][period] = new_ema
        return new_ema

    def calculate_MACD(self, symbol):
        """
        Calculate MACD line and signal line (12, 26, 9).
        """
        ema_fast = self.calculate_EMA(symbol, 12)
        ema_slow = self.calculate_EMA(symbol, 26)
        if ema_fast is None or ema_slow is None:
            return None, None
        macd_line = ema_fast - ema_slow
        if 'signal_line' not in self.ema_values[symbol]:
            if len(self.hourly_data[symbol]) >= 35:  # 26 + 9 periods
                closes = [close for close, _, _ in self.hourly_data[symbol][-35:-9]]
                macd_series = [self.calculate_EMA(symbol, 12) - self.calculate_EMA(symbol, 26) for _ in closes]
                self.ema_values[symbol]['signal_line'] = sum(macd_series) / 9  # Initial SMA
            else:
                return macd_line, None
        prev_signal = self.ema_values[symbol]['signal_line']
        alpha = 2 / (9 + 1)
        signal_line = (macd_line - prev_signal) * alpha + prev_signal
        self.ema_values[symbol]['signal_line'] = signal_line
        return macd_line, signal_line

    def calculate_Bollinger_Bands(self, symbol, period=20, std_dev=2):
        """
        Calculate Bollinger Bands over the last 'period' hourly closes.
        """
        if symbol not in self.hourly_data or len(self.hourly_data[symbol]) < period:
            return None, None, None
        closes = [close for close, _, _ in self.hourly_data[symbol][-period:]]
        middle_band = sum(closes) / period
        variance = sum((x - middle_band) ** 2 for x in closes) / period
        std = math.sqrt(variance)
        upper_band = middle_band + std_dev * std
        lower_band = middle_band - std_dev * std
        return upper_band, middle_band, lower_band

# Initialize Indicators class
indicators = Indicators()

# Shared list for streamer messages
shared_list = []

class Portfolio:
    def __init__(self, initial_cash=100000.0):
        """
        Initialize the simulated portfolio.
        """
        self.cash = initial_cash
        self.positions = {}  # {symbol: {'quantity': int, 'entry_price': float}}
        self.realized_gains_losses = []

    def buy(self, symbol, price, quantity):
        cost = price * quantity
        if self.cash >= cost:
            if symbol in self.positions:
                current_quantity = self.positions[symbol]['quantity']
                current_entry = self.positions[symbol]['entry_price']
                new_quantity = current_quantity + quantity
                new_entry = (current_entry * current_quantity + price * quantity) / new_quantity
                self.positions[symbol] = {'quantity': new_quantity, 'entry_price': new_entry}
            else:
                self.positions[symbol] = {'quantity': quantity, 'entry_price': price}
            self.cash -= cost
            logging.info(f"[SIM] Bought {quantity} shares of {symbol} at {price}, Cost: {cost:.2f}, Cash: {self.cash:.2f}")
        else:
            logging.warning(f"Insufficient cash to buy {quantity} shares of {symbol}")

    def sell(self, symbol, price, quantity):
        if symbol in self.positions and self.positions[symbol]['quantity'] >= quantity:
            position = self.positions[symbol]
            entry_price = position['entry_price']
            profit_loss = (price - entry_price) * quantity
            self.cash += price * quantity
            self.realized_gains_losses.append(profit_loss)
            position['quantity'] -= quantity
            if position['quantity'] == 0:
                del self.positions[symbol]
            logging.info(f"[SIM] Sold {quantity} shares of {symbol} at {price}, P/L: {profit_loss:.2f}, Cash: {self.cash:.2f}")
        else:
            logging.warning(f"No/insufficient position to sell {quantity} shares of {symbol}")

    def get_position(self, symbol):
        return self.positions.get(symbol)

    def report_gains_losses(self):
        total_gains_losses = sum(self.realized_gains_losses)
        logging.info(f"[Portfolio Report] Total Realized Gains/Losses: {total_gains_losses:.2f}, Cash: {self.cash:.2f}")

def response_handler(message):
    """Append incoming streamer messages to the shared list."""
    shared_list.append(message)

def has_macd_crossover(macdhistory, direction="above"):
    """
    Check if MACD crossed the signal line in the specified direction within the last 2-4 hours.
    """
    if len(macdhistory) < 2:
        return False
    for i in range(1, min(4, len(macdhistory))):  # Check last 2-4 periods
        prev_macd, prev_signal = macdhistory[-i-1]
        curr_macd, curr_signal = macdhistory[-i]
        if direction == "above" and prev_macd <= prev_signal and curr_macd > curr_signal:
            return True
        elif direction == "below" and prev_macd >= prev_signal and curr_macd < curr_signal:
            return True
    return False

def buyCondition(symbol, indicators):
    """
    Determine trading action based on the intraday swing trading strategy.

    Args:
        symbol (str): Stock symbol.
        indicators (Indicators): Instance of Indicators class.

    Returns:
        str: "buy", "sell", or "hold"
    """
    ind = indicators.indicators.get(symbol, {})
    if not ind or len(ind['ma_short_history']) < 2:
        return "hold"

    # MA Crossover
    ma_short_prev = ind['ma_short_history'][-2]
    ma_long_prev = ind['ma_long_history'][-2]
    ma_short_current = ind['ma_short_history'][-1]
    ma_long_current = ind['ma_long_history'][-1]
    ma_cross_up = ma_short_prev <= ma_long_prev and ma_short_current > ma_long_current
    ma_cross_down = ma_short_prev >= ma_long_prev and ma_short_current < ma_long_current

    # RSI
    rsi = ind['rsi_history'][-1] if ind['rsi_history'] else None
    rsi_buy = rsi is not None and rsi < 70
    rsi_sell = rsi is not None and rsi > 70

    # MACD Crossover
    macd_history = ind['macd_history']
    macd_buy = has_macd_crossover(macd_history, "above")
    macd_sell = has_macd_crossover(macd_history, "below")

    # Bollinger Bands (not too wide: width < 10% of middle band)
    bollinger = ind['bollinger_history'][-1] if ind['bollinger_history'] else (None, None, None)
    bollinger_condition = False
    if bollinger[0] is not None:
        upper, middle, lower = bollinger
        band_width = (upper - lower) / middle
        bollinger_condition = band_width < 0.1

    # Volume (greater than last 5 hours)
    volume_history = ind['volume_history']
    volume_condition = False
    if len(volume_history) >= 6:
        current_volume = volume_history[-1]
        volume_condition = all(current_volume > v for v in volume_history[-6:-1])

    # Buy Condition
    if ma_cross_up and rsi_buy and macd_buy and bollinger_condition and volume_condition:
        return "buy"
    # Sell Condition
    if ma_cross_down and rsi_sell and macd_sell and bollinger_condition:
        return "sell"
    return "hold"

def stockTrader(service, client, simulate, portfolio, indicators):
    """
    Process CHART_EQUITY data and execute trades based on conditions.
    """
    contents = service.get("content", [])
    for content in contents:
        symbol = content.get("key", "NO KEY")
        close_price = content.get("4")  # Close price
        volume = content.get("5")       # Assuming volume is field "5"
        timestamp = content.get("7")    # Timestamp
        if close_price is None or volume is None or timestamp is None:
            continue

        # Update indicators with minute data
        updated = indicators.update_minute_data(symbol, close_price, volume, timestamp)
        if updated:  # New hour completed
            action = buyCondition(symbol, indicators)
            if action == "buy":
                if simulate:
                    if not portfolio.get_position(symbol):
                        portfolio.buy(symbol, close_price, 100)
                else:
                    order = {
                        "orderType": "MARKET",
                        "session": "NORMAL",
                        "duration": "DAY",
                        "orderStrategyType": "SINGLE",
                        "orderLegCollection": [
                            {"instruction": "BUY", "quantity": 100, "instrument": {"symbol": symbol, "assetType": "EQUITY"}}
                        ]
                    }
                    response = client.order_place(account_hash, order)
                    if response.ok:
                        logging.info(f"[REAL] Placed buy order for 100 shares of {symbol}")
                    else:
                        logging.error(f"Failed to place buy order: {response.text}")
            elif action == "sell":
                if simulate:
                    if portfolio.get_position(symbol):
                        portfolio.sell(symbol, close_price, 100)
                else:
                    order = {
                        "orderType": "MARKET",
                        "session": "NORMAL",
                        "duration": "DAY",
                        "orderStrategyType": "SINGLE",
                        "orderLegCollection": [
                            {"instruction": "SELL", "quantity": 100, "instrument": {"symbol": symbol, "assetType": "EQUITY"}}
                        ]
                    }
                    response = client.order_place(account_hash, order)
                    if response.ok:
                        logging.info(f"[REAL] Placed sell order for 100 shares of {symbol}")
                    else:
                        logging.error(f"Failed to place sell order: {response.text}")

def stockScanner(service, streamer, indicators, portfolio, client):
    """
    Process SCREENER_EQUITY data and manage subscriptions to CHART_EQUITY based on buyCondition,
    using self.subscriptions to avoid redundant API calls and minimizing historical data requests.

    Args:
        service (dict): The SCREENER_EQUITY service data from the streamer.
        streamer: The Schwab streamer object for sending subscription commands.
        indicators (Indicators): Instance of Indicators class for tracking symbol data.
        portfolio (Portfolio): Instance of Portfolio class for checking positions.
        client: Schwab API client for requesting historical data.
    """
    # Minimum number of hourly candles required for indicators (e.g., MACD: 26 + 9)
    MIN_HOURLY_CANDLES = 35

    # Initial days of historical data to fetch (optimized to ~5 days)
    INITIAL_DAYS = 5

    # Process screener data
    contents = service.get("content", [])
    for content in contents:
        symbol = content.get("key", "NO KEY")
        if symbol == "NO KEY":
            continue

        # Check if already subscribed to CHART_EQUITY using self.subscriptions
        if "CHART_EQUITY" in streamer.subscriptions and symbol in streamer.subscriptions["CHART_EQUITY"]:
            continue  # Skip if already subscribed

        # Fetch minimal historical data (5 days of 1-minute candles)
        history_response = client.price_history(
            symbol=symbol,
            periodType="day",
            period=INITIAL_DAYS,
            frequencyType="minute",
            frequency=1,
            needExtendedHoursData=False
        )
        if history_response.ok:
            history_data = history_response.json()
            candles = history_data.get('candles', [])
            for candle in candles:
                close = candle['close']
                volume = candle['volume']
                timestamp = candle['datetime']  # in milliseconds
                indicators.update_minute_data(symbol, close, volume, timestamp)

            # Ensure enough hourly candles for indicators
            if symbol in indicators.hourly_data and len(indicators.hourly_data[symbol]) < MIN_HOURLY_CANDLES:
                # Fetch additional data if insufficient
                additional_days = 5
                history_response = client.price_history(
                    symbol=symbol,
                    periodType="day",
                    period=INITIAL_DAYS + additional_days,
                    frequencyType="minute",
                    frequency=1,
                    needExtendedHoursData=False
                )
                if history_response.ok:
                    history_data = history_response.json()
                    candles = history_data.get('candles', [])
                    for candle in candles:
                        close = candle['close']
                        volume = candle['volume']
                        timestamp = candle['datetime']
                        indicators.update_minute_data(symbol, close, volume, timestamp)
                else:
                    logging.error(f"Failed to fetch additional history for {symbol}: {history_response.text}")

            # Evaluate buy condition with updated indicators
            action = buyCondition(symbol, indicators)
            if action == "buy":
                # Subscribe to CHART_EQUITY for this symbol
                streamer.send(streamer.chart_equity(symbol, "0,1,2,3,4,5,6,7,8"))
                logging.info(f"Subscribed to {symbol} based on screener data and buy condition")
        else:
            logging.error(f"Failed to fetch history for {symbol}: {history_response.text}")

        # Respect API rate limits with a small delay
        time.sleep(1)

    # Unsubscribe from symbols with no open positions
    if "CHART_EQUITY" in streamer.subscriptions:
        for symbol in list(streamer.subscriptions["CHART_EQUITY"].keys()):
            if not portfolio.get_position(symbol):
                streamer.send(streamer.chart_equity(symbol, "0,1,2,3,4,5,6,7,8", command="UNSUBS"))
                logging.info(f"Unsubscribed from {symbol} as position is closed")

def main():
    """Set up and run the Schwab API streamer with historical price data."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    client = schwabdev.Client(os.getenv('app_key'), os.getenv('app_secret'), os.getenv('callback_url'))
    streamer = client.stream

    # Initialize portfolio and indicators
    portfolio = Portfolio(initial_cash=100000.0)
    simulate = True  # Set to False for real trading
    global account_hash
    account_hash = None
    if not simulate:
        account_response = client.account_linked()
        if account_response.ok:
            accounts = account_response.json()
            account_hash = accounts[0]["hashValue"]

    # Define minimal history constants
    MIN_HOURLY_CANDLES = 35
    INITIAL_DAYS = 5

    # Initialize subscriptions for initial symbols
    initial_symbols = ["TSLA"]  # Add more symbols as needed
    for symbol in initial_symbols:
        if "CHART_EQUITY" not in streamer.subscriptions:
            streamer.subscriptions["CHART_EQUITY"] = {}
        streamer.subscriptions["CHART_EQUITY"][symbol] = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]

    # Fetch minimal historical data for initial symbols
    for symbol in initial_symbols:
        # Fetch initial 5 days of 1-minute data
        history_response = client.price_history(
            symbol=symbol,
            periodType="day",
            period=INITIAL_DAYS,
            frequencyType="minute",
            frequency=1,
            needExtendedHoursData=False
        )
        if history_response.ok:
            history_data = history_response.json()
            candles = history_data.get('candles', [])
            for candle in candles:
                close = candle['close']
                volume = candle['volume']
                timestamp = candle['datetime']
                indicators.update_minute_data(symbol, close, volume, timestamp)

            # Check if enough hourly candles are available
            if symbol in indicators.hourly_data and len(indicators.hourly_data[symbol]) < MIN_HOURLY_CANDLES:
                # Fetch additional 5 days if insufficient
                additional_days = 5
                history_response = client.price_history(
                    symbol=symbol,
                    periodType="day",
                    period=INITIAL_DAYS + additional_days,
                    frequencyType="minute",
                    frequency=1,
                    needExtendedHoursData=False
                )
                if history_response.ok:
                    history_data = history_response.json()
                    candles = history_data.get('candles', [])
                    for candle in candles:
                        close = candle['close']
                        volume = candle['volume']
                        timestamp = candle['datetime']
                        indicators.update_minute_data(symbol, close, volume, timestamp)
                else:
                    logging.error(f"Failed to fetch additional history for {symbol}: {history_response.text}")
            logging.info(f"Loaded historical data for {symbol}")
        else:
            logging.error(f"Failed to fetch history for {symbol}: {history_response.text}")

    # Start the streamer
    streamer.start_auto(
        receiver=response_handler,
        start_time=datetime.time(9, 29, 0),
        stop_time=datetime.time(16, 0, 0),
        on_days=(0, 1, 2, 3, 4),
        now_timezone=zoneinfo.ZoneInfo("America/New_York"),
        daemon=True
    )

    # Subscribe to real-time data
    streamer.send(streamer.chart_equity(",".join(initial_symbols), "0,1,2,3,4,5,6,7,8"))
    streamer.send(streamer.screener_equity("$SPX.X_AVERAGE_PERCENT_VOLUME_60", "0,1,2,3,4,5,6,7,8"))

    # Main loop
    report_interval = 300  # 5 minutes
    last_report_time = time()

    while True:
        while len(shared_list) > 0:
            message = json.loads(shared_list.pop(0))
            for rtype, services in message.items():
                match rtype:
                    case "data":
                        for service in services:
                            match service:
                                case "CHART_EQUITY":
                                    stockTrader(service, client, simulate, portfolio, indicators)
                                    break
                                case "SCREENER_EQUITY":
                                    stockScanner(service, client, simulate, portfolio, indicators)
                                    #pass
                                    break
                                case _:
                                    break
                        break
                    case "notify":
                        for service in services:
                            print(f"[Heartbeat]({datetime.datetime.fromtimestamp(int(service.get('heartbeat', 0))//1000)})")
                        break
                    case _:
                        break
                
        current_time = time()
        if current_time - last_report_time >= report_interval and streamer.active:
            portfolio.report_gains_losses()
            last_report_time = current_time
        sleep(0.5)

if __name__ == '__main__':
    main()