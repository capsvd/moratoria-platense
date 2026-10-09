import pytest

from core.validacion import normalizar_dni, validar_participacion

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
