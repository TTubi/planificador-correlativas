from app.database.db import RUTA_BASE_POR_DEFECTO, ruta_base_configurada


def test_sin_variable_usa_la_ruta_por_defecto(monkeypatch):
    monkeypatch.delenv("PLANIFICADOR_DB", raising=False)
    assert ruta_base_configurada() == RUTA_BASE_POR_DEFECTO


def test_la_variable_de_entorno_cambia_la_ruta(monkeypatch, tmp_path):
    monkeypatch.setenv("PLANIFICADOR_DB", str(tmp_path / "otra.db"))
    assert ruta_base_configurada() == tmp_path / "otra.db"


def test_una_variable_vacia_se_ignora(monkeypatch):
    # Por ejemplo, si en el hosting se crea la variable sin valor.
    monkeypatch.setenv("PLANIFICADOR_DB", "")
    assert ruta_base_configurada() == RUTA_BASE_POR_DEFECTO
