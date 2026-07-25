# database.py
import sqlite3
import bcrypt
from datetime import datetime
import config

def get_db_connection():
    conn = sqlite3.connect('g_crypto.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            currency TEXT DEFAULT 'G',
            balance REAL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            currency_from TEXT,
            currency_to TEXT,
            rate REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def create_user(email, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, hashed))
        user_id = c.lastrowid
        c.execute('INSERT INTO wallets (user_id, balance) VALUES (?, ?)', (user_id, config.INITIAL_BALANCE))
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user(email, password):
    conn = get_db_connection()
    c = conn.cursor()
    user = c.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
        return dict(user)
    return None

def get_user_by_id(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    user = c.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_wallet(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    wallet = c.execute('SELECT * FROM wallets WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(wallet) if wallet else None

def update_balance(user_id, new_balance):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE wallets SET balance = ? WHERE user_id = ?', (new_balance, user_id))
    conn.commit()
    conn.close()

def add_transaction(user_id, tx_type, amount, currency_from=None, currency_to=None, rate=None):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (user_id, type, amount, currency_from, currency_to, rate)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, tx_type, amount, currency_from, currency_to, rate))
    conn.commit()
    conn.close()

def get_transactions(user_id, limit=50):
    conn = get_db_connection()
    c = conn.cursor()
    txs = c.execute('''
        SELECT * FROM transactions WHERE user_id = ?
        ORDER BY timestamp DESC LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return [dict(tx) for tx in txs]
