# auth.py
import streamlit as st
import database as db

def login_user(email, password):
    user = db.get_user(email, password)
    if user:
        st.session_state['user_id'] = user['id']
        st.session_state['user_email'] = user['email']
        st.session_state['logged_in'] = True
        return True
    return False

def logout_user():
    for key in ['user_id', 'user_email', 'logged_in']:
        if key in st.session_state:
            del st.session_state[key]

def is_logged_in():
    return st.session_state.get('logged_in', False)

def get_current_user_id():
    return st.session_state.get('user_id')

def get_current_user_email():
    return st.session_state.get('user_email', '')
