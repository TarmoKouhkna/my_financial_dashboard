from django import forms
from .models import Portfolio, Security


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name']


class SecurityForm(forms.ModelForm):
    class Meta:
        model = Security
        fields = ['ticker_symbol', 'purchase_date', 'purchase_price', 'amount']


class AddStockForm(forms.ModelForm):
    class Meta:
        model = Security
        fields = ['ticker_symbol', 'purchase_date', 'purchase_price', 'amount']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'ticker_symbol': 'Ticker Symbol',
            'purchase_date': 'Purchase Date',
            'purchase_price': 'Purchase Price',
            'amount': 'Amount',
        }
