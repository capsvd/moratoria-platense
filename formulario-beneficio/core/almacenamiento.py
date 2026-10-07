"""Guarda el padrón de socios y las inscripciones en la carpeta data/."""

import csv
import io
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from core.validacion import normalizar_dni, normalizar_telefono

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PADRON = DATA_DIR / "padron_socios.txt"
INSCRIPCIONES = DATA_DIR / "inscripciones.csv"
ZONA = ZoneInfo("America/Argentina/Buenos_Aires")

COLUMNAS = [
    "fecha",
    "nombre",
    "dni",
    "whatsapp",
    "mail",
    "madre_nombre",
    "madre_dni",
    "madre_whatsapp",
    "madre_mail",
    "consentimiento",
]


def guardar_padron(dnis: set[str]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    PADRON.write_text("\n".join(sorted(dnis)), encoding="utf-8")


def cargar_padron() -> set[str]:
    if not PADRON.exists():
        return set()
    return {d for d in PADRON.read_text(encoding="utf-8").split() if d}


def padron_actualizado() -> datetime | None:
    if not PADRON.exists():
        return None
    return datetime.fromtimestamp(PADRON.stat().st_mtime, ZONA)


def leer_inscripciones() -> pd.DataFrame:
    if not INSCRIPCIONES.exists():
        return pd.DataFrame(columns=COLUMNAS)
    return pd.read_csv(INSCRIPCIONES, dtype=str)


def ya_inscripto(dni: str) -> bool:
    return normalizar_dni(dni) in set(leer_inscripciones()["dni"].fillna(""))


def guardar_inscripcion(datos: dict) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    fila = {
        "fecha": datetime.now(ZONA).strftime("%Y-%m-%d %H:%M"),
        "nombre": datos["nombre"].strip(),
        "dni": normalizar_dni(datos["dni"]),
        "whatsapp": normalizar_telefono(datos["whatsapp"]),
        "mail": datos["mail"].strip().lower(),
        "madre_nombre": datos["madre_nombre"].strip(),
        "madre_dni": normalizar_dni(datos["madre_dni"]),
        "madre_whatsapp": normalizar_telefono(datos["madre_whatsapp"]),
        "madre_mail": datos["madre_mail"].strip().lower(),
        "consentimiento": "Sí",
    }
    nuevo = not INSCRIPCIONES.exists()
    with INSCRIPCIONES.open("a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS)
        if nuevo:
            escritor.writeheader()
        escritor.writerow(fila)


def inscripciones_excel() -> bytes:
    buffer = io.BytesIO()
    leer_inscripciones().to_excel(buffer, index=False, sheet_name="Inscripciones")
    return buffer.getvalue()
