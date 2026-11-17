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

# 🛡️ Smart NOC Syslog - Enterprise Operations Suite v4.0

Plataforma centralizada de gestión de redes, monitoreo en tiempo real, respuesta automatizada a incidentes y ciberseguridad forense, desarrollada en Python (`Tkinter`).

---

## 🚀 Características Principales (v4.0)

* **🟢 Monitoreo Dinámico en Tiempo Real:** Visualización del estado operativo de dispositivos de red (`SW-CORE-01`, `RTR-BPL-02`, `FW-EDGE-01`, `AP-PISO2-05`) con bloqueo automático de estados ante fallas activas para evitar duplicidad de tickets.
* **📡 Colector Syslog RFC:** Clasificación de eventos por niveles de severidad (`0` al `7`), métricas KPI en vivo e integración de notificaciones instantáneas vía **Telegram Bot API**.
* **🔒 Seguridad Criptográfica (`AUDIT-SHA256`):** Registro de auditoría forense inalterable mediante un sistema de hashes encadenados (*Blockchain-lite*).
* **🛂 Control de Acceso Basado en Roles (RBAC):** Segregación de privilegios por perfil (*Operador L1*, *Ingeniero L2* y *Administrador*) bajo el principio de mínimo privilegio.
* **🛠️ Consola SSH & Troubleshooting Blindado:** Ejecución simulada de comandos de diagnóstico (`ping`, `tracert`, `show ip bgp summary`, `show arp`) vinculada a tickets abiertos, con sanitización estricta contra ataques de inyección de comandos.
* **🤖 Asistente Cognitivo IA & RCA:** Generación automática de Análisis de Causa Raíz (RCA) en la bitácora de cada incidente y chat interactivo para consultar el estado de la infraestructura.

---

## ⚙️ Modelo de Gobernanza Híbrida

1. **Incidentes Críticos (Niveles 0 – 4):** El sistema bloquea el dispositivo en monitoreo, abre un ticket en estado `ABIERTO (Requiere Humano)`, genera un diagnóstico preliminar de causa raíz y envía una alerta prioritaria a Telegram.
2. **Eventos de Rutina (Niveles 5 – 7):** El automatismo abre y cierra el ticket de forma autónoma (`RESUELTO & CERRADO`), notificando por Telegram sin interrumpir la operación humana.

---

## 📦 Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/0Stif0/noc-syslog-inteligente.git](https://github.com/0Stif0/noc-syslog-inteligente.git)
   cd noc-syslog-inteligente