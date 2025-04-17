
#!/bin/bash

# Cargar funciones comunes
source /vagrant/scripts/funciones_comunes.sh

instalar_paquetes_base "ADMIN-SERVER"
habilitar_ssh "ADMIN-SERVER"
esperar_puerto "ADMIN-SERVER" 192.168.20.10 22
generar_clave_ssh "ADMIN-SERVER"
registrar_known_host "ADMIN-SERVER" 192.168.20.10
copiar_clave_ssh "ADMIN-SERVER" 192.168.20.10 22
verificar_conexion_ssh "ADMIN" 192.168.20.10

# Instalar PostgreSQL 
echo "[ADMIN]  Instalando PostgreSQL."
sudo dnf install -y postgresql-server postgresql

# Inicializar y habilitar el servicio
echo "[ADMIN] Inicializando base de datos"
sudo postgresql-setup --initdb

echo "[ADMIN] Habilitando y arrancando servicio PostgreSQL..."
sudo systemctl enable --now postgresql

# Configurar pg_hba.conf
pg_hba="/var/lib/pgsql/data/pg_hba.conf"
echo "[ADMIN] Verificando reglas en pg_hba.conf..."

# Limpiar reglas anteriores si existieran
sudo sed -i '/127\.0\.0\.1\/32/d' "$pg_hba"
sudo sed -i '/::1\/128/d' "$pg_hba"


if ! grep -q "^host\s\+all\s\+all\s\+127\.0\.0\.1/32\s\+md5" "$pg_hba"; then
  echo "host all all 127.0.0.1/32 md5" | sudo tee -a "$pg_hba"
fi

if ! grep -q "^host\s\+all\s\+all\s\+::1/128\s\+md5" "$pg_hba"; then
  echo "host all all ::1/128 md5" | sudo tee -a "$pg_hba"
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
sql_file="/vagrant/data.sql"
# Verificar existencia del archivo SQL antes de cargarlo

if [ ! -f "$sql_file" ]; then
  echo "[ERROR] No se encontró el archivo $sql_file"
  exit 1
fi
echo "[ADMIN] Cargando archivo SQL: $sql_file"
sudo -u postgres psql -d infra_db -f "$sql_file" 2>/dev/null

echo "[ADMIN] Dando permisos de lectura al usuario 'vagrant'..."
sudo -u postgres psql -d infra_db -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO vagrant;" 2>/dev/null
sudo -u postgres psql -d infra_db -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO vagrant;" 2>/dev/null

echo "[ADMIN] Probando acceso del usuario 'vagrant' a la base de datos..."
pgpassword=vagrant psql -U vagrant -d infra_db -h 127.0.0.1 -c "\dt" && \
echo "[ADMIN] Conexión de prueba exitosa con el usuario 'vagrant'" || \
echo "[ADMIN] Error de conexión con el usuario 'vagrant'"


echo "[ADMIN] Instalando Python, pip y entorno virtual..."
sudo dnf install -y python3 python3-pip python3-virtualenv

# Crear entorno virtual si no existe
venv_path="/home/vagrant/venv"
if [ ! -d "$venv_path" ]; then
  echo "[ADMIN] Creando entorno virtual en $venv_path..."
  sudo -u vagrant python3 -m venv "$venv_path"
fi

# Instalar requerimientos del script de automatización
echo "[ADMIN] Instalando dependencias desde requirements.txt..."
sudo -u vagrant "$venv_path/bin/pip" install --upgrade pip
sudo -u vagrant "$venv_path/bin/pip" install -r /vagrant/remote_access_tool/requirements.txt

# Comprobación rápida
echo "[ADMIN] Verificando instalación de paquetes..."
sudo -u vagrant "$venv_path/bin/python" -c "import psycopg2, paramiko, dotenv; print('Todos los paquetes importados correctamente')"

