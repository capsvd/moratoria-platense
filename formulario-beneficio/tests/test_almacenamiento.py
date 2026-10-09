import gspread
import pytest

from core.almacenamiento import ENCABEZADOS, AlmacenLocal, AlmacenSheets

DATOS = {
    "nombre": " Juana Pérez ",
    "dni": "30.123.456",
    "whatsapp": "+54 9 11 2345-6789",
    "mail": "Juana@Mail.com",
    "madre_nombre": "Rosa Gómez",
    "madre_dni": "10123456",
    "madre_whatsapp": "1123456789",
    "madre_mail": "rosa@mail.com",
    "consentimiento": True,
}


class HojaFalsa:
    """Imita la parte de gspread.Worksheet que usa la app."""

    def __init__(self):
        self.celdas: list[list[str]] = []

    def update(self, filas, rango, value_input_option=None):
        assert rango == "A1"
        self.celdas = [list(f) for f in filas]

    def append_row(self, fila, value_input_option=None):
        assert value_input_option == "RAW"
        self.celdas.append(list(fila))

    def col_values(self, n):
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

    def worksheet(self, nombre):
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


def test_padron_vacio_al_inicio(almacen):
    assert almacen.cargar_padron() == set()


def test_guardar_y_cargar_padron(almacen):
    almacen.guardar_padron({"30123456", "7123456"})
    assert almacen.cargar_padron() == {"30123456", "7123456"}
    assert almacen.padron_actualizado()


def test_inscripcion_normalizada_y_duplicado(almacen):
    assert not almacen.ya_inscripto("30123456")
    almacen.guardar_inscripcion(DATOS)
    assert almacen.ya_inscripto("30.123.456")
    df = almacen.leer_inscripciones()
    assert list(df.columns) == ENCABEZADOS
    fila = df.iloc[0]
    assert (fila["Nombre y apellido"], fila["DNI"], fila["WhatsApp"], fila["Mail"]) == (
        "Juana Pérez",
        "30123456",
        "5491123456789",
        "juana@mail.com",
    )
    assert fila["Consentimiento"] == "Sí"
    assert almacen.inscripciones_excel()[:2] == b"PK"


def test_sheets_crea_hojas_con_encabezado():
    planilla = PlanillaFalsa()
    AlmacenSheets(planilla).guardar_inscripcion(DATOS)
    assert planilla.hojas["Inscripciones"].celdas[0] == ENCABEZADOS


def test_sheets_reemplaza_padron_anterior():
    almacen = AlmacenSheets(PlanillaFalsa())
    almacen.guardar_padron({"30123456"})
    almacen.guardar_padron({"25340493"})
    almacen._padron = None  # forzar lectura desde la hoja
    assert almacen.cargar_padron() == {"25340493"}
