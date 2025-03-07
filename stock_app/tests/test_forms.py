from django.test import TestCase
from ..forms import OrderForm, PortfolioForm, AlgoStrategyForm  
from ..models import Portfolio, Stock, User
from decimal import Decimal
from datetime import date

class FormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.stock = Stock.objects.create(ticker='AAPL', name='Apple Inc', price=Decimal('175.50'))
        self.portfolio = Portfolio.objects.create(user=self.user, name='TestPortfolio')

    def test_order_form_valid(self):
        data = {
            'stock_ticker': 'AAPL',
            'quantity': 10,
            'type': 'BUY',
            'order_type': 'MARKET',
            'use_margin': False
        }
        form = OrderForm(data)
        self.assertTrue(form.is_valid())

    def test_order_form_invalid_options(self):
        data = {
            'stock_ticker': 'AAPL',
            'quantity': 10,
            'type': 'BUY',
            'order_type': 'CALL_OPTION',
            'use_margin': False
        }
        form = OrderForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('Strike Price and Expiration Date are required', str(form.errors))

    def test_portfolio_form_valid(self):
        data = {'name': 'NewPortfolio'}
        form = PortfolioForm(data)
        self.assertTrue(form.is_valid())

    def test_algo_strategy_form_valid(self):
        data = {
            'name': 'TestAlgo',
            'stock': self.stock.id,
            'condition': '50-day MA > 200-day MA',
            'action': 'BUY',
            'quantity': 5,
            'is_active': True
        }
        form = AlgoStrategyForm(data)
        self.assertTrue(form.is_valid())