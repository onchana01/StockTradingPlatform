from rest_framework import serializers
from .models import Portfolio, Stock, PortfolioStock, Transaction
from django.contrib.auth.models import User

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'ticker', 'name', 'price', 'last_updated']
        read_only_fields = ['last_updated']

    def validate_ticker(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Ticker cannot be empty.")
        return value.upper()

class PortfolioStockSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    stock_id = serializers.PrimaryKeyRelatedField(
        queryset=Stock.objects.all(), source='stock', write_only=True
    )

    class Meta:
        model = PortfolioStock
        fields = ['id', 'portfolio', 'stock', 'stock_id', 'quantity', 'purchase_price']
        read_only_fields = ['portfolio']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

class PortfolioSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    stocks = PortfolioStockSerializer(source='portfoliostock_set', many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = ['id', 'user', 'name', 'created_at', 'stocks']
        read_only_fields = ['created_at', 'user']

    def validate_name(self, value):
        user = self.context['request'].user
        if Portfolio.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError("A portfolio with this name already exists.")
        return value

class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    stock = StockSerializer(read_only=True)
    stock_id = serializers.PrimaryKeyRelatedField(
        queryset=Stock.objects.all(), source='stock', write_only=True
    )
    portfolio = serializers.PrimaryKeyRelatedField(read_only=True)  # Removed queryset
    portfolio_id = serializers.PrimaryKeyRelatedField(
        queryset=Portfolio.objects.all(), source='portfolio', write_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'stock', 'stock_id', 'portfolio', 'portfolio_id',
            'type', 'quantity', 'price', 'timestamp'
        ]
        read_only_fields = ['user', 'timestamp', 'portfolio']

    def validate(self, data):
        quantity = data.get('quantity')
        portfolio = data.get('portfolio')
        stock = data.get('stock')
        order_type = data.get('type')

        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")

        if order_type == 'SELL':
            portfolio_stock = PortfolioStock.objects.filter(
                portfolio=portfolio, stock=stock
            ).first()
            if not portfolio_stock or portfolio_stock.quantity < quantity:
                raise serializers.ValidationError(
                    "Insufficient stock quantity in portfolio for this sell order."
                )

        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TransactionHistorySerializer(serializers.ModelSerializer):
    stock_ticker = serializers.CharField(source='stock.ticker', read_only=True)
    portfolio_name = serializers.CharField(source='portfolio.name', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'stock_ticker', 'portfolio_name', 'type',
            'quantity', 'price', 'timestamp'
        ]