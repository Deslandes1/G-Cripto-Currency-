# utils.py
import requests
import qrcode
from io import BytesIO
import streamlit as st
import config

def get_exchange_rate(from_currency, to_currency):
    """
    Récupère le taux de change en temps réel.
    Priorité :
    1. API gratuite exchangerate.host (sans clé, sans limite)
    2. Si échec, taux de secours fixes (silencieux)
    """
    if from_currency == to_currency:
        return 1.0

    # --- 1. Essayer l'API gratuite exchangerate.host ---
    try:
        url = "https://api.exchangerate.host/latest"
        params = {
            "base": "USD",
            "symbols": f"{from_currency},{to_currency}"
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get('success'):
            rates = data.get('rates', {})
            if from_currency in rates and to_currency in rates:
                # Taux croisé via USD
                return rates[to_currency] / rates[from_currency]
    except Exception:
        # Échec silencieux – on passe aux taux de secours
        pass

    # --- 2. Taux de secours (aucun message affiché) ---
    return get_fallback_rate(from_currency, to_currency)

def get_fallback_rate(from_currency, to_currency):
    """Taux de secours fixes (silencieux)"""
    fallback_rates = {
        "USD": 1.0,
        "EUR": 0.92,
        "G": 130.0,      # 1 USD = 130 G (HTG)
        "HTG": 130.0,
        "GBP": 0.79,
        "CAD": 1.36,
        "JPY": 149.5,
    }
    if from_currency in fallback_rates and to_currency in fallback_rates:
        return fallback_rates[to_currency] / fallback_rates[from_currency]
    return 1.0   # valeur par défaut

# --- Les autres fonctions (generate_qr_code, format_currency) restent inchangées ---

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
