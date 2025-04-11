#!/bin/bash

echo "[DESTINATION] Instalando paquetes base..."
dnf install -y openssh-server nmap-ncat

echo "[DESTINATION] Habilitando SSH..."
systemctl enable --now sshd

echo "[DESTINATION] Configuración completada."
