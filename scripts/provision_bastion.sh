#!/bin/bash

echo "[BASTION] Instalando paquetes base..."
dnf install -y openssh-server nmap-ncat sshpass

echo "[BASTION] Habilitando SSH..."
systemctl enable --now sshd

# Esperar a destination (192.168.10.10:22)
echo "[BASTION] Esperando a destination..."
while ! nc -z 192.168.10.10 22; do
  echo "⏳ Esperando a que destination (192.168.10.10:22) esté disponible..."
  sleep 2
done

echo "[BASTION] ⏳ Esperando a que destination permita conexión SSH con contraseña..."
while ! sshpass -p 'vagrant' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 vagrant@192.168.10.10 "echo 'SSH OK'" >/dev/null 2>&1; do
  echo "⌛ Aún no responde por SSH... reintentando"
  sleep 2
done

# Generar clave si no existe
if [ ! -f /home/vagrant/.ssh/id_rsa ]; then
  echo "[BASTION] Generando clave RSA..."
  sudo -u vagrant ssh-keygen -t rsa -N '' -f /home/vagrant/.ssh/id_rsa
fi

# Agregar la clave del host destination al known_hosts de bastion (usuario vagrant)
echo "[BASTION] 📥 Registrando clave de host de destination..."
sudo -u vagrant ssh-keygen -R 192.168.10.10 >/dev/null 2>&1
sudo -u vagrant ssh-keyscan -H 192.168.10.10 >> /home/vagrant/.ssh/known_hosts


echo "[BASTION] 🔐 Estableciendo confianza SSH con destination..."
PUB_KEY=$(cat /home/vagrant/.ssh/id_rsa.pub)

sudo -u vagrant sshpass -p 'vagrant' ssh -o StrictHostKeyChecking=no vagrant@192.168.10.10 "
  mkdir -p /home/vagrant/.ssh &&
  chmod 700 /home/vagrant/.ssh &&
  echo \"$PUB_KEY\" >> /home/vagrant/.ssh/authorized_keys &&
  chmod 600 /home/vagrant/.ssh/authorized_keys &&
  chown -R vagrant:vagrant /home/vagrant/.ssh"



# Esperar un poquito para que todo se estabilice
sleep 3

for i in {1..3}; do
  if sudo -u vagrant ssh -o BatchMode=yes -o ConnectTimeout=5 vagrant@192.168.10.10 "echo OK" 2>/dev/null; then
    echo "[BASTION] ✅ Conexión establecida con destination sin contraseña"
    break
  else
    echo "[BASTION] 🔁 Reintentando conexión..."
    sleep 2
  fi
done