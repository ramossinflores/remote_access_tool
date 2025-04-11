#!/bin/bash

echo "[BASTION] Instalando paquetes base..."
dnf install -y openssh-server nmap-ncat sshpass

echo "[BASTION] Habilitando SSH..."
systemctl enable --now sshd

# Esperar a destination
echo "[BASTION] Esperando a destination..."
while ! nc -z 192.168.10.10 22; do
  echo "Esperando a destination (192.168.10.10:22)..."
  sleep 2
done

# Generar clave SSH si no existe
if [ ! -f /home/vagrant/.ssh/id_rsa ]; then
  echo "[BASTION] Generando clave RSA..."
  sudo -u vagrant ssh-keygen -t rsa -N '' -f /home/vagrant/.ssh/id_rsa
fi

# Copiar clave pública a destination
echo "[BASTION] Copiando clave pública a destination..."
sudo -u vagrant sshpass -p 'vagrant' ssh-copy-id -o StrictHostKeyChecking=no vagrant@192.168.10.10

# Probar conexión
echo "[BASTION] Probando conexión SSH sin contraseña a destination..."
sudo -u vagrant ssh -o BatchMode=yes vagrant@192.168.10.10 "echo 'Conexión exitosa desde bastion'"

echo "[BASTION] Configuración completada."
