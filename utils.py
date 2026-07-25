# utils.py
import requests
import qrcode
from io import BytesIO
import config

def get_exchange_rate(from_currency, to_currency):
    if from_currency == to_currency:
        return 1.0
    # Try free exchangerate.host API
    try:
        url = "https://api.exchangerate.host/latest"
        params = {"base": "USD", "symbols": f"{from_currency},{to_currency}"}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get('success'):
            rates = data.get('rates', {})
            if from_currency in rates and to_currency in rates:
                return rates[to_currency] / rates[from_currency]
    except:
        pass
    # Fallback (silent)
    return get_fallback_rate(from_currency, to_currency)

def get_fallback_rate(from_currency, to_currency):
    fallback_rates = {
        "USD": 1.0, "EUR": 0.92, "G": 130.0, "HTG": 130.0,
        "GBP": 0.79, "CAD": 1.36, "JPY": 149.5,
    }
    if from_currency in fallback_rates and to_currency in fallback_rates:
        return fallback_rates[to_currency] / fallback_rates[from_currency]
    return 1.0

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
