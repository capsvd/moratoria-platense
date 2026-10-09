"""Guarda el padrón de socios y las solicitudes en Google Sheets.

La planilla tiene dos hojas que la app crea si no existen:
- "Inscripciones": una fila por solicitud.
- "Padron": columna A con los DNIs de socios; C2 guarda la fecha de la última carga.

Sin credenciales de Google (prueba local) usa archivos en data/.
"""

import csv
import io
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from core.validacion import normalizar_dni, normalizar_telefono

ZONA = ZoneInfo("America/Argentina/Buenos_Aires")
HOJA_INSCRIPCIONES = "Inscripciones"
HOJA_PADRON = "Padron"
ENCABEZADO_PADRON = ["DNI", "", "Actualizado"]
CACHE_PADRON_SEG = 120

ENCABEZADOS = [
    "Fecha",
    "Nombre y apellido",
    "DNI",
    "WhatsApp",
    "Mail",
    "Madre: nombre y apellido",
    "Madre: DNI",
    "Madre: WhatsApp",
    "Madre: mail",
    "Consentimiento",
]
COLUMNA_DNI = ENCABEZADOS.index("DNI") + 1


def _ahora() -> str:
    return datetime.now(ZONA).strftime("%Y-%m-%d %H:%M")


def armar_fila(datos: dict) -> list[str]:
    return [
        _ahora(),
        datos["nombre"].strip(),
        normalizar_dni(datos["dni"]),
        normalizar_telefono(datos["whatsapp"]),
        datos["mail"].strip().lower(),
        datos["madre_nombre"].strip(),
        normalizar_dni(datos["madre_dni"]),
        normalizar_telefono(datos["madre_whatsapp"]),
        datos["madre_mail"].strip().lower(),
        "Sí",
    ]


def _excel(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, sheet_name="Inscripciones")
    return buffer.getvalue()


class AlmacenSheets:
    def __init__(self, planilla):
        self.planilla = planilla
        self._padron: set[str] | None = None
        self._padron_leido = 0.0

    @classmethod
    def desde_credenciales(cls, credenciales: dict, spreadsheet_id: str) -> "AlmacenSheets":
        import gspread

        cliente = gspread.service_account_from_dict(dict(credenciales))
        return cls(cliente.open_by_key(spreadsheet_id))

    @property
    def descripcion(self) -> str:
        return f"Google Sheets · <a href='{self.planilla.url}' target='_blank'>abrir planilla</a>"

    def _hoja(self, nombre: str, encabezado: list[str]):
        import gspread

        try:
            return self.planilla.worksheet(nombre)
        except gspread.WorksheetNotFound:
            hoja = self.planilla.add_worksheet(title=nombre, rows=1000, cols=len(encabezado))
            hoja.update([encabezado], "A1")
            return hoja

    def cargar_padron(self) -> set[str]:
        if self._padron is None or time.monotonic() - self._padron_leido > CACHE_PADRON_SEG:
            valores = self._hoja(HOJA_PADRON, ENCABEZADO_PADRON).col_values(1)[1:]
            self._padron = {normalizar_dni(v) for v in valores} - {""}
            self._padron_leido = time.monotonic()
        return self._padron

    def padron_actualizado(self) -> str | None:
        return self._hoja(HOJA_PADRON, ENCABEZADO_PADRON).acell("C2").value or None

    def guardar_padron(self, dnis: set[str]) -> None:
        hoja = self._hoja(HOJA_PADRON, ENCABEZADO_PADRON)
        filas = [ENCABEZADO_PADRON]
        for i, dni in enumerate(sorted(dnis)):
            filas.append([dni, "", _ahora()] if i == 0 else [dni, "", ""])
        hoja.clear()
        hoja.resize(rows=len(filas), cols=3)
        hoja.update(filas, "A1", value_input_option="RAW")
        self._padron = set(dnis)
        self._padron_leido = time.monotonic()

    def ya_inscripto(self, dni: str) -> bool:
        hoja = self._hoja(HOJA_INSCRIPCIONES, ENCABEZADOS)
        return normalizar_dni(dni) in set(hoja.col_values(COLUMNA_DNI)[1:])

    def guardar_inscripcion(self, datos: dict) -> None:
        # RAW deja DNI y teléfonos como texto: sin notación científica ni ceros perdidos
        self._hoja(HOJA_INSCRIPCIONES, ENCABEZADOS).append_row(armar_fila(datos), value_input_option="RAW")

    def leer_inscripciones(self) -> pd.DataFrame:
        valores = self._hoja(HOJA_INSCRIPCIONES, ENCABEZADOS).get_all_values()
        if len(valores) <= 1:
            return pd.DataFrame(columns=ENCABEZADOS)
        return pd.DataFrame(valores[1:], columns=valores[0])

    def inscripciones_excel(self) -> bytes:
        return _excel(self.leer_inscripciones())


class AlmacenLocal:
    """Solo para probar en la computadora: el disco de Streamlit Cloud se borra al reiniciar."""

    descripcion = "archivos locales en <b>data/</b> · modo prueba, configurá Google Sheets para publicar"

    def __init__(self, carpeta: Path):
        self.carpeta = carpeta
        self.padron = carpeta / "padron_socios.txt"
        self.inscripciones = carpeta / "inscripciones.csv"

    def cargar_padron(self) -> set[str]:
        if not self.padron.exists():
            return set()
        return set(self.padron.read_text(encoding="utf-8").split())

    def padron_actualizado(self) -> str | None:
        if not self.padron.exists():
            return None
        return datetime.fromtimestamp(self.padron.stat().st_mtime, ZONA).strftime("%Y-%m-%d %H:%M")

    def guardar_padron(self, dnis: set[str]) -> None:
        self.carpeta.mkdir(exist_ok=True)
        self.padron.write_text("\n".join(sorted(dnis)), encoding="utf-8")

    def leer_inscripciones(self) -> pd.DataFrame:
        if not self.inscripciones.exists():
            return pd.DataFrame(columns=ENCABEZADOS)
        return pd.read_csv(self.inscripciones, dtype=str)

    def ya_inscripto(self, dni: str) -> bool:
        return normalizar_dni(dni) in set(self.leer_inscripciones()["DNI"].fillna(""))

    def guardar_inscripcion(self, datos: dict) -> None:
        self.carpeta.mkdir(exist_ok=True)
        nuevo = not self.inscripciones.exists()
        with self.inscripciones.open("a", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            if nuevo:
                escritor.writerow(ENCABEZADOS)
            escritor.writerow(armar_fila(datos))

    def inscripciones_excel(self) -> bytes:
        return _excel(self.leer_inscripciones())
