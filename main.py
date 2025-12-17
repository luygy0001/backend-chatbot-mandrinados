import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configurar logs para verlos en el dashboard de Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MandrinadosAnaid Chatbot API")

# CORS: Permitir acceso desde cualquier origen (ajustar en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    logger.info("Acceso al root endpoint verificado.")
    return {"message": "API Chatbot Mandrinados Anaid está en línea 🚀"}

@app.get("/health")
def health():
    logger.info("Health check solicitado.")
    return {"status": "ok", "environment": os.getenv("RAILWAY_ENVIRONMENT", "local")}

@app.post("/chat")
def chat(req: ChatRequest):
    logger.info(f"Mensaje recibido: {req.message}")
    # De momento respuesta fija para comprobar
    return {"reply": f"Confirmado, backend activo. Recibí: {req.message}"}

