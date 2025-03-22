import logging

class Portfolio:
    def __init__(self, initial_cash=100000.0):
        """
        Initialize the Portfolio with an initial cash balance.

        Args:
            initial_cash (float): Starting cash balance. Default is 100,000.0.

        Raises:
            ValueError: If initial_cash is negative.
        """
        if initial_cash < 0:
            logging.error("Initial cash cannot be negative")
            raise ValueError("Initial cash must be non-negative")
        self.cash = initial_cash
        self.positions = {}  # {symbol: {'quantity': float, 'entry_price': float}}
        self.realized_gains_losses = []
        logging.info(f"Portfolio initialized with cash: {self.cash:.2f}")

    def buy(self, symbol, quantity, price):
        """
        Buy a specified quantity of a stock at a given price.

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL').
            quantity (float): Number of shares to buy.
            price (float): Price per share.

        Raises:
            ValueError: If quantity or price is not positive, or if cash is insufficient.
        """
        if quantity <= 0 or price <= 0:
            raise ValueError("Quantity and price must be positive")
        cost = quantity * price
        if cost > self.cash:
            raise ValueError("Insufficient cash to buy")
        if symbol in self.positions:
            current = self.positions[symbol]
            new_quantity = current['quantity'] + quantity
            new_entry = (current['entry_price'] * current['quantity'] + price * quantity) / new_quantity
            self.positions[symbol] = {'quantity': new_quantity, 'entry_price': new_entry}
        else:
            self.positions[symbol] = {'quantity': quantity, 'entry_price': price}
        self.cash -= cost
        logging.info(f"Bought {quantity} shares of {symbol} at {price:.2f}, cost: {cost:.2f}, cash left: {self.cash:.2f}")

    def sell(self, symbol, quantity, price):
        """
        Sell a specified quantity of a stock at a given price.

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL').
            quantity (float): Number of shares to sell.
            price (float): Price per share.

        Raises:
            ValueError: If quantity or price is not positive, or if shares are insufficient.
        """
        if quantity <= 0 or price <= 0:
            raise ValueError("Quantity and price must be positive")
        if symbol not in self.positions or self.positions[symbol]['quantity'] < quantity:
            raise ValueError("Insufficient shares to sell")
        position = self.positions[symbol]
        entry_price = position['entry_price']
        profit_loss = (price - entry_price) * quantity
        self.realized_gains_losses.append(profit_loss)
        position['quantity'] -= quantity
        if position['quantity'] == 0:
            del self.positions[symbol]
        self.cash += price * quantity
        logging.info(f"Sold {quantity} shares of {symbol} at {price:.2f}, proceeds: {price * quantity:.2f}, cash: {self.cash:.2f}, P/L: {profit_loss:.2f}")

    def get_position(self, symbol):
        """
        Retrieve the current position for a stock.

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL').

        Returns:
            dict: {'quantity': float, 'entry_price': float} if position exists,
                  otherwise {'quantity': 0, 'entry_price': 0}.
        """
        return self.positions.get(symbol, {'quantity': 0, 'entry_price': 0})

    def report_gains_losses(self):
        """
        Calculate the total realized gains or losses from all sales.

        Returns:
            float: Sum of realized gains and losses.
        """
        total = sum(self.realized_gains_losses)
        logging.info(f"Total realized gains/losses: {total:.2f}")
        return total