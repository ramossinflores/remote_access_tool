import pytest
from unittest.mock import patch, MagicMock
from remote_access_tool import db

@patch("remote_access_tool.db.psycopg2.connect")
def test_obtener_maquina_y_bastion_por_ip(mock_connect):
    # Simular cursor y conexión
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("destination", "192.168.10.10", "192.168.20.10")

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    # Ejecutar la función con un parámetro IP
    resultado = db.obtener_maquina_y_bastion("192.168.10.10")

    assert resultado == {
        "nombre": "destination",
        "ip": "192.168.10.10",
        "bastion": "192.168.20.10"
    }

@patch("remote_access_tool.db.psycopg2.connect")
def test_obtener_maquina_y_bastion_por_nombre(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("dest2", "192.168.10.20", "192.168.20.20")

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    resultado = db.obtener_maquina_y_bastion("dest2")

    assert resultado == {
        "nombre": "dest2",
        "ip": "192.168.10.20",
        "bastion": "192.168.20.20"
    }

@patch("remote_access_tool.db.psycopg2.connect")
def test_maquina_no_encontrada(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    resultado = db.obtener_maquina_y_bastion("no_existe")

    assert resultado is None
