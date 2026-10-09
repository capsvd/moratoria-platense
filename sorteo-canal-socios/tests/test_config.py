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
