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
├── Vagrantfile
├── data.sql
├── .env
├── scripts/
│   ├── common_functions.sh
│   ├── provision_admin.sh
│   ├── provision_bastion.sh
│   └── provision_destination.sh
├── remote_access_tool/
│   ├── __init__.py
│   ├── app.py                  # Interfaz web con Flask ( para el dashboard)
│   ├── config.py               # Carga .env y configuración de logging
│   ├── db.py                   # Módulo de acceso a PostgreSQL
│   ├── interactive.py          # Sesión SSH interactiva
│   ├── main.py                 # Punto de entrada del script CLI
│   ├── ssh.py                  # Funciones para conexión SSH
│   ├── utils.py                # Script completo (al inicio, no estaba modular)
│   ├── requirements.txt
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       └── index.html
├── tests/
│   ├── integration/
│   │   ├── test_parametro_invalido.py
│   │   └── test_salto_completo.py
│   └── unit/
│       ├── __init__.py
│       ├── test_db.py
│       └── test_ssh.py
├── .gitignore
├── README.md

```

## 📊 Interfaz web (Dashboard)

Se encuentra en desarrollo una **interfaz web de administración** construida con **Flask**, ubicada en `remote_access_tool/app.py`, que permite lanzar consultas sobre servidores destino mediante nombre o IP.

El dashboard actualmente:

- Consulta la base de datos.
- Ejecuta el salto SSH automáticamente.
- Muestra información del sistema remoto (`hostname`, `uptime`, uso de CPU, disco y procesos).
- Usa plantillas HTML con `Chart.js` y estilos CSS propios.

> ⚠️ *Este módulo está en construcción. El código aún no ha sido refactorizado ni optimizado para producción.*

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
cd /vagrant/
source ~/venv/bin/activate
python3 -m remote_access_tool.main <nombre_o_ip_destino>
```

Este script consulta la base de datos `infra_db` para obtener la ruta de salto (bastión y destino) asociada al nombre o IP proporcionado, y establece una conexión SSH usando la lógica de salto desde `admin-server` hacia `destination` a través de `bastion` 🦘

## 🧭 Posibles mejoras

En futuras versiones se añadirá soporte para **saltos SSH encadenados a través de múltiples bastiones**, y se refactorizará tanto la lógica del script como la base de datos. El **dashboard web** también será reorganizado en módulos independientes, incorporando autenticación, mejor gestión de errores y mejoras visuales. Se prevé además refactorizar el **HTML, CSS y JavaScript** del panel para optimizar su estructura y estilo, que actualmente se corresponde con el tiempo limitado para ejecutarlo y la flexibilidad de estar en pruebas. Finalmente, se considera migrar el entorno de pruebas a **Docker**, facilitando el despliegue y su integración con CI/CD.

> **Se vienen cambios** 🙏🏾

## 📄 Licencia

Este es mi **Proyecto Integrado**, que ha sido desarrollado con fines **educativos y de aprendizaje personal** como parte de mis estudios en el ciclo de **Administración de Sistemas Informáticos en Red (ASIR)** ❤️.

Lo comparto como estudiante y aprendiz, sin garantías de funcionamiento en entornos productivos.  
El código puede contener errores, implementaciones mejorables o estar en fase de experimentación.

Eres libre de usarlo, adaptarlo o mejorarlo citando la fuente original 💛
Toda sugerencia o corrección es bienvenida, ya que me encuentro en pleno proceso de formación 🙌

## 👩‍💻 Autoría

Desarrollado por **Laura Ramos Granados**  
📧 [LinkedIn](https://www.linkedin.com/in/emele-ramos-granados/) |  [GitHub](https://github.com/ramossinflores)
