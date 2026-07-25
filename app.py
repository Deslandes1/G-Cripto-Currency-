# app.py
import streamlit as st
import database as db
import auth
import utils
import config
from datetime import datetime
import pandas as pd
import bcrypt

# Page config
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=config.APP_ICON,
    layout="wide"
)

# Initialize database
db.init_db()

# ====== CUSTOM CSS – LIGHT BLUE THEME ======
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #e3f2fd !important;
    }
    .stApp [data-testid="stAppViewContainer"] {
        background-color: transparent !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #bbdefb !important;
        border-right: 1px solid #90caf9;
    }
    [data-testid="stSidebar"] * {
        color: #0d47a1 !important;
    }
    .stSidebar .stButton > button {
        background: #64b5f6 !important;
        color: white !important;
    }

    /* Headers */
    h1, h2, h3, h4 {
        color: #0d47a1 !important;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > textarea,
    .stSelectbox > div > div {
        background: #ffffff !important;
        color: #0d47a1 !important;
        border: 1px solid #90caf9 !important;
        border-radius: 8px !important;
    }

    /* Buttons (primary) */
    .stButton > button {
        background: linear-gradient(105deg, #1e88e5 0%, #42a5f5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 40px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 20px rgba(30, 136, 229, 0.4);
    }

    /* Cards */
    .balance-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #ff6600;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        color: #0d47a1;
    }

    /* Main header – bright white text */
    .main-header {
        text-align: center;
        padding: 1.5rem 1rem;
        background: linear-gradient(135deg, #0d47a1, #42a5f5);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: #ffffff !important;
        font-size: 3rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin: 0;
    }
    .main-header p {
        color: #ffffff !important;
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.3rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #90caf9;
        color: #0d47a1;
    }
</style>
""", unsafe_allow_html=True)

# Header – bright white title
st.markdown(f"""
<div class="main-header">
    <h1>{config.APP_NAME}</h1>
    <p>Built by {config.BUILT_BY}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Haitian flag
    st.image(
        "https://raw.githubusercontent.com/Deslandes1/G-Cripto-Currency-/main/2000px-Flag_of_Haiti_1859%E2%80%931964.png",
        width=120
    )
    st.caption("🇭🇹 Haiti – G Cryptocurrency")
    st.markdown("---")
    st.markdown("### Navigation")

    if auth.is_logged_in():
        st.write(f"👤 {auth.get_current_user_email()}")
        if st.button("🚪 Logout"):
            auth.logout_user()
            st.rerun()
        menu = st.radio("Go to", ["Dashboard", "Exchange", "History", "Profile"])
    else:
        menu = st.radio("Go to", ["Login", "Sign Up"])

# Main content
if not auth.is_logged_in():
    if menu == "Login":
        st.subheader("🔐 Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                if auth.login_user(email, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    elif menu == "Sign Up":
        st.subheader("📝 Create Account")
        with st.form("signup_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Sign Up")
            if submit:
                if password != confirm:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    user_id = db.create_user(email, password)
                    if user_id:
                        st.success("Account created! Please log in.")
                        st.balloons()
                    else:
                        st.error("Email already exists")

else:
    user_id = auth.get_current_user_id()
    wallet = db.get_wallet(user_id)
    balance = wallet['balance'] if wallet else 0

    if menu == "Dashboard":
        st.subheader("📊 Dashboard")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="balance-card">
                <h3>💰 G Balance</h3>
                <h2>{utils.format_currency(balance)}</h2>
            </div>
            """, unsafe_allow_html=True)

        usd_rate = utils.get_exchange_rate('G', 'USD')
        usd_value = balance * usd_rate
        with col2:
            st.markdown(f"""
            <div class="balance-card">
                <h3>💵 USD Equivalent</h3>
                <h2>{utils.format_currency(usd_value, 'USD')}</h2>
            </div>
            """, unsafe_allow_html=True)

        eur_rate = utils.get_exchange_rate('G', 'EUR')
        eur_value = balance * eur_rate
        with col3:
            st.markdown(f"""
            <div class="balance-card">
                <h3>💶 EUR Equivalent</h3>
                <h2>{utils.format_currency(eur_value, 'EUR')}</h2>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📱 Quick Access")
        qr_data = config.QR_CODE_URL
        qr_image = utils.generate_qr_code(qr_data)
        st.image(qr_image, width=200)
        st.caption("Scan this QR code to open your dashboard on mobile")

    elif menu == "Exchange":
        st.subheader("🔄 Exchange G to Other Currencies")
        with st.form("exchange_form"):
            col1, col2 = st.columns(2)
            with col1:
                from_currency = st.selectbox("From", ["G", "USD", "EUR"])
                amount = st.number_input("Amount", min_value=0.0, step=0.01)
            with col2:
                to_currency = st.selectbox("To", ["G", "USD", "EUR"])
            submit = st.form_submit_button("Exchange")
            if submit:
                if amount <= 0:
                    st.error("Amount must be positive")
                elif from_currency == to_currency:
                    st.error("Currencies must be different")
                else:
                    if from_currency == "G" and amount > balance:
                        st.error("Insufficient G balance")
                    else:
                        rate = utils.get_exchange_rate(from_currency, to_currency)
                        converted = amount * rate
                        if from_currency == "G":
                            new_balance = balance - amount
                            db.update_balance(user_id, new_balance)
                            db.add_transaction(user_id, 'sell', amount, 'G', to_currency, rate)
                        elif to_currency == "G":
                            new_balance = balance + converted
                            db.update_balance(user_id, new_balance)
                            db.add_transaction(user_id, 'buy', converted, from_currency, 'G', rate)
                        else:
                            db.add_transaction(user_id, 'exchange', amount, from_currency, to_currency, rate)
                        st.success(f"Exchanged {amount} {from_currency} to {converted:.2f} {to_currency} at rate {rate:.4f}")
                        st.rerun()

    elif menu == "History":
        st.subheader("📜 Transaction History")
        transactions = db.get_transactions(user_id)
        if transactions:
            df = pd.DataFrame(transactions)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['timestamp', 'type', 'amount', 'currency_from', 'currency_to', 'rate']]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No transactions yet")

    elif menu == "Profile":
        st.subheader("👤 Profile")
        st.write(f"**Email:** {auth.get_current_user_email()}")
        st.write(f"**User ID:** {user_id}")
        st.markdown("---")
        st.subheader("Change Password")
        with st.form("change_password"):
            old = st.text_input("Current Password", type="password")
            new = st.text_input("New Password", type="password")
            confirm = st.text_input("Confirm New Password", type="password")
            submit = st.form_submit_button("Update Password")
            if submit:
                user = db.get_user_by_id(user_id)
                if user and bcrypt.checkpw(old.encode('utf-8'), user['password_hash']):
                    if new == confirm and len(new) >= 6:
                        hashed = bcrypt.hashpw(new.encode('utf-8'), bcrypt.gensalt())
                        conn = db.get_db_connection()
                        c = conn.cursor()
                        c.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hashed, user_id))
                        conn.commit()
                        conn.close()
                        st.success("Password updated!")
                    else:
                        st.error("New password must match and be at least 6 characters")
                else:
                    st.error("Current password is incorrect")

# Footer
st.markdown(f"""
<div class="footer">
    <p>{config.APP_NAME} v{config.APP_VERSION} | Built by {config.BUILT_BY}</p>
    <p>📧 {config.APP_NAME.lower().replace(' ', '')}@globalinternet.py</p>
</div>
""", unsafe_allow_html=True)
