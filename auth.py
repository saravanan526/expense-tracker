import hashlib
import hmac
import os
import re

import mysql.connector
import streamlit as st

import database as db

ITERATIONS = 200_000          # how many times PBKDF2 repeats (makes guessing slower)


# ---------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------
def hash_password(password):
    """Return 'salt$hash' (both in hex). A new random salt is used for every user."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return salt.hex() + "$" + digest.hex()


def verify_password(password, stored_value):
    """Check a password against the stored 'salt$hash' value."""
    try:
        salt_hex, hash_hex = stored_value.split("$")
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return hmac.compare_digest(digest.hex(), hash_hex)


# ---------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------
def validate_registration(full_name, username, email, password, confirm_password):
    """Return a list of error messages (empty list = everything is valid)."""
    errors = []

    if not full_name.strip():
        errors.append("Full name cannot be empty.")

    if not re.fullmatch(r"[A-Za-z0-9_]{3,30}", username.strip()):
        errors.append("Username must be 3-30 characters (letters, numbers and underscore only).")

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
        errors.append("Please enter a valid email address.")

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    elif not (re.search(r"[A-Za-z]", password) and re.search(r"[0-9]", password)):
        errors.append("Password must contain at least one letter and one number.")

    if password != confirm_password:
        errors.append("Password and confirm password do not match.")

    return errors


def register_user(full_name, username, email, password, confirm_password):
    """Return (True, []) on success or (False, [error messages])."""
    errors = validate_registration(full_name, username, email, password, confirm_password)
    if errors:
        return False, errors

    username = username.strip().lower()      # usernames are not case-sensitive
    email = email.strip().lower()

    if db.username_exists(username):
        return False, ["This username is already taken."]
    if db.email_exists(email):
        return False, ["An account with this email already exists."]

    try:
        db.create_user(full_name.strip(), username, email, hash_password(password))
    except mysql.connector.IntegrityError:
        # Happens only if two people register the same username at the same moment
        return False, ["This username or email is already registered."]
    return True, []


# ---------------------------------------------------------------------
# Login / logout
# ---------------------------------------------------------------------
def login_user(username, password):
    """Return (user_dict, None) on success or (None, error message)."""
    if not username.strip() or not password:
        return None, "Please enter username and password."

    user = db.get_user_by_username(username.strip().lower())

    # Same message for a wrong username and a wrong password (do not give hints)
    if user is None or not verify_password(password, user["password_hash"]):
        return None, "Invalid username or password."

    return {"id": user["id"], "full_name": user["full_name"], "username": user["username"]}, None


def set_user(user):
    st.session_state["user"] = user


def is_logged_in():
    return "user" in st.session_state


def get_user():
    return st.session_state["user"]


def get_user_id():
    return st.session_state["user"]["id"]


def logout():
    """Clear everything stored in the session (used as a button callback)."""
    st.session_state.clear()
