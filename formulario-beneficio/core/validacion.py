"""Normalización y validación de los datos del formulario y del padrón de socios."""

import io
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


def leer_padron(nombre_archivo: str, contenido: bytes) -> set[str]:
    """Lee un .xlsx/.xls/.csv/.txt con DNIs y devuelve el conjunto normalizado.

    Toma cualquier celda que, normalizada, tenga 7 u 8 dígitos; así ignora
    encabezados como "DNI" y funciona con o sin columna nombrada.
    """
    nombre = nombre_archivo.lower()
    if nombre.endswith((".xlsx", ".xls")):
        hojas = pd.read_excel(io.BytesIO(contenido), header=None, dtype=str, sheet_name=None)
        celdas = [v for df in hojas.values() for v in df.to_numpy().ravel()]
    elif nombre.endswith((".csv", ".txt")):
        texto = contenido.decode("utf-8-sig", errors="ignore")
        celdas = re.split(r"[\s,;]+", texto)
    else:
        raise ValueError("Formato no soportado. Usá .xlsx, .csv o .txt")

    dnis = {normalizar_dni(c) for c in celdas}
    return {d for d in dnis if 7 <= len(d) <= 8}


def validar_inscripcion(datos: dict) -> list[str]:
    """Devuelve la lista de errores (vacía si todo está bien)."""
    errores = []
    if not nombre_valido(datos.get("nombre", "")):
        errores.append("Ingresá tu nombre y apellido.")
    if not telefono_valido(datos.get("whatsapp", "")):
        errores.append("Tu WhatsApp debe tener entre 8 y 15 números.")
    if not mail_valido(datos.get("mail", "")):
        errores.append("Tu mail no tiene un formato válido.")
    if not dni_valido(datos.get("dni", "")):
        errores.append("Tu DNI debe tener 7 u 8 números.")
    if not nombre_valido(datos.get("madre_nombre", "")):
        errores.append("Ingresá el nombre y apellido de tu madre.")
    if not dni_valido(datos.get("madre_dni", "")):
        errores.append("El DNI de tu madre debe tener 7 u 8 números.")
    if not mail_valido(datos.get("madre_mail", "")):
        errores.append("El mail de tu madre no tiene un formato válido.")
    if not telefono_valido(datos.get("madre_whatsapp", "")):
        errores.append("El WhatsApp de tu madre debe tener entre 8 y 15 números.")
    if not datos.get("consentimiento"):
        errores.append("Tenés que aceptar el consentimiento para continuar.")
    return errores
