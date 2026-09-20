"""
dashboard_ui.py - theme for everything after login (sidebar, metrics, tables,
forms, charts). Matches the look of auth_ui.py.

Call apply_dashboard_theme() once in app.py. Pages can then use:

    import dashboard_ui as ui
    ui.page_header("Analytics", "Where your money went this month")
    fig, ax = plt.subplots(); ui.style_axes(ax)   # optional
"""

import matplotlib.pyplot as plt
import streamlit as st

GREEN = "#0F5C4D"
GREEN_DARK = "#0A4437"
INK = "#1F2A2E"
MUTED = "#6B7780"
LINE = "#E3E8E6"
SOFT = "#F3F7F5"

# Chart colours (green first, then distinct but calm)
PALETTE = ["#0F5C4D", "#2FA084", "#F2A541", "#E4572E", "#4C6EF5", "#8E6BBF", "#7A8B99"]

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {{ font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif; color: {INK}; }}
.stApp {{ background: #FFFFFF; }}
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }}

/* ---------- page header ---------- */
.page-header {{
    background: {GREEN}; color: #fff; border-radius: 18px;
    padding: 1.6rem 1.8rem; margin-bottom: 1.6rem;
    border-left: 8px solid #8EE0C6;
}}
.page-header h1 {{ color: #fff; font-size: 1.8rem; font-weight: 800; margin: 0; letter-spacing: -.4px; padding: 0; }}
.page-header p {{ color: #CFE5DF; margin: .35rem 0 0; font-size: .97rem; }}

/* headings */
h1, h2, h3 {{ color: {INK}; letter-spacing: -.3px; font-weight: 800; }}
h2 {{ font-size: 1.35rem; }}
h3 {{ font-size: 1.1rem; }}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {{ background: {SOFT}; border-right: 1px solid {LINE}; }}
[data-testid="stSidebarNavLink"] {{
    border-radius: 10px; padding: .5rem .75rem; font-weight: 600; color: {INK};
}}
[data-testid="stSidebarNavLink"]:hover {{ background: #E4EFEB; }}
[data-testid="stSidebarNavLink"][aria-current="page"] {{
    background: {GREEN}; color: #fff;
}}
[data-testid="stSidebarNavLink"][aria-current="page"] span {{ color: #fff; }}
.sidebar-brand {{ display:flex; align-items:center; gap:.6rem; font-weight:800; font-size:1.05rem; padding:.3rem .2rem 1rem; }}
.sidebar-brand span {{
    width:32px; height:32px; line-height:32px; text-align:center; border-radius:9px;
    background:{GREEN}; color:#fff; font-weight:800;
}}
.user-card {{
    display:flex; align-items:center; gap:.75rem; background:#fff;
    border:1px solid {LINE}; border-radius:14px; padding:.8rem .9rem; margin:.4rem 0 .8rem;
}}
.avatar {{
    width:40px; height:40px; border-radius:50%; background:{GREEN}; color:#fff;
    display:flex; align-items:center; justify-content:center; font-weight:700;
}}
.user-name {{ font-weight:700; font-size:.95rem; line-height:1.2; }}
.user-handle {{ color:{MUTED}; font-size:.8rem; }}

/* ---------- metric cards ---------- */
[data-testid="stMetric"] {{
    background: #fff; border: 1px solid {LINE}; border-radius: 14px;
    padding: 1rem 1.2rem; border-top: 4px solid {GREEN};
}}
[data-testid="stMetricLabel"] p {{ color: {MUTED}; font-weight: 600; font-size: .85rem; }}
[data-testid="stMetricValue"] {{ font-weight: 800; color: {INK}; }}

/* ---------- inputs ---------- */
.stTextInput label p, .stNumberInput label p, .stSelectbox label p,
.stDateInput label p, .stTextArea label p, .stMultiSelect label p {{
    font-size: .85rem; font-weight: 600; color: {INK};
}}
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input {{
    border-radius: 10px;
}}
div[data-baseweb="input"], div[data-baseweb="select"] > div, div[data-baseweb="textarea"] {{
    border-radius: 10px !important; border-color: {LINE} !important;
}}
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within {{
    border-color: {GREEN} !important; box-shadow: 0 0 0 3px rgba(15,92,77,.15);
}}

/* forms: soft card */
[data-testid="stForm"] {{
    background: {SOFT}; border: 1px solid {LINE}; border-radius: 16px; padding: 1.4rem;
}}

/* ---------- buttons ---------- */
.stButton button, div[data-testid="stFormSubmitButton"] button {{
    background: {GREEN}; color: #fff; border: none; border-radius: 10px;
    padding: .6rem 1.2rem; font-weight: 700; transition: background .15s ease;
}}
.stButton button:hover, div[data-testid="stFormSubmitButton"] button:hover {{
    background: {GREEN_DARK}; color: #fff; border: none;
}}
.stButton button:focus-visible, div[data-testid="stFormSubmitButton"] button:focus-visible {{
    outline: 3px solid rgba(15,92,77,.35); outline-offset: 2px;
}}

/* ---------- tables, tabs, expanders, alerts ---------- */
[data-testid="stDataFrame"] {{ border: 1px solid {LINE}; border-radius: 12px; overflow: hidden; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 1.4rem; border-bottom: 1px solid {LINE}; }}
.stTabs [data-baseweb="tab"] {{ font-weight: 600; color: {MUTED}; background: transparent; }}
.stTabs [aria-selected="true"] {{ color: {GREEN}; }}
.stTabs [data-baseweb="tab-highlight"] {{ background-color: {GREEN}; height: 3px; }}
[data-testid="stExpander"] {{ border: 1px solid {LINE}; border-radius: 12px; }}
[data-testid="stAlert"] {{ border-radius: 10px; }}
[data-testid="stProgress"] div[role="progressbar"] > div {{ background-color: {GREEN}; }}
hr {{ border-color: {LINE}; }}

@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
</style>
"""


def apply_dashboard_theme():
    """Call once in app.py after login. Also sets the default Matplotlib look."""
    st.markdown(CSS, unsafe_allow_html=True)
    plt.rcParams.update({
        "axes.prop_cycle": plt.cycler(color=PALETTE),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": LINE,
        "axes.labelcolor": INK,
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.grid": True,
        "grid.color": "#EEF2F0",
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "font.family": "sans-serif",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })


def page_header(title, subtitle=""):
    """Green banner at the top of a page."""
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f'<div class="page-header"><h1>{title}</h1>{sub}</div>', unsafe_allow_html=True)


def sidebar_brand():
    """Small logo + app name at the top of the sidebar."""
    st.sidebar.markdown(
        '<div class="sidebar-brand"><span>₹</span>Expense Tracker</div>',
        unsafe_allow_html=True,
    )


def style_axes(ax):
    """Optional: light clean-up for one Matplotlib axes."""
    ax.set_axisbelow(True)
    ax.grid(axis="x", visible=False)
    return ax