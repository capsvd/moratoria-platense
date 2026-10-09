"""Padrón de socios: lectura del Excel del club, estado de cuota y débito automático.

El archivo tiene una fila por socio con tres columnas (el orden no importa y los
nombres pueden variar un poco):
- DNI
- Última cuota paga: el último mes abonado (10/2026, 2026-10, octubre 2026 o una fecha).
- Débito automático: Sí / No (también acepta X, 1, "Débito automático" como forma de pago).
"""

import io
import re
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from core.validacion import normalizar_dni

Mes = tuple[int, int]  # (año, mes)

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
_MES_POR_NOMBRE = {nombre[:3]: i for i, nombre in enumerate(MESES, start=1)} | {"set": 9}
MAX_MESES_DETALLE = 6


@dataclass(frozen=True)
class Socio:
    ultima_cuota: Mes | None
    debito: bool


def _texto(valor) -> str:
    """Minúsculas, sin acentos ni espacios de más."""
    texto = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", texto).strip().lower()


def _vacio(valor) -> bool:
    return valor is None or (not isinstance(valor, str) and pd.isna(valor)) or str(valor).strip() == ""


def leer_mes(valor) -> Mes | None:
    """Interpreta el mes de la última cuota paga en los formatos habituales de Excel."""
    if _vacio(valor):
        return None
    if isinstance(valor, (datetime, date, pd.Timestamp)):
        return (valor.year, valor.month)
    if isinstance(valor, (int, float, np.integer, np.floating)) and not isinstance(valor, bool):
        numero = int(valor)
        if 190001 <= numero <= 210012 and 1 <= numero % 100 <= 12:  # 202610
            return (numero // 100, numero % 100)
        if 20000 <= numero <= 80000:  # fecha serial de Excel
            fecha = date(1899, 12, 30) + timedelta(days=numero)
            return (fecha.year, fecha.month)
        return None

    texto = _texto(valor)
    texto = re.sub(r"[ t]\d{1,2}:\d{2}(:\d{2})?$", "", texto)  # "2026-10-01 00:00:00"
    patrones = [
        (r"(\d{4})[-/.](\d{1,2})", lambda a, m: (a, m)),
        (r"(\d{1,2})[-/.](\d{4})", lambda m, a: (a, m)),
        (r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", lambda d, m, a: (a, m)),
        (r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", lambda a, m, d: (a, m)),
        (r"(\d{1,2})[-/.](\d{2})", lambda m, a: (2000 + a, m)),
        (r"(\d{4})(\d{2})", lambda a, m: (a, m)),
    ]
    for patron, armar in patrones:
        coincide = re.fullmatch(patron, texto)
        if coincide:
            anio, mes = armar(*map(int, coincide.groups()))
            return (anio, mes) if 1 <= mes <= 12 and 1900 <= anio <= 2100 else None

    coincide = re.fullmatch(r"([a-z]+)\.?(?:\s*de\s*|[\s\-/.]*)(\d{2}|\d{4})", texto)
    if coincide and coincide.group(1)[:3] in _MES_POR_NOMBRE:
        anio = int(coincide.group(2))
        return (anio + 2000 if anio < 100 else anio, _MES_POR_NOMBRE[coincide.group(1)[:3]])
    return None


def leer_debito(valor) -> bool:
    if _vacio(valor):
        return False
    texto = _texto(valor)
    if texto in {"si", "s", "x", "1", "1.0", "true", "verdadero", "adherido", "adherida", "yes"}:
        return True
    return "debito" in texto or "automatic" in texto


def meses_adeudados(socio: Socio, requerido: Mes) -> list[Mes]:
    """Meses desde el siguiente a la última cuota paga hasta el requerido, inclusive."""
    if socio.ultima_cuota is None:
        return []
    anio, mes = socio.ultima_cuota
    adeudados = []
    while (anio, mes) < requerido:
        anio, mes = (anio + 1, 1) if mes == 12 else (anio, mes + 1)
        adeudados.append((anio, mes))
    return adeudados


def nombre_mes(mes: Mes) -> str:
    return f"{MESES[mes[1] - 1]} {mes[0]}"


def describir_meses(meses: list[Mes]) -> str:
    """'agosto 2026, septiembre 2026 y octubre 2026', o un rango si son muchos."""
    if len(meses) > MAX_MESES_DETALLE:
        return f"desde {nombre_mes(meses[0])} hasta {nombre_mes(meses[-1])} ({len(meses)} meses)"
    nombres = [nombre_mes(m) for m in meses]
    return nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]


def _columna(encabezados: list[str], claves: tuple[str, ...], excluir: set[int]) -> int | None:
    for i, encabezado in enumerate(encabezados):
        if i not in excluir and any(clave in encabezado for clave in claves):
            return i
    return None


def leer_padron(nombre_archivo: str, contenido: bytes) -> dict[str, Socio]:
    """Lee el Excel/CSV del club y devuelve {dni: Socio}."""
    nombre = nombre_archivo.lower()
    if nombre.endswith((".xlsx", ".xls")):
        tabla = pd.read_excel(io.BytesIO(contenido), header=None, dtype=object)
    elif nombre.endswith((".csv", ".txt")):
        tabla = pd.read_csv(io.BytesIO(contenido), header=None, dtype=str, sep=None, engine="python",
                            encoding="utf-8-sig")
    else:
        raise ValueError("Formato no soportado. Usá .xlsx, .csv o .txt")

    fila_encabezado = None
    for i in range(min(15, len(tabla))):
        textos = [_texto(v) for v in tabla.iloc[i]]
        if any("dni" in t or "documento" in t for t in textos):
            fila_encabezado = i
            break
    if fila_encabezado is None:
        raise ValueError("No encontré la columna DNI. Usá la plantilla que se descarga en esta página.")

    encabezados = [_texto(v) for v in tabla.iloc[fila_encabezado]]
    col_dni = _columna(encabezados, ("dni", "documento"), set())
    col_debito = _columna(encabezados, ("debito", "adherid", "automatic", "forma de pago"), {col_dni})
    col_cuota = _columna(encabezados, ("cuota", "ultim", "pag", "mes", "periodo"), {col_dni, col_debito})
    if col_cuota is None:
        raise ValueError("No encontré la columna de última cuota paga. Usá la plantilla que se descarga en esta página.")

    socios: dict[str, Socio] = {}
    for _, fila in tabla.iloc[fila_encabezado + 1:].iterrows():
        dni = normalizar_dni(fila.iloc[col_dni])
        if not 7 <= len(dni) <= 8:
            continue
        socio = Socio(
            ultima_cuota=leer_mes(fila.iloc[col_cuota]),
            debito=col_debito is not None and leer_debito(fila.iloc[col_debito]),
        )
        anterior = socios.get(dni)
        if anterior:  # DNI repetido: queda la cuota más reciente y el débito si figura en alguna fila
            cuotas = [c for c in (anterior.ultima_cuota, socio.ultima_cuota) if c]
            socio = Socio(max(cuotas) if cuotas else None, anterior.debito or socio.debito)
        socios[dni] = socio
    return socios


def plantilla_excel() -> bytes:
    ejemplo = pd.DataFrame(
        {
            "DNI": ["30123456", "25340493", "40111222"],
            "Última cuota paga": ["10/2026", "08/2026", "11/2026"],
            "Débito automático": ["Sí", "No", "No"],
        }
    )
    buffer = io.BytesIO()
    ejemplo.to_excel(buffer, index=False, sheet_name="Padron")
    return buffer.getvalue()
