import unittest
import logging
from portfolio import initialize_portfolio

class TestInitializePortfolio(unittest.TestCase):
    
    def setUp(self):
        # Clear logging handlers to avoid interference
        logging.getLogger().handlers = []
        logging.basicConfig(level=logging.INFO)
    
    def test_successful_initialization_default(self):
        # Act
        with self.assertLogs(level='INFO') as log:
            success, portfolio = initialize_portfolio()
        
        # Assert
        self.assertTrue(success)
        self.assertIsNotNone(portfolio)
        self.assertEqual(portfolio.cash, 100000.0)
        self.assertEqual(portfolio.positions, {})
        self.assertEqual(portfolio.realized_gains_losses, [])
        self.assertIn("Portfolio initialized with initial cash: 100000.00", log.output[-1])
    
    def test_successful_initialization_custom_cash(self):
        # Arrange
        custom_cash = 50000.0
        
        # Act
        with self.assertLogs(level='INFO') as log:
            success, portfolio = initialize_portfolio(custom_cash)
        
        # Assert
        self.assertTrue(success)
        self.assertIsNotNone(portfolio)
        self.assertEqual(portfolio.cash, 50000.0)
        self.assertEqual(portfolio.positions, {})
        self.assertEqual(portfolio.realized_gains_losses, [])
        self.assertIn("Portfolio initialized with initial cash: 50000.00", log.output[-1])
    
    def test_negative_cash_failure(self):
        # Arrange
        negative_cash = -1000.0
        
        # Act
        with self.assertLogs(level='ERROR') as log:
            success, portfolio = initialize_portfolio(negative_cash)
        
        # Assert
        self.assertFalse(success)
        self.assertIsNone(portfolio)
        self.assertIn("Failed to initialize portfolio: Initial cash must be non-negative", log.output[-1])

if __name__ == '__main__':
    unittest.main()