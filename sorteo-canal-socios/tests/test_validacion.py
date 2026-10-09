import io

import pandas as pd
import pytest

from core.validacion import leer_padron, normalizar_dni, validar_participacion

DATOS_OK = {
    "nombre": "Juana Pérez",
    "dni": "30.123.456",
    "whatsapp": "+54 9 11 2345-6789",
    "mail": "juana@mail.com",
    "sigue_canal": True,
}


@pytest.mark.parametrize(
    "entrada, esperado",
    [("30.123.456", "30123456"), (" 30123456 ", "30123456"), ("30123456.0", "30123456"), (30123456, "30123456"), ("07123456", "7123456"), (None, "")],
)
def test_normalizar_dni(entrada, esperado):
    assert normalizar_dni(entrada) == esperado


def test_datos_validos_no_tienen_errores():
    assert validar_participacion(DATOS_OK) == []


@pytest.mark.parametrize("campo, valor", [("dni", "123"), ("mail", "juana@"), ("whatsapp", "123"), ("nombre", "J"), ("sigue_canal", False)])
def test_campo_invalido_da_error(campo, valor):
    assert len(validar_participacion({**DATOS_OK, campo: valor})) == 1


def test_padron_excel_con_encabezado_y_numeros():
    df = pd.DataFrame({"DNI": [30123456, "25.340.493", None, "abc"]})
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    assert leer_padron("socios.xlsx", buffer.getvalue()) == {"30123456", "25340493"}


def test_padron_csv_y_txt():
    assert leer_padron("socios.csv", "DNI\n30123456\n25.340.493\n".encode()) == {"30123456", "25340493"}
    assert leer_padron("socios.txt", b"30123456 25340493;7123456") == {"30123456", "25340493", "7123456"}


def test_formato_no_soportado():
    with pytest.raises(ValueError):
        leer_padron("socios.pdf", b"")
