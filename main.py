import schwabdev
import os
import schwabdev.stream
import datetime
import zoneinfo
import json
from indicators import Indicators
from portfolio import Portfolio
from dotenv import load_dotenv
from time import sleep, time

class AccountInformation:
    def __init__(self, client):
        self.client = client
        self.account_linked = []

    def refreshAccountLinked(self):
        self.account_linked = self.client.account_linked()

    def getAccountNumber(self):
        return self.account_linked.json()[0].get('accountNumber')

    def getAccountHash(self):
        return self.account_linked.json()[0].get('accountHash')


class TradingBot:
    def __init__(self, app_key, app_secret, symbol, simulate):
        self.app_key = app_key
        self.app_secret = app_secret
        self.symbol = symbol
        self.shared_list = []
        self.client = schwabdev.Client(app_key, app_secret,'https://127.0.0.1')
        self.stream = schwabdev.stream.Stream(self.client)
        #self.indicators = Indicators()
        self.account = AccountInformation(self.client)

    def action_condition(self, symbol):
        """
        Determine trading action based on the intraday swing trading strategy.

        Returns:
            str: "buy", "sell", or "hold"
        
        # Import symbol history.
        # ind = self.indicators.indicators.get(symbol, {})

        ## return hold if not enough data.
    
        # TODO
        ## Determine Buy condition according to Truth values.
        if #ma_cross_up and rsi_buy and macd_buy and bollinger_condition and volume_condition:
            # return "Buy" if conditions are true
            return "buy"
        if #ma_cross_down and rsi_sell and macd_sell and bollinger_condition:
            # return "sell" if conditioner are true for sell
            return "sell"
        return "hold"
        """
        pass

    def response_handler(self, message): # Don't touch.
        """Append incoming streamer messages to the shared list."""
        self.shared_list.append(message)

    def report_gains_losses():
        pass

    def setup():
        pass

    def run(self): # TODO report gains losses
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

        report_interval = 60  # 5 minutes
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
                    elif rtype == "notify":
                        for service in services:
                            self.logger.info(f"[Heartbeat]({datetime.datetime.fromtimestamp(int(service.get('heartbeat', 0))//1000)})")
            current_time = time()
            if current_time - last_report_time >= report_interval and self.stream.active:
                #TODO self.portfolio.report_gains_losses()
                # account_linked = client.account_linked()
                # account_details = client.account_details(, fields=None)
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
            
            ## TODO et cash available for trading.

            action = self.action(symbol)
            if action == "buy":
                if self.simulate:
                    pass
                    #TODO 
                    # if not self.portfolio.get_position(symbol):
                    #    self.portfolio.buy(symbol, close_price, 100)
                else:
                    order = {
                        "orderType": "MARKET",
                        "session": "NORMAL",
                        "duration": "DAY",
                        "orderStrategyType": "SINGLE",
                        "orderLegCollection": [
                            {"instruction": "BUY", "quantity": 1, "instrument": {"symbol": symbol, "assetType": "EQUITY"}}
                        ]
                    }
                    response = self.client.order_place(self.account_hash, order)
                    if response.ok:
                        self.logger.info(f"[REAL] Placed buy order for 1 share of {symbol}")
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

""" Unit tests """

def testinitialization(app_key,app_secret,callback_url):
    client = schwabdev.client.Client(app_key,app_secret,callback_url)
    return client



if __name__ == '__main__':
    load_dotenv()
    """Begin Unit testing"""
    





    #bot = TradingBot(os.getenv('app_key'), os.getenv('app_secret'), "TSLL", simulate=True)
    #bot.run()