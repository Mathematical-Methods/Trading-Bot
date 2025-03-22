import unittest
import logging
from domain.entities.portfolio import Portfolio

class TestPortfolio(unittest.TestCase):
    
    def setUp(self):
        # Clear logging handlers to avoid interference between tests
        logging.getLogger().handlers = []
        logging.basicConfig(level=logging.INFO)
        # Initialize a Portfolio instance with 100,000 cash for each test
        self.portfolio = Portfolio(initial_cash=100000.0)
    
    ### Tests for Initialization (__init__)
    def test_initialization_successful(self):
        # Assert
        self.assertEqual(self.portfolio.cash, 100000.0)
        self.assertEqual(self.portfolio.positions, {})
        self.assertEqual(self.portfolio.realized_gains_losses, [])
    
    ### Tests for buy Method
    def test_buy_successful(self):
        # Act
        self.portfolio.buy('AAPL', 100, 150.0)
        
        # Assert
        self.assertEqual(self.portfolio.cash, 85000.0)  # 100,000 - (100 * 150)
        self.assertEqual(self.portfolio.get_position('AAPL'), {'quantity': 100, 'entry_price': 150.0})
    
    def test_buy_insufficient_cash(self):
        # Act & Assert
        with self.assertRaises(ValueError) as cm:
            self.portfolio.buy('AAPL', 1000, 150.0)  # Cost: 150,000 > 100,000
        self.assertEqual(str(cm.exception), "Insufficient cash to buy")
    
    def test_buy_invalid_quantity_or_price(self):
        # Test negative quantity
        with self.assertRaises(ValueError) as cm:
            self.portfolio.buy('AAPL', -10, 150.0)
        self.assertEqual(str(cm.exception), "Quantity and price must be positive")
        
        # Test negative price
        with self.assertRaises(ValueError) as cm:
            self.portfolio.buy('AAPL', 100, -150.0)
        self.assertEqual(str(cm.exception), "Quantity and price must be positive")
    
    def test_buy_additional_shares(self):
        # Arrange: First buy
        self.portfolio.buy('AAPL', 100, 150.0)
        
        # Act: Buy more shares
        self.portfolio.buy('AAPL', 50, 160.0)
        
        # Assert: Check weighted average entry price and total quantity
        expected_entry = (150.0 * 100 + 160.0 * 50) / 150  # (15,000 + 8,000) / 150 = 153.33
        self.assertAlmostEqual(self.portfolio.get_position('AAPL')['entry_price'], expected_entry, places=2)
        self.assertEqual(self.portfolio.get_position('AAPL')['quantity'], 150)
        self.assertEqual(self.portfolio.cash, 77000.0)  # 100,000 - 15,000 - 8,000
    
    ### Tests for sell Method
    def test_sell_successful(self):
        # Arrange
        self.portfolio.buy('AAPL', 100, 150.0)
        
        # Act
        self.portfolio.sell('AAPL', 50, 160.0)
        
        # Assert
        self.assertEqual(self.portfolio.cash, 93000.0)  # 85,000 + (50 * 160)
        self.assertEqual(self.portfolio.get_position('AAPL'), {'quantity': 50, 'entry_price': 150.0})
        self.assertEqual(self.portfolio.report_gains_losses(), 500.0)  # (160 - 150) * 50
    
    def test_sell_insufficient_shares(self):
        # Arrange
        self.portfolio.buy('AAPL', 100, 150.0)
        
        # Act & Assert
        with self.assertRaises(ValueError) as cm:
            self.portfolio.sell('AAPL', 150, 160.0)
        self.assertEqual(str(cm.exception), "Insufficient shares to sell")
    
    def test_sell_invalid_quantity_or_price(self):
        # Arrange
        self.portfolio.buy('AAPL', 100, 150.0)
        
        # Test negative quantity
        with self.assertRaises(ValueError) as cm:
            self.portfolio.sell('AAPL', -10, 160.0)
        self.assertEqual(str(cm.exception), "Quantity and price must be positive")
        
        # Test negative price
        with self.assertRaises(ValueError) as cm:
            self.portfolio.sell('AAPL', 50, -160.0)
        self.assertEqual(str(cm.exception), "Quantity and price must be positive")
    
    def test_sell_all_shares(self):
        # Arrange
        self.portfolio.buy('AAPL', 100, 150.0)
        
        # Act
        self.portfolio.sell('AAPL', 100, 160.0)
        
        # Assert
        self.assertEqual(self.portfolio.cash, 101000.0)  # 100,000 - (100 * 150) + (100 * 160)
        self.assertEqual(self.portfolio.get_position('AAPL'), {'quantity': 0, 'entry_price': 0})
        self.assertEqual(self.portfolio.report_gains_losses(), 1000.0)  # (160 - 150) * 100
    
    ### Tests for get_position Method
    def test_get_position_existing(self):
        # Arrange
        self.portfolio.buy('AAPL', 100, 150.0)
        
        # Act
        position = self.portfolio.get_position('AAPL')
        
        # Assert
        self.assertEqual(position, {'quantity': 100, 'entry_price': 150.0})
    
    def test_get_position_non_existing(self):
        # Act
        position = self.portfolio.get_position('GOOG')
        
        # Assert
        self.assertEqual(position, {'quantity': 0, 'entry_price': 0})
    
    ### Tests for report_gains_losses Method
    def test_report_gains_losses_no_sales(self):
        # Act
        total = self.portfolio.report_gains_losses()
        
        # Assert
        self.assertEqual(total, 0.0)
    
    def test_report_gains_losses_after_multiple_sales(self):
        # Arrange
        self.portfolio.buy('AAPL', 100, 150.0)
        self.portfolio.sell('AAPL', 50, 160.0)  # Gain: (160 - 150) * 50 = 500
        self.portfolio.sell('AAPL', 50, 155.0)  # Gain: (155 - 150) * 50 = 250
        
        # Act
        total = self.portfolio.report_gains_losses()
        
        # Assert
        self.assertEqual(total, 750.0)  # 500 + 250

if __name__ == '__main__':
    unittest.main()