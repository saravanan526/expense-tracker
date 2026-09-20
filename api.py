"""
api.py
------
Currency converter using a public REST API and the requests library.

API used: https://open.er-api.com  (free, no API key needed)
Example: https://open.er-api.com/v6/latest/USD

If you switch to an API that needs a key, store the key in the .env file
and read it with os.getenv() - never write it inside the code.
"""

import requests

API_URL = "https://open.er-api.com/v6/latest/{}"
CURRENCIES = ["USD", "EUR", "GBP", "AED", "SGD", "AUD", "CAD", "JPY"]


def get_exchange_rate(from_currency, to_currency="INR"):
    """
    Return (rate, error_message).
    On success  -> (83.12, None)
    On failure  -> (None, "message to show the user")
    """
    url = API_URL.format(from_currency)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()          # raises error for 4xx / 5xx status codes
        data = response.json()
    except requests.exceptions.Timeout:
        return None, "The request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return None, "Could not connect to the internet / API server."
    except requests.exceptions.RequestException as error:
        return None, f"API request failed: {error}"

    if data.get("result") != "success":
        return None, "The API did not return valid data."

    rate = data.get("rates", {}).get(to_currency)
    if rate is None:
        return None, f"Exchange rate for {to_currency} was not found."

    return float(rate), None


def convert_to_inr(amount, from_currency):
    """Return (rate, converted_amount, error_message)."""
    rate, error = get_exchange_rate(from_currency, "INR")
    if error:
        return None, None, error
    return rate, amount * rate, None
