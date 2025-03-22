import logging

class Portfolio:
    def __init__(self, initial_cash=100000.0):
        self.cash = initial_cash
        self.positions = {}
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
