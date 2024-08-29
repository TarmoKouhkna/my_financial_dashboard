from django.shortcuts import render, redirect, get_object_or_404
from .models import Portfolio, Security
from .forms import AddStockForm, PortfolioForm
import requests
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm  # Import UserCreationForm from Django
from django.views import View
from django.conf import settings  # Import settings to access API_KEY


def index(request):
    return render(request, 'portfolio/index.html')


def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolio/portfolio_list.html', {'portfolios': portfolios})


def get_current_price(ticker_symbol):
    url = f'https://eodhd.com/api/real-time/{ticker_symbol}?api_token={settings.API_KEY}&fmt=json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Attempt to get the 'last' price, if available, otherwise fall back to 'close'
        last_price = data.get('last') or data.get('close')
        if last_price is not None:
            return last_price
        else:
            print(f"No price data available for ticker symbol {ticker_symbol}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for ticker symbol {ticker_symbol}: {e}")
    except ValueError as e:
        print(f"Error decoding JSON for ticker symbol {ticker_symbol}: {e}")

    # Return None if there was an error or no data
    return None


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
            stock.save()
            return redirect('portfolio_detail', pk=portfolio.pk)
    else:
        form = AddStockForm()

    stocks = portfolio.security_set.all()

    # Update today's value for each stock
    for stock in stocks:
        current_price = get_current_price(stock.ticker_symbol)
        if current_price:
            stock.todays_value = current_price * stock.amount
            stock.save()

    total_value = sum(stock.todays_value for stock in stocks)

    context = {
        'portfolio': portfolio,
        'stocks': stocks,
        'total_value': total_value,
        'form': form,
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
