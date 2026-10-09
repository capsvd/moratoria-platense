"""Guarda el padrón de socios y los participantes del sorteo en Google Sheets.

La planilla tiene dos hojas que la app crea si no existen:
- "Participantes": una fila por persona anotada.
- "Padron": DNI, última cuota paga (AAAA-MM) y débito automático; E2 guarda la fecha de la última carga.

Sin credenciales de Google (prueba local) usa archivos en data/.
"""

import csv
import io
import threading
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from core.socios import Socio
from core.validacion import normalizar_dni, normalizar_telefono

ZONA = ZoneInfo("America/Argentina/Buenos_Aires")
HOJA_PARTICIPANTES = "Participantes"
HOJA_PADRON = "Padron"
ENCABEZADO_PADRON = ["DNI", "Última cuota paga", "Débito automático", "", "Actualizado"]
CACHE_PADRON_SEG = 120
CACHE_PARTICIPANTES_SEG = 60

ENCABEZADOS = [
    "Fecha",
    "Nombre y apellido",
    "DNI",
    "WhatsApp",
    "Mail",
    "Sigue el canal",
    "Débito automático",
    "Chances",
]
COLUMNA_DNI = ENCABEZADOS.index("DNI") + 1


def _ahora() -> str:
    return datetime.now(ZONA).strftime("%Y-%m-%d %H:%M")


def _mes_a_texto(mes) -> str:
    return f"{mes[0]:04d}-{mes[1]:02d}" if mes else ""


def _texto_a_mes(texto: str):
    try:
        anio, mes = texto.split("-")
        return (int(anio), int(mes))
    except ValueError:
        return None


def _fila_padron(dni: str, socio: Socio) -> list[str]:
    return [dni, _mes_a_texto(socio.ultima_cuota), "Sí" if socio.debito else "No"]


def _socio_de_fila(fila: list[str]) -> Socio:
    fila = list(fila) + ["", "", ""]
    return Socio(ultima_cuota=_texto_a_mes(fila[1]), debito=fila[2] == "Sí")


def armar_fila(datos: dict, socio: Socio) -> list[str]:
    return [
        _ahora(),
        datos["nombre"].strip(),
        normalizar_dni(datos["dni"]),
        normalizar_telefono(datos["whatsapp"]),
        datos["mail"].strip().lower(),
        "Sí",
        "Sí" if socio.debito else "No",
        "2" if socio.debito else "1",
    ]


def _excel(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, sheet_name="Participantes")
    return buffer.getvalue()


class AlmacenSheets:
    """Pensado para picos de inscripciones: Google acepta unas 60 lecturas y 60 escrituras por minuto.

    Guarda en memoria las hojas, el padrón y los DNIs ya anotados, así cada inscripción hace una sola
    escritura; si Google igual frena por cuota, el cliente reintenta con espera creciente.
    """

    def __init__(self, planilla):
        self.planilla = planilla
        self._hojas: dict = {}
        self._padron: dict[str, Socio] | None = None
        self._padron_leido = 0.0
        self._anotados: set[str] | None = None
        self._anotados_leido = 0.0
        self._lock = threading.Lock()

    @classmethod
    def desde_credenciales(cls, credenciales: dict, spreadsheet_id: str) -> "AlmacenSheets":
        import gspread

        cliente = gspread.service_account_from_dict(dict(credenciales), http_client=gspread.BackOffHTTPClient)
        return cls(cliente.open_by_key(spreadsheet_id))

    @property
    def descripcion(self) -> str:
        return f"Google Sheets · <a href='{self.planilla.url}' target='_blank'>abrir planilla</a>"

    def _hoja(self, nombre: str, encabezado: list[str]):
        import gspread

        if nombre not in self._hojas:
            try:
                self._hojas[nombre] = self.planilla.worksheet(nombre)
            except gspread.WorksheetNotFound:
                hoja = self.planilla.add_worksheet(title=nombre, rows=1000, cols=len(encabezado))
                hoja.update([encabezado], "A1")
                self._hojas[nombre] = hoja
        return self._hojas[nombre]

    def cargar_padron(self) -> dict[str, Socio]:
        if self._padron is None or time.monotonic() - self._padron_leido > CACHE_PADRON_SEG:
            filas = self._hoja(HOJA_PADRON, ENCABEZADO_PADRON).get_all_values()[1:]
            self._padron = {normalizar_dni(f[0]): _socio_de_fila(f) for f in filas if f and normalizar_dni(f[0])}
            self._padron_leido = time.monotonic()
        return self._padron

    def padron_actualizado(self) -> str | None:
        return self._hoja(HOJA_PADRON, ENCABEZADO_PADRON).acell("E2").value or None

    def guardar_padron(self, socios: dict[str, Socio]) -> None:
        hoja = self._hoja(HOJA_PADRON, ENCABEZADO_PADRON)
        filas = [ENCABEZADO_PADRON]
        for i, dni in enumerate(sorted(socios)):
            filas.append(_fila_padron(dni, socios[dni]) + ["", _ahora() if i == 0 else ""])
        hoja.clear()
        hoja.resize(rows=len(filas), cols=len(ENCABEZADO_PADRON))
        hoja.update(filas, "A1", value_input_option="RAW")
        self._padron = dict(socios)
        self._padron_leido = time.monotonic()

    def _dnis_anotados(self) -> set[str]:
        if self._anotados is None or time.monotonic() - self._anotados_leido > CACHE_PARTICIPANTES_SEG:
            self._anotados = set(self._hoja(HOJA_PARTICIPANTES, ENCABEZADOS).col_values(COLUMNA_DNI)[1:])
            self._anotados_leido = time.monotonic()
        return self._anotados

    def ya_participa(self, dni: str) -> bool:
        with self._lock:
            return normalizar_dni(dni) in self._dnis_anotados()

    def guardar_participante(self, datos: dict, socio: Socio) -> None:
        fila = armar_fila(datos, socio)
        # RAW deja DNI y teléfonos como texto: sin notación científica ni ceros perdidos
        self._hoja(HOJA_PARTICIPANTES, ENCABEZADOS).append_row(fila, value_input_option="RAW")
        with self._lock:
            self._dnis_anotados().add(fila[COLUMNA_DNI - 1])

    def leer_participantes(self) -> pd.DataFrame:
        valores = self._hoja(HOJA_PARTICIPANTES, ENCABEZADOS).get_all_values()
        if len(valores) <= 1:
            return pd.DataFrame(columns=ENCABEZADOS)
        return pd.DataFrame(valores[1:], columns=valores[0])

    def participantes_excel(self) -> bytes:
        return _excel(self.leer_participantes())


class AlmacenLocal:
    """Solo para probar en la computadora: el disco de Streamlit Cloud se borra al reiniciar."""

    descripcion = "archivos locales en <b>data/</b> · modo prueba, configurá Google Sheets para publicar"

    def __init__(self, carpeta: Path):
        self.carpeta = carpeta
        self.padron = carpeta / "padron_socios.csv"
        self.participantes = carpeta / "participantes.csv"

    def cargar_padron(self) -> dict[str, Socio]:
        if not self.padron.exists():
            return {}
        with self.padron.open(newline="", encoding="utf-8") as f:
            filas = list(csv.reader(f))[1:]
        return {f[0]: _socio_de_fila(f) for f in filas if f}

    def padron_actualizado(self) -> str | None:
        if not self.padron.exists():
            return None
        return datetime.fromtimestamp(self.padron.stat().st_mtime, ZONA).strftime("%Y-%m-%d %H:%M")

    def guardar_padron(self, socios: dict[str, Socio]) -> None:
        self.carpeta.mkdir(exist_ok=True)
        with self.padron.open("w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerow(ENCABEZADO_PADRON[:3])
            escritor.writerows(_fila_padron(dni, socios[dni]) for dni in sorted(socios))

    def leer_participantes(self) -> pd.DataFrame:
        if not self.participantes.exists():
            return pd.DataFrame(columns=ENCABEZADOS)
        return pd.read_csv(self.participantes, dtype=str)

    def ya_participa(self, dni: str) -> bool:
        return normalizar_dni(dni) in set(self.leer_participantes()["DNI"].fillna(""))

    def guardar_participante(self, datos: dict, socio: Socio) -> None:
        self.carpeta.mkdir(exist_ok=True)
        nuevo = not self.participantes.exists()
        with self.participantes.open("a", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            if nuevo:
                escritor.writerow(ENCABEZADOS)
            escritor.writerow(armar_fila(datos, socio))

    def participantes_excel(self) -> bytes:
        return _excel(self.leer_participantes())
