from datetime import datetime

from core import config
from core.almacenamiento import ZONA


def test_sin_cierre_configurado(monkeypatch):
    monkeypatch.setattr(config, "secret", lambda clave, por_defecto=None: por_defecto)
    assert config.cierre_sorteo() is None


def test_cierre_en_hora_de_buenos_aires(monkeypatch):
    monkeypatch.setattr(config, "secret", lambda clave, por_defecto=None: "2026-10-13 20:00" if clave == "cierre" else por_defecto)
    assert config.cierre_sorteo() == datetime(2026, 10, 13, 20, 0, tzinfo=ZONA)
