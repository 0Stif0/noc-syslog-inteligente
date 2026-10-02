from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="NOC Syslog Inteligente")

# 1. Definimos la estructura de un mensaje de Syslog
class SyslogSchema(BaseModel):
    dispositivo: str    # Ejemplo: "Router-Principal" o "Switch-Piso2"
    prioridad: str      # Ejemplo: "CRITICAL", "WARNING", "INFO"
    mensaje: str        # Ejemplo: "Interfaz GigabitEthernet0/1 caida"

# 2. Esta función recibe el Syslog y detecta formato Cisco
@app.post("/syslog/recibir")
def recibir_syslog(log: SyslogSchema):
    # Agrega la hora exacta en la que tu servidor recibe el mensaje
    hora_recepcion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # NUEVO CAMBIO: Los equipos Cisco usan un símbolo de porcentaje '%' antes de sus códigos de error.
    # Aquí validamos si ese símbolo existe dentro del texto del mensaje.
    es_cisco = "%" in log.mensaje
    
    return {
        "estado": "Procesado con éxito",
        "fecha_registro": hora_recepcion,
        "es_dispositivo_cisco": es_cisco,
        "datos_recibidos": log
    }
