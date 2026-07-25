# app.py
import streamlit as st
import database as db
import auth
import utils
import config
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=config.APP_ICON,
    layout="wide"
)

# Initialize database
db.init_db()

# CSS for professional look
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .sidebar-info {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .balance-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #ff6600;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .qr-code {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #ddd;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="main-header">
    <h1>{config.APP_NAME}</h1>
    <p>Built by {config.BUILT_BY}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x150?text=G", width=150)
    st.markdown("### Navigation")

    if auth.is_logged_in():
        user_email = auth.get_current_user_email()
        st.write(f"👤 {user_email}")
        if st.button("🚪 Logout"):
            auth.logout_user()
            st.rerun()
        # Dashboard menu
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

        # Get USD equivalent
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

        # QR Code
        st.markdown("### 📱 Quick Access")
        st.write("Scan this QR code to open your dashboard on mobile (or share with others)")
        qr_data = config.QR_CODE_URL  # You can append user-specific token if needed
        qr_image = utils.generate_qr_code(qr_data)
        st.image(qr_image, width=200)
        st.caption("Scan to visit the app")

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
                    # Check balance if selling G
                    if from_currency == "G" and amount > balance:
                        st.error("Insufficient G balance")
                    else:
                        # Get rate
                        rate = utils.get_exchange_rate(from_currency, to_currency)
                        converted = amount * rate
                        # Update balance if from_currency == G
                        if from_currency == "G":
                            new_balance = balance - amount
                            db.update_balance(user_id, new_balance)
                            db.add_transaction(user_id, 'sell', amount, 'G', to_currency, rate)
                        elif to_currency == "G":
                            # Buying G with other currency
                            new_balance = balance + converted
                            db.update_balance(user_id, new_balance)
                            db.add_transaction(user_id, 'buy', converted, from_currency, 'G', rate)
                        else:
                            # Non-G exchange: not directly affecting G balance, but we can still record
                            # For simplicity, we'll just simulate a transaction without changing G balance
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
        st.write(f"**Account Created:** (retrieve from DB if needed)")

        # Option to change password (simplified)
        st.markdown("---")
        st.subheader("Change Password")
        with st.form("change_password"):
            old = st.text_input("Current Password", type="password")
            new = st.text_input("New Password", type="password")
            confirm = st.text_input("Confirm New Password", type="password")
            submit = st.form_submit_button("Update Password")
            if submit:
                # Verify old password
                user = db.get_user_by_id(user_id)
                if user and bcrypt.checkpw(old.encode('utf-8'), user['password_hash']):
                    if new == confirm and len(new) >= 6:
                        hashed = bcrypt.hashpw(new.encode('utf-8'), bcrypt.gensalt())
                        # Update in DB (add a function)
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
