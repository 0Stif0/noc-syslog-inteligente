
# Documento de Entrega: Corte 2 - v0.2.0 (Producto Mínimo Viable - MVP)

**Estudiante:** Harold Stif Moreno Duran  
**Programa:** Ingeniería de Telecomunicaciones  
**Asignatura:** Administración y Gestión de Redes  
**Proyecto:** NOC Syslog Inteligente  
**Versión:** v0.2.0 (MVP)  
**Repositorio GitHub:** [https://github.com/0Stif0/noc-syslog-inteligente](https://github.com/0Stif0/noc-syslog-inteligente)

---

## 📄 Cumplimiento de Requisitos del Producto Mínimo Viable (MVP)

### 1. Repositorio Individual y Configuración Base
- **Repositorio Público:** Creado de forma individual y configurado como público para acceso y revisión del docente.
- **Fichero README.md:** Ubicado en la raíz del proyecto. Documenta el stack tecnológico (Python, FastAPI, SQLite, Jinja2), prerrequisitos e instrucciones detalladas de instalación y ejecución.
- **Licencia / Uso Académico:** Archivo `LICENSE` (MIT) que especifica los términos de uso estrictamente académicos y educativos.
- **Exclusión de Ficheros (.gitignore):** Configurado para evitar subir entornos virtuales (`venv/`), base de datos local (`network_management.db`) y secretos (`.env`).

---

### 2. Alcance, Requisitos, Diagrama, Modelo de Datos e Historias
- **Alcance (Método 4-D):**
  1. *Deconstruir:* Sistema unificado para inventario de equipos, ingesta de trazas Syslog, gestión de incidentes y consola de diagnóstico simulada.
  2. *Diagnosticar:* Mitigación de riesgos operativos limitando las ejecuciones de red a entornos simulados y comandos de lectura.
  3. *Desarrollar:* Arquitectura modular basada en FastAPI y SQLite con renderizado de vistas dinámicas.
  4. *Entregar:* Aplicación funcional v0.2.0 probada en laboratorio local.
- **Requisitos Funcionales Clave:** CRUD de inventario, ingesta de logs, clasificación de severidad RFC 5424 (0–7), dashboard operativo, generación de configuraciones multivendor y consola simulada read-only.
- **Modelo de Datos y Diagrama ER:**
  ```text
  +-----------------------+       +-------------------------+       +------------------------+
  |      DISPOSITIVO      |       |      EVENTO SYSLOG      |       |        INCIDENTE       |
  +-----------------------+       +-------------------------+       +------------------------+
  | id (PK)               |<------| id (PK)                 |------>| id (PK)                |
  | nombre                | 1   * | device_id (FK)          | *   1 | device_id (FK)         |
  | ip                    |       | timestamp               |       | titulo                 |
  | marca (Vendor)        |       | facility                |       | severidad (0-7)        |
  | modelo                |       | severidad (0-7)         |       | estado                 |
  | version_so            |       | mensaje                 |       | responsable            |
  | estado                |       | es_sintetico            |       | fecha_creacion         |
  | fecha_actualizacion   |       +-------------------------+       +------------------------+
  +-----------------------+