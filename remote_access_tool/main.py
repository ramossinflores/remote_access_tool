import sys
import os
import logging

from .config import SSH_USER, SSH_KEY_PATH
from .db import obtener_maquina_y_bastion
from .ssh import conectar_ssh_con_claves
from .interactive import establecer_sesion_interactiva

def main():
    if len(sys.argv) < 2:
        logging.error("Uso: python -m remote_access_tool.main <nombre_o_ip>")
        sys.exit(1)

    if not os.path.isfile(os.path.expanduser(SSH_KEY_PATH)):
        logging.error(f"La clave privada SSH no existe en la ruta: {SSH_KEY_PATH}")
        sys.exit(1)

    nombre_o_ip = sys.argv[1]
    maquina = obtener_maquina_y_bastion(nombre_o_ip)

    if not maquina:
        sys.exit(1)

    bastion_ip = maquina["bastion"]
    destino_ip = maquina["ip"]

    if not SSH_USER:
        logging.error("Error: Configurar SSH_USER en las variables de entorno.")
        sys.exit(1)

    # Conectar al bastion
    cliente_bastion = conectar_ssh_con_claves(bastion_ip, SSH_USER, SSH_KEY_PATH)
    if not cliente_bastion:
        logging.error("No se pudo conectar al bastion")
        sys.exit(1)

    logging.info(f"Conectado al bastion {bastion_ip}. Ejecutando salto SSH hacia {destino_ip}...")

    # Ejecutar el salto SSH como un comando dentro del bastion
    try:
        comando = f"ssh -tt {SSH_USER}@{destino_ip}"
        stdin, stdout, stderr = cliente_bastion.exec_command(comando)
        establecer_sesion_interactiva(stdin, stdout)
    except Exception as e:
        if str(e) == "Socket is closed":
            logging.info("Sesión cerrada. Canal SSH finalizado")
        else:        
            logging.error(f"Error ejecutando el salto SSH en bastion: {e}")
    finally:
        cliente_bastion.close()

if __name__ == "__main__":
    main()
