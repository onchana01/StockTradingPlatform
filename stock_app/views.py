from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from alpha_vantage.timeseries import TimeSeries
from decimal import Decimal
import pandas as pd
import os

from .models import Portfolio, Stock, PortfolioStock, Transaction, AlgoStrategy
from .forms import OrderForm, PortfolioForm, AlgoStrategyForm, UserRegistrationForm
from .serializers import StockSerializer, PortfolioSerializer, PortfolioStockSerializer, TransactionSerializer



# ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'W4AQWGNID2HL4KBJ')

# Pre-login dashboard with general market data
def public_dashboard(request):
    ts = TimeSeries(key=settings.ALPHA_VANTAGE_API_KEY, output_format='pandas')
    indices = ['SPY', 'DIA', 'QQQ', 'IWM', 'GLD']  
    market_data = {}
    for symbol in indices:
        try:
            data, _ = ts.get_daily(symbol=symbol, outputsize='compact')
            latest_price = float(data['4. close'].iloc[0])
            previous_price = float(data['4. close'].iloc[1])
            change = latest_price - previous_price
            change_percent = (change / previous_price) * 100
            market_data[symbol] = {
                'price': latest_price,
                'change': change,
                'change_percent': change_percent,
                'history': data['4. close'].head(5).tolist()
            }
        except ValueError as e:
            market_data[symbol] = {'error': str(e)}
    context = {'market_data': market_data}
    return render(request, 'public_dashboard.html', context)


# Dashboard view - requires login
@login_required
def dashboard(request):
    portfolios = Portfolio.objects.filter(user=request.user).distinct()
    ts = TimeSeries(key=settings.ALPHA_VANTAGE_API_KEY, output_format='pandas')
    
    # Portfolio stocks with real-time data
    portfolio_stocks = PortfolioStock.objects.filter(portfolio__user=request.user).select_related('stock')
    stock_data = {}
    total_value = Decimal('0.00')
    total_cost = Decimal('0.00')
    sector_data = {}

    for ps in portfolio_stocks:
        cache_key = f'stock_data_{ps.stock.ticker}'
        cached_data = cache.get(cache_key)
        if cached_data and 'price' in cached_data:
            stock_data[ps.stock.ticker] = cached_data
        else:
            try:
                data, _ = ts.get_daily(symbol=ps.stock.ticker, outputsize='compact')
                latest_price = Decimal(str(data['4. close'].iloc[0]))
                change = latest_price - Decimal(str(data['4. close'].iloc[1]))
                if not ps.stock.sector:
                    ps.stock.sector = 'Unknown'
                    ps.stock.save()
                stock_data[ps.stock.ticker] = {
                    'price': latest_price,
                    'change': change,
                    'quantity': ps.quantity,
                    'history': data['4. close'].head(5).tolist()
                }
                cache.set(cache_key, stock_data[ps.stock.ticker], 86400)
            except ValueError as e:
                stock_data[ps.stock.ticker] = {'error': str(e)}

        if 'price' in stock_data[ps.stock.ticker]:
            value = stock_data[ps.stock.ticker]['price'] * ps.quantity
            cost = ps.purchase_price * ps.quantity
            total_value += value
            total_cost += cost
            sector = ps.stock.sector or 'Unknown'
            sector_data[sector] = sector_data.get(sector, Decimal('0.00')) + value

    unrealized_gain_loss = total_value - total_cost
    return_percent = (unrealized_gain_loss / total_cost * 100) if total_cost > 0 else Decimal('0.00')
    diversification = {sector: (value / total_value * 100) for sector, value in sector_data.items()} if total_value > 0 else {}

    # Market data
    indices = ['SPY', 'DIA', 'QQQ', 'IWM', 'GLD']
    market_data = {}
    for symbol in indices:
        cache_key = f'market_data_{symbol}'
        cached_data = cache.get(cache_key)
        if cached_data:
            market_data[symbol] = cached_data
        else:
            try:
                data, _ = ts.get_daily(symbol=symbol, outputsize='compact')
                latest_price = Decimal(str(data['4. close'].iloc[0]))
                previous_price = Decimal(str(data['4. close'].iloc[1]))
                change = latest_price - previous_price
                change_percent = (change / previous_price) * 100
                market_data[symbol] = {
                    'price': latest_price,
                    'change': change,
                    'change_percent': change_percent,
                    'history': data['4. close'].head(5).tolist()
                }
                cache.set(cache_key, market_data[symbol], 86400)
            except ValueError as e:
                market_data[symbol] = {'error': str(e)}

    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            messages.success(request, "Portfolio created successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to create portfolio. Please check the form.")
    else:
        form = PortfolioForm()
    
    context = {
        'portfolios': portfolios,
        'form': form,
        'stock_data': stock_data,
        'market_data': market_data,
        'total_value': total_value,
        'total_cost': total_cost,
        'unrealized_gain_loss': unrealized_gain_loss,
        'return_percent': return_percent,
        'diversification': diversification,
    }
    return render(request, 'dashboard.html', context)


@login_required
def edit_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES, instance=portfolio)
        if form.is_valid():
            form.save()
            messages.success(request, f"Portfolio '{portfolio.name}' updated successfully!")
            return redirect('dashboard')
    else:
        form = PortfolioForm(instance=portfolio)
    return render(request, 'edit_portfolio.html', {'form': form, 'portfolio': portfolio})


@login_required
def delete_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    if request.method == 'POST':
        portfolio.delete()
        messages.success(request, f"Portfolio '{portfolio.name}' deleted successfully!")
        return redirect('dashboard')
    return render(request, 'delete_portfolio.html', {'portfolio': portfolio})



# Order execution view - requires login
@login_required
def execute_order(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    transactions = Transaction.objects.filter(portfolio=portfolio, status='PENDING')
    algos = AlgoStrategy.objects.filter(portfolio=portfolio)
    
    ts = TimeSeries(key=settings.ALPHA_VANTAGE_API_KEY, output_format='pandas')
    
    if request.method == 'POST':
        if 'order_form' in request.POST:
            form = OrderForm(request.POST)
            if form.is_valid():
                stock_ticker = form.cleaned_data['stock_ticker'].upper()
                quantity = form.cleaned_data['quantity']
                order_type = form.cleaned_data['order_type']
                type = form.cleaned_data['type']
                limit_price = form.cleaned_data['limit_price']
                strike_price = form.cleaned_data['strike_price']
                expiration_date = form.cleaned_data['expiration_date']
                use_margin = form.cleaned_data['use_margin']

                data, _ = ts.get_daily(symbol=stock_ticker, outputsize='compact')
                current_price = Decimal(str(data['4. close'].iloc[0]))

                stock, _ = Stock.objects.get_or_create(ticker=stock_ticker, defaults={'name': stock_ticker})
                stock.price = current_price
                stock.save()

                total_cost = current_price * quantity if order_type == 'MARKET' else (strike_price or limit_price or 0) * quantity
                margin_used = total_cost * Decimal('0.5') if use_margin and portfolio.margin_enabled else Decimal('0.00')

                transaction = Transaction.objects.create(
                    user=request.user,
                    stock=stock,
                    portfolio=portfolio,
                    type=type,
                    order_type=order_type,
                    quantity=quantity,
                    price=current_price if order_type == 'MARKET' else Decimal('0.00'),
                    limit_price=limit_price,
                    strike_price=strike_price,
                    expiration_date=expiration_date,
                    margin_used=margin_used,
                    status='EXECUTED' if order_type == 'MARKET' else 'PENDING'
                )

                if order_type == 'MARKET':
                    portfolio_stock, created = PortfolioStock.objects.get_or_create(
                        portfolio=portfolio, stock=stock, defaults={'purchase_price': current_price}
                    )
                    if type == 'BUY':
                        portfolio_stock.quantity += quantity
                    elif type == 'SELL' and portfolio_stock.quantity >= quantity:
                        portfolio_stock.quantity -= quantity
                    portfolio_stock.save()
                    if use_margin and portfolio.margin_enabled:
                        portfolio.margin_balance -= margin_used

                portfolio.save()
                messages.success(request, f"Order placed: {type} {quantity} shares of {stock_ticker} ({order_type})")
                return redirect('execute_order', portfolio_id=portfolio_id)

        elif 'algo_form' in request.POST:
            algo_form = AlgoStrategyForm(request.POST)
            if algo_form.is_valid():
                algo = algo_form.save(commit=False)
                algo.portfolio = portfolio
                algo.save()
                messages.success(request, f"Algo strategy '{algo.name}' added!")
                return redirect('execute_order', portfolio_id=portfolio_id)
    else:
        form = OrderForm()
        algo_form = AlgoStrategyForm()

    # Simple algo execution
    for algo in algos.filter(is_active=True):
        data, _ = ts.get_daily(symbol=algo.stock.ticker, outputsize='full')
        ma50 = data['4. close'].rolling(50).mean().iloc[-1]
        ma200 = data['4. close'].rolling(200).mean().iloc[-1]
        if algo.condition == "50-day MA > 200-day MA" and ma50 > ma200 and algo.action == 'BUY':
            Transaction.objects.create(
                user=request.user, stock=algo.stock, portfolio=portfolio,
                type='BUY', order_type='MARKET', quantity=algo.quantity,
                price=Decimal(str(data['4. close'].iloc[0])), status='EXECUTED'
            )
            messages.info(request, f"Algo executed: Buy {algo.quantity} {algo.stock.ticker}")

    context = {
        'portfolio': portfolio,
        'form': form,
        'algo_form': algo_form,
        'transactions': transactions,
        'algos': algos,
    }
    return render(request, 'stock_detail.html', context)

@login_required
def manage_algo_strategies(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    algos = AlgoStrategy.objects.filter(portfolio=portfolio)
    ts = TimeSeries(key=settings.ALPHA_VANTAGE_API_KEY, output_format='pandas')

    if request.method == 'POST':
        algo_form = AlgoStrategyForm(request.POST)
        if algo_form.is_valid():
            algo = algo_form.save(commit=False)
            algo.portfolio = portfolio
            algo.save()
            messages.success(request, f"Algo strategy '{algo.name}' added!")
            return redirect('manage_algo_strategies', portfolio_id=portfolio_id)
    else:
        algo_form = AlgoStrategyForm()

    # Simple algo execution (example: moving average crossover)
    for algo in algos.filter(is_active=True):
        data, _ = ts.get_daily(symbol=algo.stock.ticker, outputsize='full')
        ma50 = data['4. close'].rolling(50).mean().iloc[-1]
        ma200 = data['4. close'].rolling(200).mean().iloc[-1]
        if algo.condition == "50-day MA > 200-day MA" and ma50 > ma200 and algo.action == 'BUY':
            Transaction.objects.create(
                user=request.user, stock=algo.stock, portfolio=portfolio,
                type='BUY', order_type='MARKET', quantity=algo.quantity,
                price=Decimal(str(data['4. close'].iloc[0])), status='EXECUTED'
            )
            messages.info(request, f"Algo executed: Buy {algo.quantity} {algo.stock.ticker}")

    context = {
        'portfolio': portfolio,
        'algo_form': algo_form,
        'algos': algos,
    }
    return render(request, 'algo_strategies.html', context)

@login_required
def modify_order(request, portfolio_id, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, portfolio__id=portfolio_id, user=request.user, status='PENDING')
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            transaction.quantity = form.cleaned_data['quantity']
            transaction.type = form.cleaned_data['type']
            transaction.order_type = form.cleaned_data['order_type']
            transaction.limit_price = form.cleaned_data['limit_price'] if form.cleaned_data['order_type'] in ['LIMIT', 'STOP_LOSS'] else None
            transaction.save()
            messages.success(request, f"Order modified: {transaction}")
            return redirect('execute_order', portfolio_id=portfolio_id)
    else:
        form = OrderForm(initial={
            'stock_ticker': transaction.stock.ticker,
            'quantity': transaction.quantity,
            'type': transaction.type,
            'order_type': transaction.order_type,
            'limit_price': transaction.limit_price,
        })
    context = {'form': form, 'portfolio': transaction.portfolio, 'transaction': transaction}
    return render(request, 'modify_order.html', context)

@login_required
def cancel_order(request, portfolio_id, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, portfolio__id=portfolio_id, user=request.user, status='PENDING')
    if request.method == 'POST':
        transaction.status = 'CANCELED'
        transaction.save()
        messages.success(request, f"Order canceled: {transaction}")
        return redirect('execute_order', portfolio_id=portfolio_id)
    return render(request, 'cancel_order.html', {'transaction': transaction})

# Registration view
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

# Login view
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

# Logout view
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PortfolioStockViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioStockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PortfolioStock.objects.filter(portfolio__user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)