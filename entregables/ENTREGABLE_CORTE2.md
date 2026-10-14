
# Documento de Entrega: Corte 2 - v0.2.0 (MVP)

**Estudiante:** Harold Stif Moreno Duran  
**Programa:** Ingeniería de Telecomunicaciones  
**Asignatura:** Administración y Gestión de Redes  
**Proyecto:** NOC Syslog Inteligente  
**Versión:** v0.2.0 (Producto Mínimo Viable)

---

## 1. Repositorio y Configuración Base
* **Estado del Repositorio:** El proyecto cuenta con un repositorio individual alojado en GitHub (`noc-syslog-inteligente`).
* **Control de Versiones y Exclusiones:** Se configuró un archivo `.gitignore` para garantizar que archivos sensibles o pesados (como el entorno virtual `venv/`, bases de datos locales o variables de entorno `.env`) no se suban al repositorio remoto.
* **Licencia y Términos de Uso:** Cuenta con una licencia MIT orientada a uso estrictamente académico y educativo.
* **Documentación Principal:** Se dispone de un `README.md` estructurado que detalta el stack tecnológico, prerequisitos y la guía de instalación.

---

## 2. Alcance, Requisitos, Diagramas e Historias de Usuario

### 2.1. Alcance y Método 4-D
* **Deconstruir:** El objetivo es construir un sistema liviano para la gestión de dispositivos de red, ingestión y normalización de Syslog, atención de incidentes y consola de diagnóstico simulada.
* **Diagnosticar:** Se definieron supuestos de laboratorio local para reducir riesgos de dependencias externas.
* **Desarrollar:** Arquitectura modular construida sobre Python, FastAPI, SQLite y plantillas HTML/JS.
* **Entregar:** Versión v0.2.0 ejecutable para pruebas de laboratorio.

### 2.2. Historias de Usuario Principales
1. **HU-01 (Inventario):** Como Administrador de Red, quiero registrar y consultar equipos con su fecha de actualización para mantener un control preciso de los activos.
2. **HU-02 (Normalización Syslog):** Como Operador L1, quiero cargar registros Syslog y clasificarlos en severidades de 0 a 7 para identificar fallas críticas rápidamente.
3. **HU-03 (Gestión de Incidentes):** Como Analista NOC, quiero gestionar las alertas recibidas mediante un estado y priorización para dar trazabilidad a los problemas.
4. **HU-04 (Configuración Multivendor):** Como Ingeniero de Red, quiero generar plantillas CLI comentadas para Cisco, Fortinet y Huawei para desplegar cambios estandarizados sin errores de sintaxis.
5. **HU-05 (Consola Simulada):** Como Operador L1, quiero ejecutar comandos de diagnóstico en modo solo lectura para revisar el estado del equipo de forma segura.

### 2.3. Diagrama Arquitectónico y Modelo de Datos
```text
+-----------------------+       +-------------------------+       +------------------------+
|      DISPOSITIVO      |       |      EVENTO SYSLOG      |       |        INCIDENTE       |
+-----------------------+       +-------------------------+       +------------------------+
| id (PK)               |<------| id (PK)                 |------>| id (PK)                |
| nombre                | 1   * | device_id (FK)          | *   1 | device_id (FK)         |
| ip                    |       | timestamp               |       | titulo                 |
| marca (Vendor)        |       | facility                |       | severidad              |
| modelo                |       | severidad (0-7)         |       | estado                 |
| version_so            |       | mensaje                 |       | responsable            |
| estado                |       | es_sintetico            |       | fecha_creacion         |
| fecha_actualizacion   |       +-------------------------+       +------------------------+
+-----------------------+