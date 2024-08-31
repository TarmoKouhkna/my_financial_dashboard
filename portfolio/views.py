from django.shortcuts import render, redirect, get_object_or_404
from .models import Portfolio, Security
from .forms import AddStockForm, PortfolioForm
import requests
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.views import View
from django.conf import settings
from decimal import Decimal, InvalidOperation
import urllib.parse
import plotly.graph_objs as go
import logging
import json
from plotly.utils import PlotlyJSONEncoder


logger = logging.getLogger(__name__)


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


def portfolio_detail(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)

    if request.method == 'POST':
        if 'delete_stock' in request.POST:
            stock_id = request.POST.get('stock_id')
            stock = get_object_or_404(Security, id=stock_id, portfolio=portfolio)
            stock.delete()
            return redirect('portfolio_detail', pk=portfolio.pk)

        form = AddStockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.portfolio = portfolio
            current_price = get_current_price(stock.ticker_symbol)
            if current_price is not None:
                stock.todays_value = current_price * stock.amount
            else:
                stock.todays_value = 0.0  # Set to 0 if the price could not be fetched

            # Manually entered company name will be saved directly from the form
            stock.save()
            return redirect('portfolio_detail', pk=portfolio.pk)
    else:
        form = AddStockForm()

    stocks = portfolio.security_set.all()

    # Prepare Plotly data
    traces = []
    plotly_data = []
    for stock in stocks:
        current_price = get_current_price(stock.ticker_symbol)
        if current_price:
            stock.todays_value = current_price * stock.amount
            stock.save()

            # Fetch historical data for the stock
            url = f'https://eodhistoricaldata.com/api/eod/{stock.ticker_symbol}.US?api_token={settings.API_KEY}&fmt=json&period=d&from=2024-01-01&to=2024-12-31'
            response = requests.get(url)
            data = response.json()

            # Assume data comes as a list of dicts
            dates = [entry['date'] for entry in data]
            closing_prices = [entry['close'] for entry in data]

            trace = go.Scatter(x=dates, y=closing_prices, mode='lines', name=stock.ticker_symbol)
            traces.append(trace)

            # Add to plotly_data for JSON serialization
            plotly_data.append(trace)

    total_value = sum(stock.todays_value for stock in stocks)

    # Serialize Plotly data to JSON
    plotly_data_json = json.dumps(plotly_data, cls=PlotlyJSONEncoder)  # Use the correct encoder

    context = {
        'portfolio': portfolio,
        'stocks': stocks,
        'total_value': total_value,
        'form': form,
        'plotly_data_json': plotly_data_json,  # Pass the serialized data to the template
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
