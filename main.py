import schwabdev
import os
import schwabdev.stream
import datetime
import zoneinfo
import json
from dotenv import load_dotenv
from time import sleep, time








class TradingBot:
    def __init__(self, app_key, app_secret, symbol, simulate):
        self.app_key = app_key
        self.app_secret = app_secret
        self.symbol = symbol
        self.shared_list = []
        self.client = schwabdev.Client(app_key, app_secret,'https://127.0.0.1')
        self.stream = schwabdev.stream.Stream(self.client)

    def response_handler(self, message):
        """Append incoming streamer messages to the shared list."""
        self.shared_list.append(message)

    def run(self):
        """Start the trading bot's main loop."""
        initial_symbols = self.symbol

        self.stream.start_auto(
            receiver=self.response_handler,
            start_time=datetime.time(9, 29, 0),
            stop_time=datetime.time(16, 0, 0),
            on_days=(0, 1, 2, 3, 4),
            now_timezone=zoneinfo.ZoneInfo("America/New_York"),
            daemon=True
        )

        self.stream.send(self.stream.chart_equity(",".join(initial_symbols), "0,1,2,3,4,5,6,7,8"))

        report_interval = 300  # 5 minutes
        last_report_time = time()

        while True:
            while len(self.shared_list) > 0:
                message = json.loads(self.shared_list.pop(0))
                for rtype, services in message.items():
                    if rtype == "data":
                        for service in services:
                            if service["service"] == "CHART_EQUITY":
                                print(f"{service}")
                                self.stock_trader(service)
                            # TODO     
                            #elif service["service"] == "History":
                            #    self.stock_scanner(service)
                    elif rtype == "notify":
                        for service in services:
                            self.logger.info(f"[Heartbeat]({datetime.datetime.fromtimestamp(int(service.get('heartbeat', 0))//1000)})")
            current_time = time()
            if current_time - last_report_time >= report_interval and self.stream.active:
                #TODO self.portfolio.report_gains_losses()
                last_report_time = current_time
            sleep(0.5)

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



if __name__ == '__main__':
    load_dotenv()
    bot = TradingBot(os.getenv('app_key'), os.getenv('app_secret'), "APPL", simulate=True)
    bot.run()