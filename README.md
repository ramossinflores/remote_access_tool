# 🛠️ Remote Access SSH Tool 🦘 - Proyecto Integrado ASIR | Entorno de pruebas

Este proyecto forma parte del Proyecto Integrado del ciclo formativo de Grado Superior en Administración de Sistemas Informáticos en Red (ASIR). Simula un entorno real de acceso remoto mediante salto SSH entre múltiples máquinas, usando Vagrant y VirtualBox. El objetivo es probar un script de automatización llamado `remote_access_tool.py`, que recibe como argumento el nombre o la IP del servidor destino, y accede a través de uno o varios bastiones intermedios. mediante salto SSH entre múltiples máquinas.

 🚧 Work In Progress – en desarrollo activo.

## 🔧 Escenario implementado

- `admin-server`: contiene el script de automatización, la base de datos PostgreSQL y un entorno virtual Python.
- `bastion`: actúa como nodo intermedio para enrutar conexiones SSH desde `admin-server` hacia `destination`.
- `destination`: máquina final que recibe la conexión SSH mediante salto.

Las máquinas están en redes distintas y no comparten relación directa fuera del salto SSH, lo que simula un entorno segmentado.

## 📁 Estructura del proyecto

```
entorno_pruebas/
entorno_pruebas/
├── Vagrantfile
├── data.sql
├── .env
├── .gitignore
├── scripts/
│   ├── provision_admin.sh
│   ├── provision_bastion.sh
│   ├── provision_destination.sh
│   └── common_functions.sh
├── remote_access_tool/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── ssh.py
│   ├── interactive.py
│   ├── main.py
│   ├── utils.py
│   ├── requirements.txt
│   └── app.log
└── tests/
    ├── unit/
    │   └── test_*.py
    └── integration/
        └── test_*.py
   
```

## 🧪 Tipos de pruebas

- **Unitarias:** verifican funciones individuales como la conexión SSH, validación de parámetros, etc.
- **Integración:** validan el comportamiento conjunto entre base de datos y lógica de conexión.

Ejecutar todas las pruebas:

```bash
pytest tests/ -v

```

## 🚀 Requisitos

- Vagrant
- VirtualBox
- Git

## 🖥️ Cómo iniciar el entorno

1. Clona el repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd entorno_pruebas
   ```

2. Levanta el entorno con Vagrant:
   ```bash
   vagrant up
   ```

Esto creará las tres máquinas virtuales con sus respectivas configuraciones y relaciones de confianza SSH 😊

## 🧰 Provisión automática

- Instalación de paquetes base (`openssh-server`, `ncat`, `sshpass`, `postgresql`, `python3`)
- Configuración de confianza SSH:
  - `admin-server → bastion`
  - `bastion → destination`
- Preparación de la base de datos `infra_db` en `admin-server` con datos cargados desde `data.sql`
- Creación de entorno virtual en `/home/vagrant/venv` y carga de dependencias desde `requirements.txt`

## 🛠️ Script de automatización

Una vez el entorno está listo, se puede acceder a `admin-server` y ejecutar el script de salto SSH:

```bash
vagrant ssh admin-server
cd /vagrant/remote_access_tool
source ~/venv/bin/activate
python3 remote_access_tool.py <nombre_o_ip_destino>
```

Este script consulta la base de datos `infra_db` para obtener la ruta de salto (bastión y destino) asociada al nombre o IP proporcionado, y establece una conexión SSH usando la lógica de salto desde `admin-server` hacia `destination` a través de `bastion` 🦘

## 👩‍💻 Autoría

Desarrollado por **Laura Ramos Granados**  
📧 [LinkedIn](https://www.linkedin.com/in/emele-ramos-granados/) |  [GitHub](https://github.com/ramossinflores)

---

## 📄 Licencia

Proyecto desarrollado con fines educativos. Puedes usarlo, adaptarlo o expandirlo libremente 💛