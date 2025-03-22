import logging

class Portfolio:
    def __init__(self, initial_cash=100000.0):
        """
        Initialize the simulated portfolio with a cash balance.

        Args:
            initial_cash (float): Initial cash amount, defaults to 100000.0.

        Attributes:
            cash (float): Current cash balance.
            positions (dict): {symbol: {'quantity': int, 'entry_price': float}}.
            realized_gains_losses (list): List of realized profit/loss amounts.
        """
        if initial_cash < 0:
            logging.error("Initial cash cannot be negative")
            raise ValueError("Initial cash must be non-negative")
        
        self.cash = initial_cash
        self.positions = {}
        self.realized_gains_losses = []
        logging.info(f"Portfolio initialized with initial cash: {self.cash:.2f}")

def initialize_portfolio(initial_cash=100000.0):
    """
    Creates a simulated portfolio with an initial cash balance.

    Args:
        initial_cash (float): Initial cash amount, defaults to 100000.0.

    Returns:
        tuple: (bool, Portfolio or None) - Success flag and Portfolio instance if successful, None if failed.
    """
    try:
        portfolio = Portfolio(initial_cash)
        return True, portfolio
    except ValueError as e:
        logging.error(f"Failed to initialize portfolio: {str(e)}")
        return False, None