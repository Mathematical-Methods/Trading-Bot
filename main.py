import schwabdev
import os
from dotenv import load_dotenv


class TradingBot:
    def __init__(self, app_key, app_secret, symbol, simulate):
        self.app_key = app_key
        self.app_secret = app_secret
        self.symbol = symbol
        self.client = schwabdev.Client(app_key, app_secret,'https://127.0.0.1')
    
    def decide_action(self, price):
        if price < self.buy_threshold:
            return 'buy'
        elif price > self.sell_threshold:
            return 'sell'
        else:
            return 'hold'

    def step(self, price):
        action = self.decide_action(price)
        if action == 'buy' and self.cash >= price:
            self.cash -= price
            self.holdings += 1
        elif action == 'sell' and self.holdings > 0:
            self.cash += price
            self.holdings -= 1
    

if __name__ == '__main__':
    load_dotenv()
    bot = TradingBot(os.getenv('app_key'), os.getenv('app_secret'), "APPL", simulate=True)
    bot.run()