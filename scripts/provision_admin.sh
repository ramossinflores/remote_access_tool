
#!/bin/bash

echo "[ADMIN] Instalando paquetes base..."
dnf install -y openssh-server nmap-ncat sshpass

echo "[ADMIN] Habilitando SSH..."
systemctl enable --now sshd

# Esperar a bastion (192.168.20.10:22)
echo "[ADMIN] Esperando a bastion..."
while ! nc -z 192.168.20.10 22; do
  echo "Esperando a bastion..."
  sleep 2
done

# Generar clave si no existe
if [ ! -f /home/vagrant/.ssh/id_rsa ]; then
  echo "[ADMIN] Generando clave RSA..."
  sudo -u vagrant ssh-keygen -t rsa -N '' -f /home/vagrant/.ssh/id_rsa
fi

# Copiar clave a bastion
echo "[ADMIN] Estableciendo confianza SSH con bastion..."
sudo -u vagrant sshpass -p 'vagrant' ssh-copy-id -o StrictHostKeyChecking=no vagrant@192.168.20.10

# Verificar conexión
echo "[ADMIN] Verificando conexión sin contraseña con bastion..."
if sudo -u vagrant ssh -o BatchMode=yes -o ConnectTimeout=5 vagrant@192.168.20.10 "echo OK" 2>/dev/null; then
  echo "[ADMIN] Conexión establecida con bastion"
else
  echo "[ADMIN] Fallo en la conexión con bastion"
fi


# Probar conexión
echo "[ADMIN] Probando conexión SSH sin contraseña a bastion..."
sudo -u vagrant ssh -o BatchMode=yes vagrant@192.168.20.10 "echo 'Conexión exitosa desde admin-server'"

# Instalar PostgreSQL 
echo "[ADMIN]  Instalando PostgreSQL."
sudo dnf install -y postgresql-server postgresql

# Inicializar y habilitar el servicio
echo "[ADMIN] Inicializando base de datos"
sudo postgresql-setup --initdb

echo "[ADMIN] Habilitando y arrancando servicio PostgreSQL..."
sudo systemctl enable --now postgresql

# Configurar pg_hba.conf
PG_HBA="/var/lib/pgsql/data/pg_hba.conf"
echo "[ADMIN] Verificando reglas en pg_hba.conf..."

# Limpiar reglas anteriores si existieran
sudo sed -i '/127\.0\.0\.1\/32/d' "$PG_HBA"
sudo sed -i '/::1\/128/d' "$PG_HBA"


if ! grep -q "^host\s\+all\s\+all\s\+127\.0\.0\.1/32\s\+md5" "$PG_HBA"; then
  echo "host all all 127.0.0.1/32 md5" | sudo tee -a "$PG_HBA"
fi

if ! grep -q "^host\s\+all\s\+all\s\+::1/128\s\+md5" "$PG_HBA"; then
  echo "host all all ::1/128 md5" | sudo tee -a "$PG_HBA"
fi

echo "[ADMIN] Reiniciando servicio PostgreSQL..."
sudo systemctl restart postgresql

# Crear usuario, base de datos y cargar SQL
echo "[ADMIN] Creando usuario 'vagrant' y base de datos 'infra_db'..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='vagrant'" 2>/dev/null | grep -q 1 || \
sudo -u postgres psql -c "CREATE USER vagrant WITH PASSWORD 'vagrant';" 2>/dev/null

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='infra_db'" 2>/dev/null | grep -q 1 || \
sudo -u postgres psql -c "CREATE DATABASE infra_db OWNER vagrant;" 2>/dev/null

# Usar ruta del archivo montado por Vagrant
SQL_FILE="/vagrant/data.sql"
echo "[ADMIN] Cargando archivo SQL: $SQL_FILE"
sudo -u postgres psql -d infra_db -f "$SQL_FILE" 2>/dev/null

echo "[ADMIN] Dando permisos de lectura al usuario 'vagrant'..."
sudo -u postgres psql -d infra_db -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO vagrant;" 2>/dev/null
sudo -u postgres psql -d infra_db -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO vagrant;" 2>/dev/null

echo "[ADMIN] Probando acceso del usuario 'vagrant' a la base de datos..."
PGPASSWORD=vagrant psql -U vagrant -d infra_db -h 127.0.0.1 -c "\dt" && \
echo "[ADMIN] Conexión de prueba exitosa con el usuario 'vagrant'" || \
echo "[ADMIN] Error de conexión con el usuario 'vagrant'"


echo "[ADMIN] Instalando Python, pip y entorno virtual..."
sudo dnf install -y python3 python3-pip python3-virtualenv

# Crear entorno virtual si no existe
VENV_PATH="/home/vagrant/venv"
if [ ! -d "$VENV_PATH" ]; then
  echo "[ADMIN] Creando entorno virtual en $VENV_PATH..."
  sudo -u vagrant python3 -m venv "$VENV_PATH"
fi

# Instalar requerimientos del script de automatización
echo "[ADMIN] Instalando dependencias desde requirements.txt..."
sudo -u vagrant "$VENV_PATH/bin/pip" install --upgrade pip
sudo -u vagrant "$VENV_PATH/bin/pip" install -r /vagrant/remote_access_tool/requirements.txt

# Comprobación rápida
echo "[ADMIN] Verificando instalación de paquetes..."
sudo -u vagrant "$VENV_PATH/bin/python" -c "import psycopg2, paramiko, dotenv; print('Todos los paquetes importados correctamente')"

