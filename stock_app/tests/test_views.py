
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Stock, Portfolio, Transaction, AlgoStrategy  
from decimal import Decimal

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.stock = Stock.objects.create(ticker='AAPL', name='Apple Inc', price=Decimal('175.50'))
        self.portfolio = Portfolio.objects.create(user=self.user, name='TestPortfolio')

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertContains(response, '<h2>Register</h2>')

    def test_register_view_post(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_dashboard_view_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, 'Welcome, testuser')

    def test_execute_order_view_get(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('execute_order', args=[self.portfolio.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stock_detail.html')
        self.assertContains(response, 'Manage Portfolio: TestPortfolio')

    def test_execute_order_view_post_order(self):
        self.client.login(username='testuser', password='testpass')
        data = {
            'order_form': '1',
            'stock_ticker': 'AAPL',
            'quantity': 5,
            'type': 'BUY',
            'order_type': 'MARKET',
            'use_margin': False
        }
        response = self.client.post(reverse('execute_order', args=[self.portfolio.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Transaction.objects.filter(stock=self.stock, quantity=5).exists())