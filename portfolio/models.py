from django.db import models
from django.contrib.auth.models import User


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def total_value(self):
        return sum(security.todays_value for security in self.security_set.all())

    def __str__(self):
        return self.name


class Security(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker_symbol = models.CharField(max_length=10)
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.IntegerField()
    todays_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.ticker_symbol
