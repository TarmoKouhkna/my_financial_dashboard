# models.py

from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def total_value(self):
        return sum(security.todays_value for security in self.security_set.all())

    def total_gain_loss_percentage(self):
        total_investment = Decimal('0.0')
        total_current_value = Decimal('0.0')

        for security in self.security_set.all():
            total_investment += security.purchase_price * security.amount
            total_current_value += Decimal(security.todays_value)

        if total_investment > 0:
            return ((total_current_value - total_investment) / total_investment) * 100
        return Decimal('0.0')

    def __str__(self):
        return self.name


class Security(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker_symbol = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255, default="Unknown")  # Add this field
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.IntegerField()
    todays_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def gain_percentage(self):
        if self.purchase_price > 0:
            todays_value_decimal = Decimal(self.todays_value)
            return ((todays_value_decimal - (self.purchase_price * self.amount)) / (
                    self.purchase_price * self.amount)) * 100
        return Decimal('0.0')

    def __str__(self):
        return self.ticker_symbol
