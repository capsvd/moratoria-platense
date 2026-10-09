import io
from datetime import datetime

import pandas as pd
import pytest

from core.socios import Socio, describir_meses, leer_debito, leer_mes, leer_padron, meses_adeudados, plantilla_excel

OCTUBRE = (2026, 10)


@pytest.mark.parametrize(
    "valor, esperado",
    [
        ("10/2026", (2026, 10)),
        ("2026-10", (2026, 10)),
        ("01/10/2026", (2026, 10)),
        ("2026-10-01 00:00:00", (2026, 10)),
        ("10-26", (2026, 10)),
        ("Octubre 2026", (2026, 10)),
        ("oct-26", (2026, 10)),
        ("Septiembre de 2026", (2026, 9)),
        ("set/2026", (2026, 9)),
        (202611, (2026, 11)),
        ("202611", (2026, 11)),
        (datetime(2026, 8, 1), (2026, 8)),
        (46296, (2026, 10)),  # fecha serial de Excel: 1/10/2026
        ("", None),
        (None, None),
        ("sin pagos", None),
        ("13/2026", None),
    ],
)
def test_leer_mes(valor, esperado):
    assert leer_mes(valor) == esperado


@pytest.mark.parametrize("valor, esperado", [("Sí", True), ("SI", True), ("x", True), (1, True), ("Débito automático", True), ("No", False), ("Efectivo", False), ("", False), (None, False)])
def test_leer_debito(valor, esperado):
    assert leer_debito(valor) is esperado


def test_meses_adeudados():
    assert meses_adeudados(Socio((2026, 10), False), OCTUBRE) == []
    assert meses_adeudados(Socio((2026, 12), False), OCTUBRE) == []
    assert meses_adeudados(Socio((2026, 7), False), OCTUBRE) == [(2026, 8), (2026, 9), (2026, 10)]
    assert meses_adeudados(Socio((2025, 11), False), OCTUBRE)[:2] == [(2025, 12), (2026, 1)]


def test_describir_meses():
    assert describir_meses([(2026, 10)]) == "octubre 2026"
    assert describir_meses([(2026, 8), (2026, 9), (2026, 10)]) == "agosto 2026, septiembre 2026 y octubre 2026"
    largo = meses_adeudados(Socio((2024, 12), False), OCTUBRE)
    assert describir_meses(largo) == "desde enero 2025 hasta octubre 2026 (22 meses)"


def _excel(df: pd.DataFrame, filas_previas: int = 0) -> bytes:
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, startrow=filas_previas)
    return buffer.getvalue()


def test_padron_excel_tipico_del_club():
    df = pd.DataFrame(
        {
            "Apellido y nombre": ["Pérez Juana", "Gómez Rosa", "López Ana", "Sin DNI"],
            "Nro. de DNI": [30123456, "25.340.493", 7123456.0, None],
            "Últ. cuota paga": [datetime(2026, 10, 1), "08/2026", "Noviembre 2026", "10/2026"],
            "Forma de pago": ["Débito automático", "Efectivo", "Débito automático", "Efectivo"],
        }
    )
    socios = leer_padron("socios.xlsx", _excel(df, filas_previas=2))  # con título arriba
    assert socios == {
        "30123456": Socio((2026, 10), True),
        "25340493": Socio((2026, 8), False),
        "7123456": Socio((2026, 11), True),
    }


def test_padron_csv_con_punto_y_coma():
    texto = "DNI;Ultima cuota paga;Debito automatico\n30123456;10/2026;Si\n25340493;;No\n"
    assert leer_padron("socios.csv", texto.encode()) == {
        "30123456": Socio((2026, 10), True),
        "25340493": Socio(None, False),
    }


def test_padron_dni_repetido_toma_la_cuota_mas_reciente():
    df = pd.DataFrame({"DNI": ["30123456", "30123456"], "Última cuota paga": ["08/2026", "10/2026"], "Débito automático": ["Sí", "No"]})
    assert leer_padron("socios.xlsx", _excel(df)) == {"30123456": Socio((2026, 10), True)}


def test_plantilla_se_puede_volver_a_cargar():
    socios = leer_padron("plantilla.xlsx", plantilla_excel())
    assert socios["30123456"] == Socio((2026, 10), True)
    assert socios["25340493"] == Socio((2026, 8), False)


@pytest.mark.parametrize(
    "contenido, mensaje",
    [
        ("Nombre;Cuota\nJuana;10/2026\n", "DNI"),
        ("DNI;Nombre\n30123456;Juana\n", "última cuota"),
    ],
)
def test_padron_sin_columnas_necesarias(contenido, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        leer_padron("socios.csv", contenido.encode())


def test_formato_no_soportado():
    with pytest.raises(ValueError):
        leer_padron("socios.pdf", b"")
