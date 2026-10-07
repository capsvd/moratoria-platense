"""Identidad visual según el Brandbook CAP26 (Escudo & Aplicaciones).

Colores web del brandbook: marrón principal #4a2e15, marrón secundario #342011,
dorado #bea15e, más blanco. Tipografías del brandbook y su reemplazo web
(las originales son comerciales):
- Awesome Serif Italic (títulos y números)   -> Playfair Display Italic
- Knockout Junior Featherweight (rótulos)    -> Oswald Light, mayúsculas espaciadas
- Logotipo sans geométrica (textos)          -> Montserrat
"""

from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parent.parent / "assets"

MARRON_PRINCIPAL = "#4a2e15"
MARRON_SECUNDARIO = "#342011"
DORADO = "#bea15e"
BLANCO = "#ffffff"
ERROR = "#e7a58c"

FUENTE_TITULOS = "Playfair Display"
FUENTE_ROTULOS = "Oswald"
FUENTE_TEXTO = "Montserrat"
FUENTES_URL = (
    "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700"
    "&family=Oswald:wght@300;400&family=Playfair+Display:ital,wght@1,400;1,500&display=swap"
)


def aplicar_estilos() -> None:
    # La hoja de estilos va en su propia llamada: un <link> seguido de líneas en blanco
    # corta el bloque HTML de Markdown y el CSS aparecería como texto.
    st.markdown(f"<link rel='stylesheet' href='{FUENTES_URL}'>", unsafe_allow_html=True)
    css = f"""
        <style>
        .stApp, [data-testid="stAppViewContainer"] {{ background: {MARRON_PRINCIPAL} !important; }}
        [data-testid="stHeader"] {{ background: transparent !important; }}
        [data-testid="stMainBlockContainer"] {{ padding-top: 2.5rem; padding-bottom: 3rem; }}
        header, footer, [data-testid="stFooter"], [class*="viewerBadge"] {{ display: none !important; }}

        html, body, p, span, label, div, li, input, button {{ font-family: '{FUENTE_TEXTO}', sans-serif; }}
        p, span, label, div, li {{ color: {BLANCO}; }}

        .cap-logo {{ display: flex; justify-content: center; margin-bottom: 1.75rem; }}
        .cap-logo svg {{ width: 170px; height: auto; }}
        .cap-regla {{ border: 0; border-top: 1px solid {BLANCO}; opacity: 0.9; margin: 0 0 1.25rem; }}
        h1.cap-titulo, h1.cap-titulo * {{
            font-family: '{FUENTE_TITULOS}', serif !important; font-style: italic; font-weight: 400 !important;
            font-size: 2.6rem; line-height: 1.1; text-align: center; color: {BLANCO}; margin: 0.25rem 0 0.5rem;
        }}
        .cap-rotulo, .cap-seccion span {{
            font-family: '{FUENTE_ROTULOS}', sans-serif; font-weight: 300; text-transform: uppercase;
            letter-spacing: 0.22em; font-size: 0.8rem; color: {BLANCO};
        }}
        .cap-rotulo {{ text-align: center; display: block; margin-bottom: 2rem; }}
        .cap-seccion {{ display: flex; align-items: baseline; gap: 0.9rem; margin: 0.5rem 0 0.75rem; }}
        .cap-seccion b {{
            font-family: '{FUENTE_TITULOS}', serif; font-style: italic; font-weight: 400;
            font-size: 2.4rem; line-height: 1; color: {DORADO};
        }}

        [data-testid="stForm"] {{
            background: {MARRON_SECUNDARIO}; border: 0; border-top: 3px solid {DORADO};
            border-radius: 4px; padding: 1.75rem 1.5rem;
        }}
        [data-testid="stWidgetLabel"] p {{
            font-family: '{FUENTE_ROTULOS}', sans-serif; font-weight: 300; text-transform: uppercase;
            letter-spacing: 0.14em; font-size: 0.78rem; color: {BLANCO};
        }}
        .stTextInput input {{
            background: {BLANCO} !important; color: {MARRON_SECUNDARIO} !important;
            -webkit-text-fill-color: {MARRON_SECUNDARIO} !important;
            border: 1px solid transparent !important; border-radius: 4px; font-weight: 500;
            font-family: '{FUENTE_TEXTO}', sans-serif !important;
        }}
        .stTextInput input:focus {{ border-color: {DORADO} !important; box-shadow: 0 0 0 2px {DORADO}55 !important; }}
        .stTextInput input::placeholder {{ color: #9a8a7a !important; -webkit-text-fill-color: #9a8a7a !important; }}
        [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p, [data-testid="stCheckbox"] p {{
            font-family: '{FUENTE_TEXTO}', sans-serif; text-transform: none; letter-spacing: 0;
            font-weight: 400; font-size: 0.95rem; line-height: 1.45;
        }}

        .stButton > button, [data-testid="stFormSubmitButton"] button, .stDownloadButton > button {{
            background: {DORADO} !important; color: {MARRON_SECUNDARIO} !important; border: 0 !important;
            border-radius: 4px; font-family: '{FUENTE_ROTULOS}', sans-serif !important; font-weight: 400;
            text-transform: uppercase; letter-spacing: 0.18em; padding: 0.7rem 1rem;
        }}
        .stButton > button p, [data-testid="stFormSubmitButton"] button p, .stDownloadButton > button p {{
            color: {MARRON_SECUNDARIO} !important; font-family: '{FUENTE_ROTULOS}', sans-serif; font-size: 1rem;
        }}
        .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover, .stDownloadButton > button:hover {{
            background: {BLANCO} !important;
        }}

        .cap-caja {{
            background: {MARRON_SECUNDARIO}; border-radius: 4px; padding: 18px 20px; margin: 14px 0;
            border-left: 4px solid {DORADO}; line-height: 1.5;
        }}
        .cap-caja.error {{ border-left-color: {ERROR}; }}
        .cap-caja b {{ color: {BLANCO}; }}
        .cap-caja a {{ color: {DORADO}; }}
        </style>
        """
    # Sin líneas en blanco: Markdown corta el bloque HTML en la primera que encuentra
    css = "\n".join(linea for linea in css.splitlines() if linea.strip())
    st.markdown(css, unsafe_allow_html=True)


def encabezado(titulo: str, rotulo: str) -> None:
    logo = (ASSETS / "logo_cap.svg").read_text(encoding="utf-8")
    st.markdown(
        f"<div class='cap-logo'>{logo}</div><hr class='cap-regla'>"
        f"<h1 class='cap-titulo'>{titulo}</h1><span class='cap-rotulo'>{rotulo}</span>",
        unsafe_allow_html=True,
    )


def seccion(numero: str, nombre: str) -> None:
    st.markdown(f"<div class='cap-seccion'><b>{numero}</b><span>{nombre}</span></div>", unsafe_allow_html=True)


def caja(html: str, tipo: str = "") -> None:
    st.markdown(f"<div class='cap-caja {tipo}'>{html}</div>", unsafe_allow_html=True)
