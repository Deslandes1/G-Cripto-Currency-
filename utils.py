# utils.py
import requests
import qrcode
from io import BytesIO
import streamlit as st
import config

def get_exchange_rate(from_currency, to_currency):
    """
    Get real-time exchange rate using fixer.io (free plan).
    If API fails, falls back to fixed rates.
    """
    if from_currency == to_currency:
        return 1.0

    # If fixer API key is not set or is default, use fallback
    if config.FIXER_API_KEY == "your_api_key_here":
        return get_fallback_rate(from_currency, to_currency)

    url = "https://data.fixer.io/api/latest"
    params = {
        "access_key": config.FIXER_API_KEY,
        "symbols": f"{from_currency},{to_currency}"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get('success'):
            rates = data.get('rates', {})
            # Free plan always returns rates relative to EUR
            # So we need to compute cross rates
            # If from_currency == 'EUR', direct rate is rates[to_currency]
            # Else: rate = rates[to_currency] / rates[from_currency]
            if from_currency == 'EUR':
                return rates.get(to_currency, 1.0)
            elif from_currency in rates and to_currency in rates:
                return rates[to_currency] / rates[from_currency]
            else:
                return get_fallback_rate(from_currency, to_currency)
        else:
            st.warning(f"Fixer API error: {data.get('error', {}).get('info', 'Unknown')}")
            return get_fallback_rate(from_currency, to_currency)
    except Exception as e:
        st.warning(f"Could not fetch live rates, using fallback: {e}")
        return get_fallback_rate(from_currency, to_currency)

def get_fallback_rate(from_currency, to_currency):
    """Fallback rates when API is unavailable"""
    rates = config.FALLBACK_RATES
    # Convert both to USD first, then compute
    if from_currency in rates and to_currency in rates:
        return rates[to_currency] / rates[from_currency]
    return 1.0  # fallback to 1:1

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def format_currency(amount, currency='G'):
    if currency == 'G' or currency == 'HTG':
        return f"G {amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"
