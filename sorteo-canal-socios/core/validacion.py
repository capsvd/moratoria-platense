"""Normalización y validación de los datos del formulario."""

import re

import pandas as pd

RE_MAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
RE_DECIMAL_CERO = re.compile(r"^(\d+)\.0+$")


def normalizar_dni(valor) -> str:
    """Devuelve el DNI solo con dígitos y sin ceros a la izquierda ('' si no hay)."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    texto = str(valor).strip()
    # Excel suele guardar 30123456 como 30123456.0
    coincide = RE_DECIMAL_CERO.match(texto)
    if coincide:
        texto = coincide.group(1)
    return re.sub(r"\D", "", texto).lstrip("0")


def dni_valido(dni: str) -> bool:
    return 7 <= len(normalizar_dni(dni)) <= 8


def normalizar_telefono(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def telefono_valido(valor: str) -> bool:
    return 8 <= len(normalizar_telefono(valor)) <= 15


def mail_valido(valor: str) -> bool:
    return bool(RE_MAIL.match((valor or "").strip()))


def nombre_valido(valor: str) -> bool:
    return len(re.sub(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", "", valor or "")) >= 3


def validar_participacion(datos: dict) -> list[str]:
    """Devuelve la lista de errores (vacía si todo está bien)."""
    errores = []
    if not nombre_valido(datos.get("nombre", "")):
        errores.append("Ingresá tu nombre y apellido.")
    if not dni_valido(datos.get("dni", "")):
        errores.append("Tu DNI debe tener 7 u 8 números.")
    if not telefono_valido(datos.get("whatsapp", "")):
        errores.append("Tu WhatsApp debe tener entre 8 y 15 números.")
    if not mail_valido(datos.get("mail", "")):
        errores.append("Tu mail no tiene un formato válido.")
    if not datos.get("sigue_canal"):
        errores.append("Para participar tenés que seguir el canal de WhatsApp de socios.")
    return errores
