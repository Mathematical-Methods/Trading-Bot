import schwabdev

class TradingBot:
    def __init__(self, cash, symbol):
        self.cash = cash
        self.holdings = 0
        self.symbol = symbol
    
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
    
        