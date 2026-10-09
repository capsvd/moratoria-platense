import gspread
import pytest

from core.almacenamiento import ENCABEZADOS, AlmacenLocal, AlmacenSheets
from core.socios import Socio

DATOS = {
    "nombre": " Juana Pérez ",
    "dni": "30.123.456",
    "whatsapp": "+54 9 11 2345-6789",
    "mail": "Juana@Mail.com",
    "sigue_canal": True,
}


class HojaFalsa:
    """Imita la parte de gspread.Worksheet que usa la app."""

    def __init__(self):
        self.celdas: list[list[str]] = []
        self.lecturas = 0

    def update(self, filas, rango, value_input_option=None):
        assert rango == "A1"
        self.celdas = [list(f) for f in filas]

    def append_row(self, fila, value_input_option=None):
        assert value_input_option == "RAW"
        self.celdas.append(list(fila))

    def col_values(self, n):
        self.lecturas += 1
        return [f[n - 1] for f in self.celdas if len(f) >= n and f[n - 1] != ""]

    def get_all_values(self):
        return self.celdas

    def acell(self, ref):
        fila, col = int(ref[1:]) - 1, ord(ref[0]) - ord("A")
        valor = self.celdas[fila][col] if fila < len(self.celdas) and col < len(self.celdas[fila]) else ""
        return type("Celda", (), {"value": valor})

    def clear(self):
        self.celdas = []

    def resize(self, rows, cols):
        pass


class PlanillaFalsa:
    url = "https://docs.google.com/spreadsheets/d/x"

    def __init__(self):
        self.hojas: dict[str, HojaFalsa] = {}
        self.pedidos_de_hoja = 0

    def worksheet(self, nombre):
        self.pedidos_de_hoja += 1
        if nombre not in self.hojas:
            raise gspread.WorksheetNotFound(nombre)
        return self.hojas[nombre]

    def add_worksheet(self, title, rows, cols):
        self.hojas[title] = HojaFalsa()
        return self.hojas[title]


@pytest.fixture(params=["sheets", "local"])
def almacen(request, tmp_path):
    if request.param == "sheets":
        return AlmacenSheets(PlanillaFalsa())
    return AlmacenLocal(tmp_path)


PADRON = {"30123456": Socio((2026, 10), True), "7123456": Socio((2026, 8), False), "25340493": Socio(None, False)}


def test_padron_vacio_al_inicio(almacen):
    assert almacen.cargar_padron() == {}


def test_guardar_y_cargar_padron(almacen):
    almacen.guardar_padron(PADRON)
    assert almacen.cargar_padron() == PADRON
    assert almacen.padron_actualizado()


def test_participante_normalizado_y_duplicado(almacen):
    assert not almacen.ya_participa("30123456")
    almacen.guardar_participante(DATOS, Socio((2026, 10), True))
    assert almacen.ya_participa("30.123.456")
    df = almacen.leer_participantes()
    assert list(df.columns) == ENCABEZADOS
    fila = df.iloc[0]
    assert (fila["Nombre y apellido"], fila["DNI"], fila["WhatsApp"], fila["Mail"]) == (
        "Juana Pérez",
        "30123456",
        "5491123456789",
        "juana@mail.com",
    )
    assert (fila["Sigue el canal"], fila["Débito automático"], fila["Chances"]) == ("Sí", "Sí", "2")
    assert almacen.participantes_excel()[:2] == b"PK"


def test_sheets_crea_hojas_con_encabezado():
    planilla = PlanillaFalsa()
    AlmacenSheets(planilla).guardar_participante(DATOS, Socio((2026, 11), False))
    assert planilla.hojas["Participantes"].celdas[0] == ENCABEZADOS


def test_sheets_reemplaza_padron_anterior():
    almacen = AlmacenSheets(PlanillaFalsa())
    almacen.guardar_padron({"30123456": Socio((2026, 10), False)})
    almacen.guardar_padron({"25340493": Socio((2026, 9), True)})
    almacen._padron = None  # forzar lectura desde la hoja
    assert almacen.cargar_padron() == {"25340493": Socio((2026, 9), True)}


def test_sheets_una_sola_escritura_por_inscripcion():
    planilla = PlanillaFalsa()
    almacen = AlmacenSheets(planilla)
    for i, dni in enumerate(["30123456", "25340493", "40111222"]):
        assert not almacen.ya_participa(dni)
        almacen.guardar_participante({**DATOS, "dni": dni}, Socio((2026, 10), False))
        assert almacen.ya_participa(dni)
    hoja = planilla.hojas["Participantes"]
    assert hoja.lecturas == 1  # los DNIs anotados se leen una vez y se mantienen en memoria
    assert planilla.pedidos_de_hoja <= 2  # la hoja se busca una sola vez
    assert len(hoja.celdas) == 4


def test_sheets_ve_anotados_cargados_por_otra_instancia(monkeypatch):
    planilla = PlanillaFalsa()
    AlmacenSheets(planilla).guardar_participante(DATOS, Socio((2026, 10), False))
    otro = AlmacenSheets(planilla)
    assert otro.ya_participa("30123456")
