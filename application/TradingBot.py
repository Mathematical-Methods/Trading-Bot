import logging
import json
import datetime
from time import sleep, time
from collections import deque
from schwabdev import Client
from schwabdev.client import Stream
from dotenv import load_dotenv
import os
import zoneinfo
from domain.entities.indicators import Indicators
from domain.entities.portfolio import Portfolio

class TradingBot:
    def __init__(self, app_key, app_secret, callback_url="https://127.0.0.1", tokens_file="tokens.json", simulate=True, initial_cash=100000.0):
        """
        Initialize the TradingBot with necessary components.

        Args:
            app_key (str): Schwab API application key.
            app_secret (str): Schwab API application secret.
            callback_url (str): Callback URL for OAuth authentication.
            tokens_file (str): Path to the tokens file.
            simulate (bool): Whether to simulate trades or execute real orders.
            initial_cash (float): Initial cash for the simulated portfolio.
        """
        self.client = Client(app_key, app_secret, callback_url, tokens_file)
        self.stream = Stream(self.client)
        self.indicators = Indicators()
        self.portfolio = Portfolio(initial_cash=initial_cash)
        self.simulate = simulate
        self.shared_list = []
        self.logger = logging.getLogger('TradingBot')
        logging.basicConfig(level=logging.INFO)
        self.account_hash = None
        if not simulate:
            account_response = self.client.account_linked()
            if account_response.ok:
                accounts = account_response.json()
                self.account_hash = accounts[0]["hashValue"]
            else:
                raise Exception("Failed to get account hash")

    def setup(self, initial_symbols):
        """
        Set up initial subscriptions and load historical data.

        Args:
            initial_symbols (list): List of symbols to subscribe to initially.
        """
        for symbol in initial_symbols:
            if "CHART_EQUITY" not in self.stream.subscriptions:
                self.stream.subscriptions["CHART_EQUITY"] = {}
            self.stream.subscriptions["CHART_EQUITY"][symbol] = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
            self._load_initial_history(symbol)

    def _load_initial_history(self, symbol, min_hourly_candles=35, initial_days=5):
        """
        Load initial historical data for a symbol.

        Args:
            symbol (str): Stock symbol.
            min_hourly_candles (int): Minimum number of hourly candles required.
            initial_days (int): Initial number of days to fetch.
        """
        history_response = self.client.price_history(
            symbol=symbol,
            periodType="day",
            period=initial_days,
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
                self.indicators.update_minute_data(symbol, close, volume, timestamp)

            if symbol in self.indicators.hourly_data and len(self.indicators.hourly_data[symbol]) < min_hourly_candles:
                additional_days = 5
                history_response = self.client.price_history(
                    symbol=symbol,
                    periodType="day",
                    period=initial_days + additional_days,
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
                        self.indicators.update_minute_data(symbol, close, volume, timestamp)
                else:
                    self.logger.error(f"Failed to fetch additional history for {symbol}: {history_response.text}")
            self.logger.info(f"Loaded historical data for {symbol}")
        else:
            self.logger.error(f"Failed to fetch history for {symbol}: {history_response.text}")

    def response_handler(self, message):
        """Append incoming streamer messages to the shared list."""
        self.shared_list.append(message)

    def run(self):
        """Start the trading bot's main loop."""
        initial_symbols = ["TSLA"]  # Add more symbols as needed
        self.setup(initial_symbols)

        self.stream.start_auto(
            receiver=self.response_handler,
            start_time=datetime.time(9, 29, 0),
            stop_time=datetime.time(16, 0, 0),
            on_days=(0, 1, 2, 3, 4),
            now_timezone=zoneinfo.ZoneInfo("America/New_York"),
            daemon=True
        )

        self.stream.send(self.stream.chart_equity(",".join(initial_symbols), "0,1,2,3,4,5,6,7,8"))
        self.stream.send(self.stream.screener_equity("$SPX.X_AVERAGE_PERCENT_VOLUME_60", "0,1,2,3,4,5,6,7,8"))

        report_interval = 300  # 5 minutes
        last_report_time = time()

        while True:
            while len(self.shared_list) > 0:
                message = json.loads(self.shared_list.pop(0))
                for rtype, services in message.items():
                    if rtype == "data":
                        for service in services:
                            if service["service"] == "CHART_EQUITY":
                                self.stock_trader(service)
                            elif service["service"] == "SCREENER_EQUITY":
                                self.stock_scanner(service)
                    elif rtype == "notify":
                        for service in services:
                            self.logger.info(f"[Heartbeat]({datetime.datetime.fromtimestamp(int(service.get('heartbeat', 0))//1000)})")
            current_time = time()
            if current_time - last_report_time >= report_interval and self.stream.active:
                self.portfolio.report_gains_losses()
                last_report_time = current_time
            sleep(0.5)

    def has_macd_crossover(self, macdhistory, direction="above"):
        if len(macdhistory) < 2:
            return False
        for i in range(1, min(4, len(macdhistory))):
            prev_macd, prev_signal = macdhistory[-i-1]
            curr_macd, curr_signal = macdhistory[-i]
            if direction == "above" and prev_macd <= prev_signal and curr_macd > curr_signal:
                return True
            elif direction == "below" and prev_macd >= prev_signal and curr_macd < curr_signal:
                return True
        return False

    def buy_condition(self, symbol):
        """
        Determine trading action based on the intraday swing trading strategy.

        Returns:
            str: "buy", "sell", or "hold"
        """
        ind = self.indicators.indicators.get(symbol, {})
        if not ind or len(ind['ma_short_history']) < 2:
            return "hold"

        ma_short_prev = ind['ma_short_history'][-2]
        ma_long_prev = ind['ma_long_history'][-2]
        ma_short_current = ind['ma_short_history'][-1]
        ma_long_current = ind['ma_long_history'][-1]
        ma_cross_up = ma_short_prev <= ma_long_prev and ma_short_current > ma_long_current
        ma_cross_down = ma_short_prev >= ma_long_prev and ma_short_current < ma_long_current

        rsi = ind['rsi_history'][-1] if ind['rsi_history'] else None
        rsi_buy = rsi is not None and rsi < 70
        rsi_sell = rsi is not None and rsi > 70

        macd_history = ind['macd_history']
        macd_buy = self.has_macd_crossover(macd_history, "above")
        macd_sell = self.has_macd_crossover(macd_history, "below")

        bollinger = ind['bollinger_history'][-1] if ind['bollinger_history'] else (None, None, None)
        bollinger_condition = False
        if bollinger[0] is not None:
            upper, middle, lower = bollinger
            band_width = (upper - lower) / middle
            bollinger_condition = band_width < 0.1

        volume_history = ind['volume_history']
        volume_condition = False
        if len(volume_history) >= 6:
            current_volume = volume_history[-1]
            volume_condition = all(current_volume > v for v in volume_history[-6:-1])

        if ma_cross_up and rsi_buy and macd_buy and bollinger_condition and volume_condition:
            return "buy"
        if ma_cross_down and rsi_sell and macd_sell and bollinger_condition:
            return "sell"
        return "hold"

    def stock_trader(self, service):
        """Process CHART_EQUITY data and execute trades."""
        contents = service.get("content", [])
        for content in contents:
            symbol = content.get("key", "NO KEY")
            close_price = content.get("4")
            volume = content.get("5")
            timestamp = content.get("7")
            if close_price is None or volume is None or timestamp is None:
                continue

            updated = self.indicators.update_minute_data(symbol, close_price, volume, timestamp)
            if updated:
                action = self.buy_condition(symbol)
                if action == "buy":
                    if self.simulate:
                        if not self.portfolio.get_position(symbol):
                            self.portfolio.buy(symbol, close_price, 100)
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
                        response = self.client.order_place(self.account_hash, order)
                        if response.ok:
                            self.logger.info(f"[REAL] Placed buy order for 100 shares of {symbol}")
                        else:
                            self.logger.error(f"Failed to place buy order: {response.text}")
                elif action == "sell":
                    if self.simulate:
                        if self.portfolio.get_position(symbol):
                            self.portfolio.sell(symbol, close_price, 100)
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
                        response = self.client.order_place(self.account_hash, order)
                        if response.ok:
                            self.logger.info(f"[REAL] Placed sell order for 100 shares of {symbol}")
                        else:
                            self.logger.error(f"Failed to place sell order: {response.text}")

    def stock_scanner(self, service):
        """Process SCREENER_EQUITY data and manage subscriptions."""
        MIN_HOURLY_CANDLES = 35
        INITIAL_DAYS = 5

        contents = service.get("content", [])
        for content in contents:
            symbol = content.get("key", "NO KEY")
            if symbol == "NO KEY":
                continue

            if "CHART_EQUITY" in self.stream.subscriptions and symbol in self.stream.subscriptions["CHART_EQUITY"]:
                continue

            history_response = self.client.price_history(
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
                    self.indicators.update_minute_data(symbol, close, volume, timestamp)

                if symbol in self.indicators.hourly_data and len(self.indicators.hourly_data[symbol]) < MIN_HOURLY_CANDLES:
                    additional_days = 5
                    history_response = self.client.price_history(
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
                            self.indicators.update_minute_data(symbol, close, volume, timestamp)
                    else:
                        self.logger.error(f"Failed to fetch additional history for {symbol}: {history_response.text}")

                action = self.buy_condition(symbol)
                if action == "buy":
                    self.stream.send(self.stream.chart_equity(symbol, "0,1,2,3,4,5,6,7,8"))
                    self.logger.info(f"Subscribed to {symbol} based on screener data and buy condition")
            else:
                self.logger.error(f"Failed to fetch history for {symbol}: {history_response.text}")
            sleep(1)

        if "CHART_EQUITY" in self.stream.subscriptions:
            for symbol in list(self.stream.subscriptions["CHART_EQUITY"].keys()):
                if not self.portfolio.get_position(symbol):
                    self.stream.send(self.stream.chart_equity(symbol, "0,1,2,3,4,5,6,7,8", command="UNSUBS"))
                    self.logger.info(f"Unsubscribed from {symbol} as position is closed")

# Example usage
if __name__ == '__main__':
    load_dotenv()
    bot = TradingBot(os.getenv('app_key'), os.getenv('app_secret'), simulate=True)
    bot.run()