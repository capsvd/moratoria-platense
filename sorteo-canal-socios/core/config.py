"""Lectura de secrets y elección del almacenamiento."""

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


@st.cache_resource
def obtener_almacen():
    credenciales = secret("gcp_service_account")
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
