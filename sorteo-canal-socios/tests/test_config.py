from datetime import datetime

from core import config
from core.almacenamiento import ZONA


def test_cierre_por_defecto_miercoles_14_a_las_19(monkeypatch):
    monkeypatch.setattr(config, "secret", lambda clave, por_defecto=None: por_defecto)
    cierre = config.cierre_sorteo()
    assert cierre == datetime(2026, 10, 14, 19, 0, tzinfo=ZONA)
    assert cierre.strftime("%A") == "Wednesday"


def test_secret_reemplaza_el_cierre(monkeypatch):
    monkeypatch.setattr(config, "secret", lambda clave, por_defecto=None: "2026-10-20 12:30" if clave == "cierre" else por_defecto)
    assert config.cierre_sorteo() == datetime(2026, 10, 20, 12, 30, tzinfo=ZONA)


def test_credenciales_pegadas_como_json(monkeypatch):
    json_google = '{"type": "service_account", "private_key": "-----BEGIN PRIVATE KEY-----\\nABC\\n-----END PRIVATE KEY-----\\n", "client_email": "sorteo@x.iam.gserviceaccount.com"}'
    monkeypatch.setattr(config, "secret", lambda clave, por_defecto=None: json_google if clave == "gcp_service_account_json" else por_defecto)
    credenciales = config.credenciales_google()
    assert credenciales["client_email"] == "sorteo@x.iam.gserviceaccount.com"
    assert credenciales["private_key"].count("\n") == 3


def test_credenciales_como_tabla(monkeypatch):
    monkeypatch.setattr(config, "secret", lambda clave, por_defecto=None: {"type": "service_account"} if clave == "gcp_service_account" else por_defecto)
    assert config.credenciales_google() == {"type": "service_account"}


def test_sin_credenciales(monkeypatch):
    monkeypatch.setattr(config, "secret", lambda clave, por_defecto=None: por_defecto)
    assert config.credenciales_google() is None
