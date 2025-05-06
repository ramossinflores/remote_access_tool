#!/bin/bash

source /vagrant/scripts/common_functions.sh

instalar_paquetes_base "DESTINATION"
habilitar_ssh "DESTINATION"

# Preparar la carpeta .ssh del usuario vagrant para aceptar claves públicas
echo "[DESTINATION] Configurando carpeta ~/.ssh del usuario vagrant..."
mkdir -p /home/vagrant/.ssh
touch /home/vagrant/.ssh/authorized_keys
chmod 700 /home/vagrant/.ssh
chmod 600 /home/vagrant/.ssh/authorized_keys
chown -R vagrant:vagrant /home/vagrant/.ssh

# Reiniciar sshd y mostrar estado
echo "[DESTINATION] Reiniciando sshd..."
if systemctl restart sshd; then
  echo "[DESTINATION] sshd reiniciado"
else
  echo "[DESTINATION] Error al reiniciar sshd"
fi