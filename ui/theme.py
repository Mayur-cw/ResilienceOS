"""
ResilienceOS UI Theme
Defines the visual identity of the Streamlit app. This module establishes a dark
"financial command center" aesthetic: confident, minimal, and high-contrast.
"""

import streamlit as st
from config import (
    BG, CARD, MINT, MINT_DARK, ICE, MUTED, WHITE,
    RED, ORANGE, AMBER, GREEN, STATE_COLOR, STATE_EMOJI
)


def inject_global_css() -> None:
    """
    Injects global CSS to establish the ResilienceOS aesthetic.
    Loads the Inter typeface, restyles Streamlit's default chrome (buttons, metrics,
    sidebar, expanders, dataframes) into a consistent card-based dark theme, and adds
    a few restrained motion touches (hover lift, fade-in on page load).
    """
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* Hide default Streamlit chrome */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header[data-testid="stHeader"] {{ background: transparent; }}

        html, body, [class*="css"], .stApp, button, input, select, textarea {{
            font-family: 'Inter', 'Avenir Next', 'Trebuchet MS', sans-serif;
        }}

        /* App background */
        .stApp {{
            background: radial-gradient(circle at 15% 0%, #132038 0%, {BG} 45%, {BG} 100%);
            color: {WHITE};
        }}

        /* Gentle fade-in for page content so navigating pages feels intentional */
        @keyframes rsxFadeIn {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        .main .block-container {{
            animation: rsxFadeIn 380ms ease-out;
            padding-top: 2.2rem;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {WHITE} !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em;
        }}
        p, span, div {{ color: {WHITE}; }}

        /* Widget labels (selectbox / slider / etc.) */
        label, .stSelectbox label, .stSlider label {{
            color: {MUTED} !important;
            font-weight: 600 !important;
            font-size: 12.5px !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0A0F1C 0%, #0D1526 100%);
            border-right: 1px solid rgba(255,255,255,0.06);
        }}
        section[data-testid="stSidebar"] * {{ color: {WHITE}; }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {{
            border-radius: 10px;
            margin: 2px 8px;
            transition: background-color 160ms ease;
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {{
            background-color: rgba(2, 195, 154, 0.10);
        }}
        section[data-testid="stSidebar"] [aria-current="page"] {{
            background-color: rgba(2, 195, 154, 0.16) !important;
            border-left: 2px solid {MINT};
        }}

        /* ---- Metrics as cards ---- */
        div[data-testid="stMetric"] {{
            background-color: {CARD} !important;
            border-radius: 14px !important;
            padding: 18px !important;
            border: 1px solid rgba(255,255,255,0.06) !important;
            box-shadow: 0 4px 18px rgba(0,0,0,0.22);
        }}
        div[data-testid="stMetricValue"] {{ color: {WHITE} !important; font-weight: 800 !important; }}
        div[data-testid="stMetricLabel"] {{
            color: {MUTED} !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            font-size: 11px !important;
            letter-spacing: 0.06em;
        }}

        div[data-testid="stMetric"],
        .stButton > button,
        div[data-testid="stExpander"],
        div[data-testid="stDataFrame"] {{
            transition: border-color 160ms ease, transform 160ms ease, box-shadow 160ms ease;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 28px rgba(2, 195, 154, 0.14);
            border-color: rgba(2, 195, 154, 0.35) !important;
        }}

        /* ---- Buttons ---- */
        .stButton > button {{
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 10px;
            font-weight: 700;
            background-color: rgba(255,255,255,0.03);
        }}
        .stButton > button:hover {{
            border-color: {ICE};
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(143, 217, 255, 0.16);
            background-color: rgba(143, 217, 255, 0.06);
        }}
        .stButton > button:focus-visible {{
            outline: 2px solid {ICE};
            outline-offset: 2px;
        }}
        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, {MINT} 0%, #01997F 100%);
            border: none;
            color: {BG};
            font-weight: 800;
        }}
        .stButton > button[kind="primary"]:hover {{
            box-shadow: 0 8px 22px rgba(2, 195, 154, 0.35);
            transform: translateY(-1px);
        }}

        /* ---- Expander ---- */
        div[data-testid="stExpander"] {{
            background-color: {CARD};
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.06);
            overflow: hidden;
        }}
        div[data-testid="stExpander"] summary {{
            font-weight: 700 !important;
            color: {WHITE} !important;
        }}

        /* ---- Dataframes ---- */
        div[data-testid="stDataFrame"] {{
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.06);
            overflow: hidden;
        }}

        /* ---- Alerts ---- */
        div[data-testid="stAlert"] {{
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.08);
        }}

        /* ---- Slider value pill accent ---- */
        div[data-testid="stThumbValue"] {{
            background-color: {MINT} !important;
            color: {BG} !important;
            font-weight: 700 !important;
        }}

        hr {{ border-color: rgba(255,255,255,0.08); }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_sidebar_brand() -> None:
    """
    Small branded wordmark shown above Streamlit's automatic page-navigation list.
    Call once near the top of every page/app entrypoint, after inject_global_css().
    """
    st.sidebar.markdown(
        f"""
        <div style="padding: 4px 4px 18px 4px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 10px;">
            <div style="color:{WHITE};font-size:18px;font-weight:800;">🛡️ ResilienceOS</div>
            <div style="color:{MINT};font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-top:2px;">
                Stress Intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str) -> None:
    """
    Renders the standardized top-to-bottom page header.
    Includes the MINT brand anchor tagline, a bold ~28px title,
    and a MUTED italic ~14px subtitle.

    Args:
        title (str): The main page title.
        subtitle (str): The descriptive subtitle placed below the title.
    """
    header_html = f"""
    <div style="margin-bottom: 1.8rem;">
        <div style="color: {MINT}; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.3rem;">
            See the shock. Watch it spread. Stop it early.
        </div>
        <div style="color: {WHITE}; font-size: 30px; font-weight: 800; line-height: 1.2; margin-bottom: 0.3rem;">
            {title}
        </div>
        <div style="color: {MUTED}; font-size: 14.5px; font-style: italic;">
            {subtitle}
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_state_badge(state: str, confidence: float) -> None:
    """
    Renders a small colored pill indicating the classification state and confidence score.

    Args:
        state (str): The borrower's classified state (e.g., 'Temporary', 'Structural', 'Stable').
        confidence (float): Confidence score between 0.0 and 1.0, or 0 to 100.
    """
    conf_pct = int(confidence * 100) if confidence <= 1.0 else int(confidence)

    color = STATE_COLOR.get(state, MUTED)
    emoji = STATE_EMOJI.get(state, "⚪")

    state_label = f"{state} Stress" if state in ["Temporary", "Vulnerable", "Structural"] else state

    badge_html = f"""
    <span style="
        display: inline-block;
        background-color: {color};
        color: {BG};
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 800;
        margin: 4px 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.25);
    ">
        {emoji} {state_label} — {conf_pct}% confidence
    </span>
    """
    st.markdown(badge_html, unsafe_allow_html=True)


def render_card(title: str, value: str = None, subtitle: str = None,
                 accent: str = None, body_html: str = "") -> None:
    """
    Generic branded stat/info card — replaces one-off inline HTML blocks scattered
    across pages so every card in the app shares the same visual language.

    A small colored dot (not a border stripe) next to the eyebrow label carries the
    status color, so the card reads as "this concerns something at risk-level X"
    without resorting to a decorative accent bar.

    Args:
        title: Small uppercase eyebrow label (e.g. "NEXT MANAGEMENT ACTION").
        value: Optional large headline value/text.
        subtitle: Optional supporting line under the value.
        accent: Hex color for the status dot; defaults to MINT.
        body_html: Optional extra HTML appended below (already-built markup).
    """
    accent = accent or MINT
    value_html = (
        f'<div style="color:{WHITE};font-size:26px;font-weight:800;margin-top:8px;line-height:1.25;">{value}</div>'
        if value else ""
    )
    subtitle_html = (
        f'<div style="color:{MUTED};font-size:13.5px;margin-top:6px;line-height:1.5;">{subtitle}</div>'
        if subtitle else ""
    )
    html = f"""
    <div style="
        background:{CARD};
        border-radius:16px;
        padding:20px 22px;
        border:1px solid rgba(255,255,255,0.06);
        box-shadow:0 6px 22px rgba(0,0,0,0.26);
    ">
        <div style="display:flex;align-items:center;gap:8px;">
            <span style="width:8px;height:8px;border-radius:50%;background:{accent};display:inline-block;"></span>
            <span style="color:{MUTED};font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;">{title}</span>
        </div>
        {value_html}
        {subtitle_html}
        {body_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)