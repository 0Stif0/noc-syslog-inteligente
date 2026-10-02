from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="NOC Syslog Inteligente")

class SyslogSchema(BaseModel):
    dispositivo: str
    prioridad: str
    mensaje: str

@app.post("/syslog/recibir")
def recibir_syslog(log: SyslogSchema):
    hora_recepcion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    es_cisco = "%" in log.mensaje
    
    # NUEVO CAMBIO PEQUEÑO: Detectar si la prioridad requiere atencion inmediata
    es_critica = log.prioridad.upper() == "CRITICAL"
    
    return {
        "estado": "Procesado con éxito",
        "fecha_registro": hora_recepcion,
        "es_dispositivo_cisco": es_cisco,
        "requiere_alerta_urgente": es_critica, # Agregamos este resultado
        "datos_recibidos": log
    }

