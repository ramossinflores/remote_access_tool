#!/bin/bash

# Funciòn para actualizar e instalar los paquetes base
instalar_paquetes_base() {
    nombre_host=$1
    echo "[$nombre_host] Actualizando paquetes..."
    dnf update
    echo "[$nombre_host] Instalando paquetes base..."
    dnf install -y openssh-server nmap-ncat sshpass
}


# Funciòn para habilitar SSH

habilitar_ssh() {
    nombre_host=$1
    echo "[[$nombre_host]] Habilitando SSH..."
    systemctl enable --now sshd

}

# Función para esperar a que un puerto esté disponible en una IP
esperar_puerto() {
    nombre_host=$1
    host=$2
    puerto=$3
    timeout_max=60
    wait_interval=2
    waited=0

    echo "[$nombre_host] Esperando a $host:$puerto..."

    while ! nc -z $host $puerto; do
    if [ $waited -ge $timeout_max ]; then
    echo "[$nombre_host][ERROR] Tiempo de espera agotado. $host no está disponible en el puerto $puerto"
    return 1
    fi
    echo "[$nombre_host] Esperando... ($waited/$timeout_max segundos)"
    sleep "$wait_interval"
    waited=$((waited + wait_interval))
    done

    echo "[$nombre_host] $host:$puerto está disponible"
    return 0
    }

# Función para generar clave SSH

generar_clave_ssh() {
    nombre_host=$1
    if [ ! -f /home/vagrant/.ssh/id_rsa ]; then
        echo "[$nombre_host]  Generando clave RSA..."
        sudo -u vagrant ssh-keygen -t rsa -N '' -f /home/vagrant/.ssh/id_rsa
    fi
}

# Función para registrar un host remoto en known_hosts y evitar advertencias de autenticación
registrar_known_host() {
    nombre_host=$1
    ip_destino=$2

    echo "[$nombre_host] Registrando $ip_destino en known_hosts..."

    # Evita duplicados
    sudo -u vagrant ssh-keygen -R "$ip_destino" 2>/dev/null
    sudo -u vagrant ssh-keyscan -H "$ip_destino" >> /home/vagrant/.ssh/known_hosts 2>/dev/null
    chown vagrant:vagrant /home/vagrant/.ssh/known_hosts
}
# Función para copiar la clave pública al host remoto usando sshpass
copiar_clave_ssh() {
    nombre_host=$1
    ip_destino=$2
    puerto=22

    echo "[$nombre_host] Copiando clave pública a $ip_destino..."

    # Intenta hasta 3 veces por si tarda en estar listo
    for intento in {1..3}; do
        sudo -u vagrant sshpass -p "vagrant" ssh-copy-id -o StrictHostKeyChecking=no -p "$puerto" vagrant@$ip_destino && break
        echo "[$nombre_host] Reintentando copia de clave ($intento)..."
        sleep 2
    done
}



# Función para verificar la conexión SSH

verificar_conexion_ssh() {
    nombre_host=$1
    ip_destino=$2

    echo "[$nombre_host] Verificando conexión SSH sin contraseña a $ip_destino..."

    if sudo -u vagrant ssh -o BatchMode=yes -o ConnectTimeout=5 vagrant@$ip_destino "echo OK" 2>/dev/null; then
        echo "[$nombre_host] Conexión establecida con $ip_destino"
        return 0
    else
        echo "[$nombre_host][ERROR] Fallo en la conexión con $ip_destino"
        return 1
    fi
    }
