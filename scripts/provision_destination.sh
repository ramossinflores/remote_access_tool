#!/bin/bash

echo "[DESTINATION] Instalando paquetes base..."
dnf install -y openssh-server nmap-ncat

echo "[DESTINATION] Habilitando SSH..."
systemctl enable sshd
systemctl start sshd

# Preparar carpeta .ssh del usuario vagrant
echo "[DESTINATION] Preparando ~/.ssh para aceptar claves..."
mkdir -p /home/vagrant/.ssh
touch /home/vagrant/.ssh/authorized_keys
chmod 700 /home/vagrant/.ssh
chmod 600 /home/vagrant/.ssh/authorized_keys
chown -R vagrant:vagrant /home/vagrant/.ssh

# Reiniciar sshd con manejo de errores
echo "[DESTINATION] 🔄 Intentando reiniciar sshd..."
if systemctl restart sshd; then
  echo "[DESTINATION] ✅ sshd reiniciado correctamente"
else
  echo "[DESTINATION] ⚠️ Error al reiniciar sshd"
fi

echo "[DESTINATION] ✅ Listo para recibir clave pública desde bastion"
