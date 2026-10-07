"""Identidad visual de Platense en un solo lugar.

Paleta tomada de la app de Moratoria (marrón y crema). Si el Brandbook 26
define otros valores o tipografías, cambiarlos acá y se aplican en todo el sitio.
"""

import base64
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parent.parent / "assets"

MARRON_OSCURO = "#2B1708"
MARRON = "#8B5A2B"
MARRON_HOVER = "#A06B35"
MARRON_PANEL = "#3E2413"
CREMA = "#F2E3D5"
ROJO_ALERTA = "#E8B4A0"

FUENTE_TITULOS = "Oswald"
FUENTE_TEXTO = "Inter"


def _imagen_base64(nombre: str) -> str | None:
    ruta = ASSETS / nombre
    if not ruta.exists():
        return None
    return base64.b64encode(ruta.read_bytes()).decode()


def aplicar_estilos() -> None:
    fondo = _imagen_base64("fondo.png")
    capa_fondo = (
        f'linear-gradient(rgba(43, 23, 8, 0.85), rgba(43, 23, 8, 0.85)), url("data:image/png;base64,{fondo}")'
        if fondo
        else MARRON_OSCURO
    )
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family={FUENTE_TITULOS}:wght@500;700&family={FUENTE_TEXTO}:wght@400;600&display=swap');

        .stApp, [data-testid="stAppViewContainer"] {{
            background: {capa_fondo} !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        [data-testid="stHeader"] {{ background: transparent !important; }}
        [data-testid="stMainBlockContainer"] {{ padding-top: 2rem; }}
        header, footer, [data-testid="stFooter"], [class*="viewerBadge"] {{ display: none !important; }}

        html, body, p, span, label, div, li {{ font-family: '{FUENTE_TEXTO}', sans-serif; color: {CREMA}; }}
        h1, h2, h3 {{
            font-family: '{FUENTE_TITULOS}', sans-serif !important;
            color: {CREMA} !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        [data-testid="stForm"] {{
            background: rgba(62, 36, 19, 0.75);
            border: 1px solid {MARRON};
            border-radius: 12px;
            padding: 1.5rem;
        }}

        .stTextInput input {{
            background-color: {CREMA} !important;
            color: {MARRON_OSCURO} !important;
            border: 2px solid {MARRON} !important;
            border-radius: 8px;
            font-weight: 600;
        }}
        .stTextInput input::placeholder {{ color: #8a7766 !important; }}

        .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{
            background-color: {MARRON} !important;
            color: {CREMA} !important;
            border: none !important;
            border-radius: 8px;
            width: 100%;
            font-family: '{FUENTE_TITULOS}', sans-serif;
            font-size: 18px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {{
            background-color: {MARRON_HOVER} !important;
            color: #FFFFFF !important;
        }}

        .cap-caja {{
            background-color: {MARRON_PANEL};
            border: 1px solid {MARRON};
            border-radius: 10px;
            padding: 18px 20px;
            margin: 12px 0;
        }}
        .cap-caja.ok {{ border-left: 6px solid {CREMA}; }}
        .cap-caja.error {{ border-left: 6px solid {ROJO_ALERTA}; }}
        .cap-caja b {{ color: #FFFFFF; }}
        .cap-subtitulo {{ text-align: center; opacity: 0.85; margin-top: -0.5rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def encabezado(titulo: str, subtitulo: str | None = None) -> None:
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        if (ASSETS / "escudo.png").exists():
            st.image(str(ASSETS / "escudo.png"), width="stretch")
    st.markdown(f"<h1 style='text-align:center'>{titulo}</h1>", unsafe_allow_html=True)
    if subtitulo:
        st.markdown(f"<p class='cap-subtitulo'>{subtitulo}</p>", unsafe_allow_html=True)


def caja(html: str, tipo: str = "") -> None:
    st.markdown(f"<div class='cap-caja {tipo}'>{html}</div>", unsafe_allow_html=True)


def pie() -> None:
    if (ASSETS / "logo_campana.png").exists():
        st.markdown("<br>", unsafe_allow_html=True)
        _, centro, _ = st.columns([1, 1.5, 1])
        with centro:
            st.image(str(ASSETS / "logo_campana.png"), width="stretch")
