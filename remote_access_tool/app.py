from flask import Flask, render_template, request, redirect, url_for, send_file
import logging
import io
from remote_access_tool.db import obtener_maquina_y_bastion
from remote_access_tool.ssh import conectar_ssh_con_claves

app = Flask(__name__, static_folder="static")
logging.basicConfig(level=logging.INFO)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/consulta", methods=["POST"])
def consulta():
    nombre_o_ip = request.form.get("parametro")
    if not nombre_o_ip:
        error = "Debes ingresar un nombre o IP."
        logging.error(error)
        return render_template("results.html", error=error)

    return redirect(url_for('dashboard', ip=nombre_o_ip))

@app.route("/dashboard", methods=["GET"])
def dashboard():
    nombre_o_ip = request.args.get("ip", "destination")
    maquina = obtener_maquina_y_bastion(nombre_o_ip)
    if not maquina:
        error = "No se encontró la máquina destino."
        logging.error(error)
        return render_template("results.html", error=error)

    bastion_ip = maquina["bastion"]
    destino_ip = maquina["ip"]
    ssh_user = "vagrant"
    ssh_key_path = "/home/vagrant/.ssh/id_rsa"

    cliente_bastion = conectar_ssh_con_claves(bastion_ip, ssh_user, ssh_key_path)
    if not cliente_bastion:
        error = "No se pudo conectar al bastion."
        logging.error(error)
        return render_template("results.html", error=error)

    comandos = {
        "hostname": "hostname",
        "uptime": "uptime -p",
        "disco": "df --output=pcent / | tail -1",
        "memoria": "free -m | grep Mem",
        "cpu": "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'",
        "procesos": "ps aux --sort=-%cpu | head -n 10",
        "logs": "dmesg | tail -n 30"
    }

    resultados = {}
    for clave, comando in comandos.items():
        try:
            stdin, stdout, stderr = cliente_bastion.exec_command(
                f"ssh -o StrictHostKeyChecking=no {ssh_user}@{destino_ip} '{comando}'"
            )
            salida = stdout.read().decode().strip()
            resultados[clave] = salida
        except Exception as e:
            resultados[clave] = f"Error: {e}"

    cliente_bastion.close()

    total_mem = used_mem = 0
    try:
        memoria_vals = resultados["memoria"].split()
        if len(memoria_vals) >= 3:
            total_mem = int(memoria_vals[1])
            used_mem = int(memoria_vals[2])
    except Exception as e:
        logging.error(f"Error procesando memoria: {e}")

    try:
        uso_cpu = float(resultados["cpu"])
    except Exception as e:
        logging.error(f"Error procesando CPU: {e}")
        uso_cpu = 0

    try:
        uso_disco = int(resultados["disco"].replace('%', '').strip())
    except Exception as e:
        logging.error(f"Error procesando disco: {e}")
        uso_disco = 0

    procesos_crudos = resultados["procesos"].splitlines()
    procesos_tabla = []

    if procesos_crudos:
        encabezado = procesos_crudos[0].split()
        for linea in procesos_crudos[1:]:
            columnas = linea.split(None, len(encabezado) - 1)
            fila = dict(zip(encabezado, columnas))
            procesos_tabla.append(fila)

    return render_template("dashboard.html",
        hostname=resultados["hostname"],
        uptime=resultados["uptime"],
        disco=resultados["disco"],
        memoria=resultados["memoria"],
        cpu=resultados["cpu"],
        procesos=procesos_tabla,
        logs=resultados["logs"],
        uso_cpu=uso_cpu,
        total_mem=total_mem,
        used_mem=used_mem,
        uso_disco=uso_disco
    )

@app.route("/exportar")
def exportar():
    contenido = request.args.get("data", "")
    nombre = request.args.get("nombre", "informe")

    buffer = io.BytesIO()
    buffer.write(contenido.encode("utf-8"))
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='text/plain',
        as_attachment=True,
        download_name=f"{nombre}.txt"
    )

if __name__ == '__main__':
    logging.info("Servidor Flask iniciando...")
    app.run(host="0.0.0.0", port=5000, debug=True)
