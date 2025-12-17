import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MandrinadosAnaid Chatbot API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar Gemini (Google AI)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.warning("⚠️ variable GOOGLE_API_KEY no encontrada. El bot no responderá con IA.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

# Modelo a usar
MODEL_NAME = "gemini-1.5-flash" 

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"message": "API Chatbot Mandrinados Anaid (Con IA) está en línea 🚀"}

@app.get("/health")
def health():
    return {"status": "ok", "ai_status": "configured" if GOOGLE_API_KEY else "missing_key"}

@app.post("/chat")
async def chat(req: ChatRequest):
    logger.info(f"Pregunta recibida: {req.message}")
    
    if not GOOGLE_API_KEY:
        return {"reply": "Error: El servidor no tiene configurada la API KEY de Google."}

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        # Instrucciones de sistema (System Prompt) simples
        prompt = (
            "Eres un asistente experto de la empresa 'Mandrinados Anaid'. "
            "Responde de forma profesional, breve y educada. "
            f"Usuario: {req.message}"
        )
        
        response = model.generate_content(prompt)
        reply_text = response.text
        
        return {"reply": reply_text}
    except Exception as e:
        logger.error(f"Error llamando a Gemini: {e}")
        return {"reply": "Lo siento, tuve un problema procesando tu solicitud."}

