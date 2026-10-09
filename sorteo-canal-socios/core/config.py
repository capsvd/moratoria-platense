"""Lectura de secrets y elección del almacenamiento."""

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from core import contenido
from core.almacenamiento import ZONA, AlmacenLocal, AlmacenSheets

RAIZ = Path(__file__).resolve().parent.parent


def secret(clave: str, por_defecto=None):
    try:
        return st.secrets.get(clave, por_defecto)
    except FileNotFoundError:  # no hay secrets.toml ni secrets en la nube
        return por_defecto


def credenciales_google() -> dict | None:
    """El JSON de la cuenta de servicio, pegado tal cual (gcp_service_account_json) o como tabla TOML."""
    texto = secret("gcp_service_account_json", "")
    if texto:
        return json.loads(texto)
    tabla = secret("gcp_service_account")
    return dict(tabla) if tabla else None


@st.cache_resource
def obtener_almacen():
    credenciales = credenciales_google()
    sheets = secret("sheets")
    if credenciales and sheets and sheets.get("spreadsheet_id"):
        return AlmacenSheets.desde_credenciales(credenciales, sheets["spreadsheet_id"])
    return AlmacenLocal(RAIZ / "data")


def cierre_sorteo() -> datetime | None:
    """Fecha y hora (Buenos Aires) en que se cierra la inscripción; el secret "cierre" pisa el valor del sorteo."""
    valor = secret("cierre", "") or contenido.CIERRE_INSCRIPCION
    if not valor:
        return None
    return datetime.strptime(valor, "%Y-%m-%d %H:%M").replace(tzinfo=ZONA)
