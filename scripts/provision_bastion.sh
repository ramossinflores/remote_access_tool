#!/bin/bash

# Cargar funciones comunes
source /vagrant/scripts/funciones_comunes.sh

instalar_paquetes_base "BASTION"
habilitar_ssh "BASTION"
esperar_puerto "BASTION" 192.168.10.10 22
generar_clave_ssh "BASTION"
registrar_known_host "BASTION" 192.168.10.10

copiar_clave_ssh "BASTION" 192.168.10.10

# Esperar un poquito para que todo se estabilice
sleep 3

verificar_conexion_ssh "BASTION" 192.168.10.10