import os
import logging
import paramiko
from .config import SSH_USER, SSH_KEY_PATH

def conectar_ssh_con_claves(hostname, username, clave_privada, bastion=None):
    ssh_client  = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        private_key_path = os.path.expanduser(clave_privada)
        if not os.path.isfile(private_key_path):
            logging.error(f"La clave privada SSH no existe en la ruta: {private_key_path}")
            return None
        logging.info(f"Cargando clave SSH desde: {private_key_path}")
        clave = paramiko.RSAKey.from_private_key_file(private_key_path)
    except Exception as e:
        logging.error(f"No se pudo cargar la clave privada SSH desde {clave_privada}: {e}")
        return None

    try:
        if bastion:
            logging.info(f"Iniciando salto SSH desde bastion hacia {hostname}...")
            bastion_transport = bastion.get_transport()
            tunnel = bastion_transport.open_channel("direct-tcpip", (hostname, 22), ("127.0.0.1", 0))
            ssh_client.connect(hostname, username=username, pkey=clave, sock=tunnel)
            logging.info(f"Conectado a {hostname}.")
        else:
            logging.info(f"Conectando directamente a {hostname}...")
            ssh_client.connect(hostname, username=username, pkey=clave)
        return ssh_client
    except Exception as e:
        logging.error(f"Error conectando a {hostname} mediante SSH: {e}")
        return None
