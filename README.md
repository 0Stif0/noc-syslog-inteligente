# NOC Syslog Inteligente - Versión Alfa (v0.2.0)

**Estudiante:** Harold Stif Moreno Duran  
**Proyecto:** NOC Syslog Inteligente  
**Asignatura:** Administración y Gestión de Redes  
**Entorno:** Laboratorio simulado (Desarrollo local)

---

## 📋 Descripción del Proyecto

Aplicación unificada para la **Administración y Gestión de Redes** en entornos de laboratorio. Permite inventariar equipos de red (Cisco, Fortinet, Huawei), recibir e importar eventos Syslog, normalizar severidades conforme al estándar RFC 5424 (0–7), gestionar el ciclo de vida de incidentes, generar plantillas de configuración CLI comentadas y ofrecer una consola de diagnóstico simulada en modo de solo lectura.

---

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.10+ / FastAPI
- **Servidor ASGI:** Uvicorn
- **Base de Datos:** SQLite (`network_management.db`)
- **Frontend / Plantillas:** HTML5, CSS3, JavaScript, Jinja2
- **Validación y Entorno:** Pydantic v2, `python-dotenv`

---

## 📁 Estructura del Proyecto

```text
noc-syslog-inteligente/
├── .env.example              # Plantilla de variables de entorno
├── .gitignore                 # Archivos excluidos de Git
├── main.py                    # Punto de entrada de la aplicación FastAPI
├── network_management.db      # Base de datos SQLite local
├── README.md                  # Documentación principal del proyecto
├── requirements.txt           # Dependencias de Python
├── entregables/
│   └── ENTREGABLE_CORTE2.md   # Informe del Corte 2 (v0.2.0)
└── docs/
    └── architecture.md        # Especificación de arquitectura y requisitos