# config.py
import os

APP_NAME = "G Cryptocurrency Exchange"
APP_ICON = "💰"
APP_VERSION = "1.0.0"
BUILT_BY = "Gesner Deslandes – Haiti National Patrimoine"

INITIAL_BALANCE = 1000.0

# Fixer.io API key (get yours at https://fixer.io)
# For free plan, base currency is always EUR.
FIXER_API_KEY = os.environ.get("FIXER_API_KEY", "your_api_key_here")

# Fallback exchange rates (used when API fails)
FALLBACK_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "G": 130.0,      # 1 USD = 130 G (HTG)
    "HTG": 130.0,
    "GBP": 0.79,
    "CAD": 1.36,
    "JPY": 149.5,
}

# QR code URL (your deployed app URL)
QR_CODE_URL = "https://g-crypto-exchange.streamlit.app/"  # replace with yours
