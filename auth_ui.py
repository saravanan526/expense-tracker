"""
auth_ui.py - Login / Register screen and sidebar user card.

Works with your existing auth.py (no changes needed there).

Usage in app.py:

    import streamlit as st
    import auth
    import auth_ui

    st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")
    auth_ui.apply_theme()

    if not auth.is_logged_in():
        auth_ui.render_auth_page()
        st.stop()

    auth_ui.render_sidebar_user()
    # ... rest of your dashboard ...
"""

import streamlit as st

import auth

GREEN = "#0F5C4D"        # brand colour (deep green - money / growth)
GREEN_DARK = "#35440A"
INK = "#1F2A2E"
MUTED = "#6B7780"
LINE = "#E3E8E6"
SOFT = "#F3F7F6"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
    color: {INK};
}}
.stApp {{ background: #FFFFFF; }}

/* hide default Streamlit chrome */
#MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
.block-container {{ padding-top: 2.5rem; padding-bottom: 2rem; max-width: 1050px; }}

/* ---------- left brand panel ---------- */
.brand-panel {{
    background: {GREEN};
    color: #fff;
    border-radius: 20px;
    padding: 2.6rem 2.2rem;
    min-height: 560px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}
.brand-logo {{ font-size: 1.05rem; font-weight: 700; letter-spacing: .2px; }}
.brand-logo span {{
    display: inline-block; width: 30px; height: 30px; line-height: 30px;
    text-align: center; background: #fff; color: {GREEN};
    border-radius: 8px; margin-right: .6rem; font-weight: 800;
}}
.brand-title {{
    font-size: 2.1rem; line-height: 1.2; font-weight: 800;
    margin: 2.2rem 0 .8rem 0; letter-spacing: -.5px;
}}
.brand-sub {{ color: #CFE5DF; font-size: .98rem; line-height: 1.6; max-width: 340px; }}

/* small preview of what the app tracks */
.preview {{
    background: rgba(255,255,255,.10);
    border: 1px solid rgba(255,255,255,.18);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    margin-top: 2rem;
}}
.preview-head {{ font-size: .8rem; color: #CFE5DF; margin-bottom: .6rem; }}
.row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: .5rem 0; font-size: .92rem;
    border-top: 1px solid rgba(255,255,255,.12);
}}
.row:first-of-type {{ border-top: none; }}
.row b {{ font-weight: 600; }}
.bar {{ height: 6px; border-radius: 6px; background: rgba(255,255,255,.18); margin-top: .35rem; }}
.bar i {{ display: block; height: 100%; border-radius: 6px; background: #8EE0C6; }}

/* ---------- right form side ---------- */
.form-title {{ font-size: 1.7rem; font-weight: 800; letter-spacing: -.4px; margin-bottom: .2rem; }}
.form-sub {{ color: {MUTED}; font-size: .95rem; margin-bottom: 1.2rem; }}

/* tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 1.4rem; border-bottom: 1px solid {LINE}; }}
.stTabs [data-baseweb="tab"] {{
    font-weight: 600; color: {MUTED}; padding: .6rem .1rem; background: transparent;
}}
.stTabs [aria-selected="true"] {{ color: {GREEN}; }}
.stTabs [data-baseweb="tab-highlight"] {{ background-color: {GREEN}; height: 3px; }}

/* form container: remove Streamlit's default box */
[data-testid="stForm"] {{ border: none; padding: 0; }}

/* inputs */
.stTextInput label p {{ font-size: .85rem; font-weight: 600; color: {INK}; }}
.stTextInput input {{
    border-radius: 10px; border: 1.5px solid {LINE}; background: #fff;
    padding: .7rem .85rem; font-size: .95rem;
}}
.stTextInput div[data-baseweb="input"] {{ border: none; background: transparent; }}
.stTextInput input:focus {{
    border-color: {GREEN}; box-shadow: 0 0 0 3px rgba(15,92,77,.15);
}}

/* buttons */
div[data-testid="stFormSubmitButton"] button, .stButton button {{
    background: {GREEN}; color: #fff; border: none; border-radius: 10px;
    padding: .7rem 1rem; font-weight: 700; font-size: .95rem;
    transition: background .15s ease;
}}
div[data-testid="stFormSubmitButton"] button:hover, .stButton button:hover {{
    background: {GREEN_DARK}; color: #fff; border: none;
}}
div[data-testid="stFormSubmitButton"] button:focus-visible, .stButton button:focus-visible {{
    outline: 3px solid rgba(15,92,77,.35); outline-offset: 2px;
}}

/* alerts */
[data-testid="stAlert"] {{ border-radius: 10px; }}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {{ background: {SOFT}; border-right: 1px solid {LINE}; }}
.user-card {{
    display: flex; align-items: center; gap: .75rem;
    background: #fff; border: 1px solid {LINE}; border-radius: 14px;
    padding: .8rem .9rem; margin-bottom: .8rem;
}}
.avatar {{
    width: 40px; height: 40px; border-radius: 50%; background: {GREEN}; color: #fff;
    display: flex; align-items: center; justify-content: center; font-weight: 700;
}}
.user-name {{ font-weight: 700; font-size: .95rem; line-height: 1.2; }}
.user-handle {{ color: {MUTED}; font-size: .8rem; }}

@media (max-width: 800px) {{
    .brand-panel {{ min-height: auto; margin-bottom: 1.5rem; }}
}}
@media (prefers-reduced-motion: reduce) {{
    * {{ transition: none !important; }}
}}
</style>
"""

BRAND_HTML = """
<div class="brand-panel">
  <div>
    <div class="brand-logo"><span>₹</span>Expense Tracker</div>
    <div class="brand-title">See where your money goes.</div>
    <div class="brand-sub">
      Log daily spending, set category budgets and read your habits from simple charts.
    </div>
  </div>
  <div class="preview">
    <div class="preview-head">This month</div>
    <div class="row"><b>Food</b><span>₹3,200</span></div>
    <div class="bar"><i style="width:72%"></i></div>
    <div class="row"><b>Travel</b><span>₹1,450</span></div>
    <div class="bar"><i style="width:38%"></i></div>
    <div class="row"><b>Shopping</b><span>₹2,100</span></div>
    <div class="bar"><i style="width:52%"></i></div>
  </div>
</div>
"""


def apply_theme():
    """Call once at the top of app.py, after st.set_page_config()."""
    st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------
# Login / Register page
# ---------------------------------------------------------------------
def render_auth_page():
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown(BRAND_HTML, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="form-title">Welcome</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="form-sub">Log in to your account or create a new one.</div>',
            unsafe_allow_html=True,
        )

        login_tab, register_tab = st.tabs(["Log in", "Create account"])

        with login_tab:
            _login_form()

        with register_tab:
            _register_form()


def _login_form():
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="your_username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="Your password", key="login_password")
        submitted = st.form_submit_button("Log in", use_container_width=True)

    if submitted:
        user, error = auth.login_user(username, password)
        if error:
            st.error(error)
        else:
            auth.set_user(user)
            st.rerun()


def _register_form():
    with st.form("register_form", clear_on_submit=False):
        full_name = st.text_input("Full name", placeholder="Enter full name", key="reg_name")
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", placeholder="Enter Username", key="reg_username")
        with col2:
            email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("Password", type="password", placeholder="8+ characters", key="reg_password")
        with col4:
            confirm = st.text_input("Confirm password", type="password", placeholder="Repeat password", key="reg_confirm")
        submitted = st.form_submit_button("Create account", use_container_width=True)

    if submitted:
        ok, errors = auth.register_user(full_name, username, email, password, confirm)
        if ok:
            st.success("Account created. Open the Log in tab and sign in.")
        else:
            for message in errors:
                st.error(message)


# ---------------------------------------------------------------------
# Sidebar user card (shown after login)
# ---------------------------------------------------------------------
def render_sidebar_user():
    user = auth.get_user()
    initial = user["full_name"].strip()[:1].upper() or "U"

    with st.sidebar:
        st.markdown(
            f"""
            <div class="user-card">
              <div class="avatar">{initial}</div>
              <div>
                <div class="user-name">{user["full_name"]}</div>
                <div class="user-handle">@{user["username"]}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Log out", on_click=auth.logout, use_container_width=True)