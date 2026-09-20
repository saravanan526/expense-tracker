"""Login / Register page. This is the only page shown before logging in."""

import streamlit as st

import auth


def show():
    st.title("Expense Tracker and Data Analytics Dashboard")
    st.write("Please login or create an account to continue.")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    # ---- Login ----
    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_clicked = st.form_submit_button("Login")

        if login_clicked:
            user, error = auth.login_user(username, password)
            if error:
                st.error(error)
            else:
                auth.set_user(user)
                st.rerun()                  # reload the app, now with the full menu

    # ---- Register ----
    with tab_register:
        with st.form("register_form"):
            full_name = st.text_input("Full name", max_chars=100)
            new_username = st.text_input("Username", max_chars=30,
                                         help="3-30 characters: letters, numbers, underscore")
            email = st.text_input("Email", max_chars=100)
            new_password = st.text_input("Password", type="password",
                                         help="At least 8 characters with a letter and a number")
            confirm_password = st.text_input("Confirm password", type="password")
            register_clicked = st.form_submit_button("Create Account")

        if register_clicked:
            success, errors = auth.register_user(full_name, new_username, email,
                                                 new_password, confirm_password)
            if success:
                st.success("Account created successfully. Please go to the Login tab and login.")
            else:
                for message in errors:
                    st.error(message)
