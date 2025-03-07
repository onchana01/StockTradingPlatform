from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Transaction, Portfolio, AlgoStrategy

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Enter a valid email address.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class OrderForm(forms.Form):
    stock_ticker = forms.CharField(max_length=10, label="Stock Ticker")
    quantity = forms.IntegerField(min_value=1, label="Quantity")
    type = forms.ChoiceField(choices=Transaction.TYPE_CHOICES, label="Buy/Sell")
    order_type = forms.ChoiceField(
        choices=Transaction.ORDER_TYPE_CHOICES,
        label="Order Type",
        widget=forms.Select(attrs={'onchange': 'toggleLimitPrice(this)'})
    )
    limit_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Limit/Stop Price")
    strike_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Strike Price")
    expiration_date = forms.DateField(required=False, label="Expiration Date", widget=forms.DateInput(attrs={'type': 'date'}))
    use_margin = forms.BooleanField(required=False, label="Use Margin")

    def clean(self):
        cleaned_data = super().clean()
        order_type = cleaned_data.get('order_type')
        limit_price = cleaned_data.get('limit_price')
        strike_price = cleaned_data.get('strike_price')
        expiration_date = cleaned_data.get('expiration_date')
        if order_type in ['LIMIT', 'STOP_LOSS'] and not limit_price:
            raise forms.ValidationError("Limit/Stop Price is required for Limit and Stop-Loss orders.")
        if order_type in ['CALL_OPTION', 'PUT_OPTION'] and not (strike_price and expiration_date):
            raise forms.ValidationError("Strike Price and Expiration Date are required for options.")
        return cleaned_data

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Portfolio Name'}),
            'image': forms.FileInput(),
        }

class AlgoStrategyForm(forms.ModelForm):
    class Meta:
        model = AlgoStrategy
        fields = ['name', 'stock', 'condition', 'action', 'quantity', 'is_active']
        widgets = {
            'condition': forms.TextInput(attrs={'placeholder': 'e.g., 50-day MA > 200-day MA'}),
        }