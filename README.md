# My Financial Dashboard

## Introduction

My Financial Dashboard is a Django-based web application that allows users to create and manage their stock portfolios. The app provides features like tracking the performance of individual stocks, displaying historical stock prices using Plotly graphs, and managing user accounts.

## Features

- **User Authentication:** Register, login, and manage your account.
- **Portfolio Management:** Create multiple portfolios, add stocks, and track their performance.
- **Stock Performance Visualization:** View historical stock prices on interactive graphs.
- **Real-time Stock Price Fetching:** Automatically fetch the latest stock prices using an API.
- **Responsive UI:** A user-friendly interface designed using custom CSS.

## Prerequisites

Before setting up the project, make sure you have the following installed:

- Python 3.7 or higher
- Django 5.1
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/my_financial_dashboard.git
    ```
2. **Navigate to the project directory:**
    ```bash
    cd my_financial_dashboard
    ```
3. **Set up a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
4. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5. **Set up the database:**
    ```bash
    python manage.py migrate
    ```
6. **Create a superuser (admin account):**
    ```bash
    python manage.py createsuperuser
    ```
7. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

8. **Access the application:**
   Open your web browser and navigate to `http://127.0.0.1:8000`.

## Deployment

### 1. Whitenoise Setup

This project uses Whitenoise for serving static files in production. Ensure you have Whitenoise installed:

```bash
pip install whitenoise
