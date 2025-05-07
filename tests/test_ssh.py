
import pytest
from unittest.mock import patch, MagicMock
from remote_access_tool import ssh

@patch("remote_access_tool.ssh.paramiko.RSAKey.from_private_key_file")
@patch("remote_access_tool.ssh.paramiko.SSHClient")
@patch("remote_access_tool.ssh.os.path.isfile", return_value=True)
def test_conexion_directa_exitosa(mock_isfile, mock_ssh_client_class, mock_rsa_key):
    mock_ssh_client = MagicMock()
    mock_ssh_client_class.return_value = mock_ssh_client
    mock_key = MagicMock()
    mock_rsa_key.return_value = mock_key

    client = ssh.conectar_ssh_con_claves(
        hostname="192.168.20.10",
        username="vagrant",
        clave_privada="/home/vagrant/.ssh/id_rsa"
    )

    assert client is not None
    mock_ssh_client.connect.assert_called_once_with(
        "192.168.20.10",
        username="vagrant",
        pkey=mock_key
    )

@patch("remote_access_tool.ssh.os.path.isfile", return_value=False)
def test_clave_privada_no_encontrada(mock_isfile):
    client = ssh.conectar_ssh_con_claves(
        hostname="192.168.20.10",
        username="vagrant",
        clave_privada="/no/existe/id_rsa"
    )
    assert client is None

@patch("remote_access_tool.ssh.paramiko.SSHClient")
@patch("remote_access_tool.ssh.paramiko.RSAKey.from_private_key_file")
@patch("remote_access_tool.ssh.os.path.isfile", return_value=True)
def test_error_en_conexion(mock_isfile, mock_rsa_key, mock_ssh_client_class):
    mock_ssh_client = MagicMock()
    mock_ssh_client.connect.side_effect = Exception("Falló la conexión SSH")
    mock_ssh_client_class.return_value = mock_ssh_client
    mock_rsa_key.return_value = MagicMock()

    client = ssh.conectar_ssh_con_claves(
        hostname="192.168.20.10",
        username="vagrant",
        clave_privada="/home/vagrant/.ssh/id_rsa"
    )
    assert client is None

@patch("remote_access_tool.ssh.paramiko.SSHClient")
@patch("remote_access_tool.ssh.paramiko.RSAKey.from_private_key_file")
@patch("remote_access_tool.ssh.os.path.isfile", return_value=True)
def test_conexion_con_bastion(mock_isfile, mock_rsa_key, mock_ssh_client_class):
    mock_bastion = MagicMock()
    mock_transport = MagicMock()
    mock_channel = MagicMock()
    mock_bastion.get_transport.return_value = mock_transport
    mock_transport.open_channel.return_value = mock_channel

    mock_ssh_client = MagicMock()
    mock_ssh_client_class.return_value = mock_ssh_client
    mock_rsa_key.return_value = MagicMock()

    client = ssh.conectar_ssh_con_claves(
        hostname="192.168.10.10",
        username="vagrant",
        clave_privada="/home/vagrant/.ssh/id_rsa",
        bastion=mock_bastion
    )

    mock_bastion.get_transport.assert_called_once()
    mock_transport.open_channel.assert_called_once_with(
        "direct-tcpip",
        ("192.168.10.10", 22),
        ("127.0.0.1", 0)
    )
    mock_ssh_client.connect.assert_called_once()
    assert client is not None
