#!/bin/bash

echo "[ADMIN] Instalando paquetes base..."
dnf install -y openssh-server nmap-ncat sshpass

echo "[ADMIN] Habilitando SSH..."
systemctl enable --now sshd

# Esperar a bastion
echo "[ADMIN] Esperando a bastion..."
while ! nc -z 192.168.20.10 22; do
  echo "Esperando a bastion (192.168.20.10:22)..."
  sleep 2
done

# Generar clave SSH si no existe
if [ ! -f /home/vagrant/.ssh/id_rsa ]; then
  echo "[ADMIN] Generando clave RSA..."
  sudo -u vagrant ssh-keygen -t rsa -N '' -f /home/vagrant/.ssh/id_rsa
fi

# Copiar clave pública a bastion
echo "[ADMIN] Copiando clave pública a bastion..."
sudo -u vagrant sshpass -p 'vagrant' ssh-copy-id -o StrictHostKeyChecking=no vagrant@192.168.20.10

# Probar conexión
echo "[ADMIN] Probando conexión SSH sin contraseña a bastion..."
sudo -u vagrant ssh -o BatchMode=yes vagrant@192.168.20.10 "echo 'Conexión exitosa desde admin-server'"

echo "[ADMIN] Configuración completada."
