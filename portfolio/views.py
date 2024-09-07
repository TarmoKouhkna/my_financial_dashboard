import json
from decimal import Decimal
import logging
import urllib.parse
from decimal import Decimal, InvalidOperation
import requests
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import AddStockForm, PortfolioForm
from .models import Portfolio, Security
from datetime import datetime
from django.db.models import Sum


def index(request):
    return render(request, 'portfolio/index.html')


def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolio/portfolio_list.html', {'portfolios': portfolios})


def get_current_price(ticker_symbol):
    # Append '.US' to the ticker symbol to ensure correct market identification
    formatted_symbol = f"{ticker_symbol}.US"

    # Encode the ticker symbol to safely include it in the URL
    encoded_symbol = urllib.parse.quote(formatted_symbol)
    url = f'https://eodhd.com/api/real-time/{encoded_symbol}?api_token={settings.API_KEY}&fmt=json'

    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Debug output: print the API response
        print(f"API response for {ticker_symbol}: {data}")

        # Attempt to get the 'last' price, if available, otherwise fall back to 'close'
        last_price = data.get('last') or data.get('close')

        if last_price is not None:
            try:
                # Convert the price to a Decimal for precision
                return Decimal(str(last_price))
            except InvalidOperation:
                print(f"Error converting price to decimal for ticker symbol {ticker_symbol}")
                return Decimal('0.0')  # Return 0.0 if conversion fails
        else:
            print(f"No price data available for ticker symbol {ticker_symbol}")
            return Decimal('0.0')

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for ticker symbol {ticker_symbol}: {e}")
    except ValueError as e:
        print(f"Error decoding JSON for ticker symbol {ticker_symbol}: {e}")

    # Return 0.0 if there was an error or no data
    return Decimal('0.0')


import json
from decimal import Decimal


def portfolio_detail(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)
    stocks = portfolio.security_set.all()
    form = AddStockForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            stock = form.save(commit=False)
            stock.portfolio = portfolio
            stock.save()
            return redirect('portfolio_detail', pk=portfolio.pk)

    plot_data = []  # Will store data for each stock to send to the template
    purchase_dates = [stock.purchase_date for stock in stocks if stock.purchase_date]  # Collect purchase dates

    # Handle the case where there are no purchase dates
    if purchase_dates:
        earliest_purchase_date = min(purchase_dates)  # Find the earliest purchase date
    else:
        earliest_purchase_date = None  # Set to None if there are no purchase dates

    # Initialize total_value before the loop
    total_value = 0.0  # Set it to 0.0 initially to avoid UnboundLocalError

    # Prepare data for the pie chart
    pie_data = []

    # Calculate total portfolio value directly from the database
    if stocks.exists():  # Ensure there are stocks before summing
        total_value = stocks.aggregate(Sum('todays_value'))['todays_value__sum'] or 0.0  # Sum the todays_value

        # Prepare data for pie chart and plot data
        for stock in stocks:
            if total_value > 0 and stock.todays_value:
                percentage = float((stock.todays_value / total_value) * 100)  # Convert percentage to float
                pie_data.append({
                    'name': stock.ticker_symbol,  # Stock symbol for pie chart
                    'y': percentage  # This is the percentage value for the pie chart
                })

            current_price = get_current_price(stock.ticker_symbol)
            if current_price:
                stock.todays_value = current_price * stock.amount
                stock.save()

                # Fetch historical data for the stock (dates and prices)
                url = f'https://eodhistoricaldata.com/api/eod/{stock.ticker_symbol}.US?api_token={settings.API_KEY}&fmt=json&period=d&from=2024-01-01&to=2024-12-31'
                response = requests.get(url)
                data = response.json()

                # Prepare the data for Highcharts
                dates = [entry['date'] for entry in data]
                closing_prices = [entry['close'] for entry in data]

                # Append stock data to plot_data list
                plot_data.append({
                    'name': stock.ticker_symbol,  # Stock symbol (used for the series name)
                    'data': list(zip(dates, closing_prices))  # Highcharts expects a list of (date, price) pairs
                })

        # Handle stock deletion
        if request.method == 'POST' and 'delete_stock' in request.POST:
            stock_id = request.POST.get('delete_stock')
            stock_to_delete = get_object_or_404(Security, id=stock_id, portfolio=portfolio)
            stock_to_delete.delete()
            return redirect('portfolio_detail', pk=portfolio.pk)

    # If there's an earliest purchase date, format it. Otherwise, set it to None for the template.
    earliest_purchase_date_str = earliest_purchase_date.strftime('%Y-%m-%d') if earliest_purchase_date else None

    # Convert Decimal values in the pie_data to floats and prepare the context
    context = {
        'portfolio': portfolio,
        'form': form,  # Pass the form to the template
        'stocks': stocks,
        'plot_data_json': json.dumps(plot_data),  # Pass the serialized plot data to the template
        'pie_data_json': json.dumps(pie_data),  # Pass pie chart data as JSON
        'earliest_purchase_date': earliest_purchase_date_str,  # Pass the earliest purchase date as a string or None
        'total_value': float(total_value),  # Convert total_value to float to avoid Decimal issues
    }

    return render(request, 'portfolio/portfolio_detail.html', context)


def portfolio_add(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            return redirect('portfolio_list')
    else:
        form = PortfolioForm()
    return render(request, 'portfolio/portfolio_add.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


class CustomLogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('index')  # Redirect to homepage after logout
