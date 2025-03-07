from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Stock, Portfolio, PortfolioStock, Transaction, AlgoStrategy  
from decimal import Decimal


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.stock = Stock.objects.create(ticker='AAPL', name='Apple Inc', price=Decimal('175.50'))
        self.portfolio = Portfolio.objects.create(user=self.user, name='TestPortfolio')

    def test_stock_str(self):
        self.assertEqual(str(self.stock), 'AAPL - Apple Inc')

    def test_portfolio_str(self):
        self.assertEqual(str(self.portfolio), "testuser's TestPortfolio")

    def test_portfolio_stock_creation(self):
        ps = PortfolioStock.objects.create(portfolio=self.portfolio, stock=self.stock, quantity=10, purchase_price=Decimal('150.00'))
        self.assertEqual(ps.quantity, 10)
        self.assertEqual(ps.purchase_price, Decimal('150.00'))

    def test_transaction_creation(self):
        tx = Transaction.objects.create(
            user=self.user, stock=self.stock, portfolio=self.portfolio,
            type='BUY', order_type='MARKET', quantity=5, price=Decimal('175.50'),
            status='EXECUTED'
        )
        self.assertEqual(str(tx), 'testuser - BUY MARKET AAPL')
        self.assertEqual(tx.quantity, 5)

    def test_algo_strategy_creation(self):
        algo = AlgoStrategy.objects.create(
            portfolio=self.portfolio, name='MACrossover', stock=self.stock,
            condition='50-day MA > 200-day MA', action='BUY', quantity=10, is_active=True
        )
        self.assertEqual(str(algo), 'MACrossover for TestPortfolio')
        self.assertTrue(algo.is_active)