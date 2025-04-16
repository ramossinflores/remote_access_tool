#!/bin/bash

echo "[DESTINATION] Iniciando configuración..."

# Verificar e instalar openssh-server si no está presente
if ! rpm -q openssh-server &> /dev/null; then
  echo "[DESTINATION] Instalando openssh..."
  dnf install -y openssh-server
else
  echo "[DESTINATION] openssh ya está instalado"
fi

# Instalar nmap-ncat si se desea mantener para depuración (opcional)
if ! rpm -q nmap-ncat &> /dev/null; then
  echo "[DESTINATION] Instalando ncat..."
  dnf install -y nmap-ncat
else
  echo "[DESTINATION] nmap-ncat ya está instalado"
fi

# Habilitar e iniciar el servicio SSH
echo "[DESTINATION] Habilitando y arrancando sshd..."
systemctl enable sshd
systemctl start sshd

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