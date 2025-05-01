import psycopg2
import logging
import ipaddress
import sys
from .config import DB_USER, DB_PASS, DB_HOST, DB_NAME, DB_PORT

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
    try:
        ipaddress.ip_address(nombre_o_ip)
        logging.info(f"El parámetro proporcionado es una dirección IP: {nombre_o_ip}")
        return "ip"
    except ValueError:
        logging.info(f"El parámetro proporcionado es un nombre: {nombre_o_ip}")
        return "nombre"

def obtener_maquina_y_bastion(nombre_o_ip):
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
