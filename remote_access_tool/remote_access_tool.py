import os
import sys
import ipaddress
import psycopg2
import paramiko
from dotenv import load_dotenv
import logging
import select
import termios
import tty



# Cargar las variables desde el archivo .env
load_dotenv()

# Configuración del sistema de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        # Guarda logs en un archivo
        logging.FileHandler("app.log"),
        #  y también imprime en consola  
        logging.StreamHandler()
    ]
)

#---------------------------- Configuración de la base de datos----------------------------

# Configuración de la base de datos usando variables de entorno
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "5432")


#Establece conexión con la base de datos Postgre utilizando la biblioteca psycopg2
def connect_to_db():
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        return connection
    except psycopg2.Error as e:
        logging.error(f"Error al conectar a la base de datos: {e}")
        sys.exit(1)

def validar_parametro(nombre_o_ip):
    #Se valida si el parámetro es una dirección IP o un nombre
    try:
        ipaddress.ip_address(nombre_o_ip)
        logging.info(f"El parámetro proporcionado es una dirección IP: {nombre_o_ip}")
        return "ip"
    except ValueError:
        logging.info(f"El parámetro proporcionado es un nombre: {nombre_o_ip}")
        return "nombre"

def obtener_maquina_y_bastion(nombre_o_ip):
    #  Consulta para obtener la máquina y su bastión correspondiente
    connection = connect_to_db()
    tipo_parametro = validar_parametro(nombre_o_ip)

    try:
        with connection:
            with connection.cursor() as cursor:
                query = f"""
                    SELECT m.name, m.ip, b.bastion_ip
                    FROM machines AS m
                    INNER JOIN bastions AS b
                    ON m.country = b.country AND m.environment = b.environment
                    WHERE m.{"ip" if tipo_parametro == "ip" else "name"} = %s;
                """
                cursor.execute(query, (nombre_o_ip,))
                resultado = cursor.fetchone()

                if not resultado:
                    logging.warning("No se encontró la máquina en la base de datos.")
                    return None

                logging.info(f"Resultado encontrado: nombre={resultado[0]}, ip={resultado[1]}, bastion={resultado[2]}")
                return {
                    "nombre": resultado[0],
                    "ip": resultado[1],
                    "bastion": resultado[2]
                }
    except psycopg2.Error as e:
        logging.error(f"Error al ejecutar la consulta: {e}")
        return None
    finally:
        connection.close()


#---------------------------- Conexiòn SSH y saltos  ----------------------------


# Ruta a la clave privada SSH
SSH_USER = os.getenv("SSH_USER")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "~/.ssh/id_rsa")

# Establece la conexión SSH utilizando claves
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
    

#---------------------------- Sesión interactiva  ----------------------------


#Crea una sesión interactiva con entrada/salida redireccionadas al usuario

def establecer_sesion_interactiva(stdin, stdout):
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        while True:
            r, w, e = select.select([sys.stdin, stdout.channel], [], [])
            if sys.stdin in r:
                data = os.read(sys.stdin.fileno(), 1024)
                if not data:
                    break
                stdin.write(data)
                stdin.flush()
            if stdout.channel in r:
                if stdout.channel.recv_ready():
                    output = stdout.channel.recv(1024)
                    if not output:
                        break
                    os.write(sys.stdout.fileno(), output)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


#---------------------------- Lógica principal ----------------------------

def main():
    if len(sys.argv) < 2:
        logging.error("Uso: python script.py <nombre_o_ip>")
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
        logging.error(f"Error ejecutando el salto SSH en bastion: {e}")
    finally:
        cliente_bastion.close()

if __name__ == "__main__":
    main()
