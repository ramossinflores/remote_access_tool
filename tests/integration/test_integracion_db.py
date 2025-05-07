import pytest
from remote_access_tool.db import obtener_maquina_y_bastion

@pytest.mark.integration
def test_obtener_maquina_por_ip():
    resultado = obtener_maquina_y_bastion("192.168.10.10")
    assert resultado is not None
    assert resultado["nombre"] == "destination"
    assert resultado["ip"] == "192.168.10.10"
    assert resultado["bastion"] == "192.168.20.10"

@pytest.mark.integration
def test_obtener_maquina_por_nombre():
    resultado = obtener_maquina_y_bastion("destination")
    assert resultado is not None
    assert resultado["nombre"] == "destination"
    assert resultado["ip"] == "192.168.10.10"
    assert resultado["bastion"] == "192.168.20.10"
