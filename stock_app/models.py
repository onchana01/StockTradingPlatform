from random import choices
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sector = models.CharField(max_length=50, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticker} - {self.name}"

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='portfolio_images/', blank=True, null=True)
    margin_enabled = models.BooleanField(default=False)
    margin_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

class PortfolioStock(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock  = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('portfolio', 'stock')

class Transaction(models.Model):
    TYPE_CHOICES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    ORDER_TYPE_CHOICES = (
        ('MARKET', 'Market'),
        ('LIMIT', 'Limit'),
        ('STOP_LOSS', 'Stop-Loss'),
        ('CALL_OPTION', 'Call Option'),  
        ('PUT_OPTION', 'Put Option'), 
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('EXECUTED', 'Executed'),
        ('CANCELED', 'Canceled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    order_type = models.CharField(max_length=12, choices=ORDER_TYPE_CHOICES, default='MARKET')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    limit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    strike_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    expiration_date = models.DateField(null=True, blank=True)  # New: Options
    margin_used = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.type} {self.order_type} {self.stock.ticker}"

class AlgoStrategy(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    condition = models.CharField(max_length=100)  # e.g., "50-day MA > 200-day MA"
    action = models.CharField(max_length=4, choices=Transaction.TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} for {self.portfolio.name}"