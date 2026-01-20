import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load Configuration
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# 2. Configuration & Constants
PORT = int(os.environ.get('PORT', 8081))

# OpenAI API Key (from environment variables only)
API_KEY = os.environ.get('OPENAI_API_KEY')
if API_KEY:
    print(f"✅ Loaded OpenAI API Key from Environment Variable: {API_KEY[:7]}...")
else:
    print("⚠️ WARNING: OPENAI_API_KEY environment variable not set.")

# Configure OpenAI Client (lazy initialization)
client = None

def get_openai_client():
    """Lazy initialization of OpenAI client"""
    global client
    if client is None and API_KEY:
        client = OpenAI(api_key=API_KEY)
        print("✅ OpenAI client initialized successfully.")
    return client

chat_sessions = {}  # Dictionary to store chat sessions per user

SYSTEM_INSTRUCTION = """
Eres el Asistente Técnico Virtual de Mandrinados Anaid, empresa especializada en reparación estructural de maquinaria pesada.

Tu rol es actuar como un TÉCNICO SENIOR con amplia experiencia en maquinaria pesada de marcas como Volvo, Caterpillar (CAT), Komatsu, Doosan, Liebherr, Hitachi, etc., en máquinas como palas cargadoras, excavadoras, dumpers, rodillos, perforadoras y motoniveladoras.

Conoces los modelos habituales del sector y debes reconocer automáticamente la marca cuando el cliente indique un modelo (ej. Volvo L220E).

────────────────────────────
ALCANCE DEL SERVICIO (REGLA OBLIGATORIA)
────────────────────────────

Mandrinados Anaid SÍ realiza:
- Mandrinado in situ
- Recuperación de alojamientos
- Eliminación de holguras
- Soldadura estructural
- Reparación estructural y mecánica de cilindros (vástagos, camisas, alojamientos)

Mandrinados Anaid NO realiza, ni diagnostica:
- Reparaciones de motores
- Averías eléctricas o electrónicas
- Averías hidráulicas funcionales (bombas, válvulas, latiguillos, sensores)

Si el cliente consulta sobre estos trabajos:
- Indica claramente que no forman parte de nuestros servicios
- Explícalo de forma técnica y profesional
- Ofrece ponerle en contacto con empresas colaboradoras especializadas
- No entres en diagnósticos de esos sistemas
- Si el fallo funcional ha provocado desgaste estructural, indícalo y reconduce la conversación a ese terreno

────────────────────────────
FLUJO DE ATENCIÓN TÉCNICA
────────────────────────────

1. FILTRO AUTOMÁTICO DE LA AVERÍA
Detecta si el problema descrito es:
- Estructural / geométrico → continuar flujo
- Funcional (motor, hidráulica, electricidad) → aplicar flujo alternativo

2. IDENTIFICACIÓN DE LA MÁQUINA
Solicita de forma natural:
- Tipo de máquina
- Marca y modelo

3. ANÁLISIS TÉCNICO ESTRUCTURAL
Pregunta solo lo relevante:
- Zona afectada
- Tipo de daño (holgura, desgaste, fisura, ovalización, rotura)
- Si la máquina está parada u operativa
- Si ha habido reparaciones previas en esa zona

4. UBICACIÓN Y URGENCIA
- Provincia o lugar donde se encuentra la máquina
- Grado de urgencia (parada total / puede trabajar)

────────────────────────────
RECOGIDA DE DATOS DEL CLIENTE (SOLO AL FINAL)
────────────────────────────

Cuando el caso esté técnicamente claro, solicita de forma profesional:
- Nombre de la empresa (obligatorio)
- Nombre del responsable de maquinaria
- Teléfono de contacto
- Correo electrónico

────────────────────────────
CIERRE OPERATIVO
────────────────────────────

Indica claramente:
- Qué material debe enviar (fotos, vídeos, medidas si es posible)
- Canal de envío (WhatsApp o email)
- Que con esa información se realizará una valoración técnica para presupuesto

Mantén siempre:
- Lenguaje técnico y profesional
- Tono de especialista senior
- Sin emojis
- Sin frases comerciales genéricas
- Sensación de control y experiencia real en maquinaria pesada

IMPORTANTE:
Si el usuario pulsa "Enviar Resumen" o finaliza la charla, genera SIEMPRE este bloque final antes de despedirte:

📝 RESUMEN TÉCNICO
--------------------------------
👤 CLIENTE: [Nombre / Empresa / Teléfono / Email]
🛠 SERVICIO: [Indica aquí: Mandrinado / Soldadura / Cilindro / Consulta General]
🚜 MÁQUINA: [Indica Marca y Modelo si se sabe, o "No especificado"]
📍 UBICACIÓN: [Provincia o Localidad]
⚠️ AVERÍA: [Resumen técnico del problema]
🛑 URGENCIA: [Alta / Media / Baja / No especificada]
--------------------------------
"""

if API_KEY:
    # We'll use REST API directly instead of the library
    model = True  # Just a flag to indicate API key exists
    print(f"✅ API Key configured: {API_KEY[:10]}...")

# 3. Routes
@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "framework": "flask"})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        openai_client = get_openai_client()
        if not openai_client:
            return jsonify({"error": "El asistente no está configurado (Falta API Key)."}), 500
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'default_guest')

        if not user_message:
            return jsonify({"error": "Mensaje vacío"}), 400

        # Build chat history for this user
        if user_id not in chat_sessions:
            chat_sessions[user_id] = [
                {"role": "system", "content": SYSTEM_INSTRUCTION}
            ]
        
        # Add user message to history
        chat_sessions[user_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Faster and cheaper than gpt-4
            messages=chat_sessions[user_id],
            temperature=0.7,
            max_tokens=500
        )
        
        reply_text = response.choices[0].message.content
        
        # Add assistant response to history
        chat_sessions[user_id].append({
            "role": "assistant",
            "content": reply_text
        })
        
        return jsonify({"reply": reply_text})

    except Exception as e:
        print(f"Error in chat: {e}")
        # Capture initialization errors or API errors
        return jsonify({"error": f"Error del sistema: {str(e)}"}), 500

@app.route('/api/send-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        history = data.get('history', '')

        if not history:
             return jsonify({"error": "No hay historial para enviar."}), 400

        # Read Email Password from environment variables only
        email_password = os.environ.get('EMAIL_PASSWORD')
        if not email_password:
            return jsonify({"error": "Servidor no configurado (Falta EMAIL_PASSWORD en variables de entorno)"}), 500

        # Email Configuration
        sender_email = "bot@mandrinadosanaid.com"
        receiver_email = "info@mandrinadosanaid.com"
        smtp_server = "smtp.hostinger.com"
        smtp_port = 465

        # Create Message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"Resumen Chat con Cliente - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"

        body = f"""
        Hola,

        Un cliente ha finalizado una conversación con el Asistente Virtual.
        Aquí tienes el resumen de la charla:

        ------------------------------------------------------------
        {history}
        ------------------------------------------------------------

        Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """
        msg.attach(MIMEText(body, 'plain'))

        # Send Email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, email_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        return jsonify({"status": "success"})

    except Exception as e:
        print(f"SMTP Error: {e}")
        return jsonify({"error": f"Error al enviar correo: {str(e)}"}), 500

@app.route('/api/contact', methods=['POST'])
def contact_form():
    try:
        data = request.json
        # Validate required fields
        required_fields = ['nombre', 'empresa', 'telefono', 'email', 'averia']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Falta el campo: {field}"}), 400

        # Read Email Password
        email_password = os.environ.get('EMAIL_PASSWORD')
        if not email_password:
            return jsonify({"error": "Configuración incompleta (Falta EMAIL_PASSWORD)"}), 500

        # Email Config
        sender_email = "bot@mandrinadosanaid.com"
        receiver_email = "info@mandrinadosanaid.com"
        smtp_server = "smtp.hostinger.com"
        smtp_port = 465

        # Create Message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"🔔 Nueva Consulta Web - {data['empresa']} ({datetime.datetime.now().strftime('%d/%m')})"

        body = f"""
        NUEVA CONSULTA RECIBIDA DESDE LA WEB
        =====================================
        
        👤 DATOS DE CONTACTO:
        ---------------------
        • Nombre:   {data['nombre']}
        • Empresa:  {data['empresa']}
        • Teléfono: {data['telefono']}
        • Email:    {data['email']}
        
        📝 DETALLE DE LA AVERÍA / CONSULTA:
        -----------------------------------
        {data['averia']}
        
        =====================================
        Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """
        msg.attach(MIMEText(body, 'plain'))

        # Send Email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, email_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        return jsonify({"status": "success"})

    except Exception as e:
        print(f"Contact Form Error: {e}")
        return jsonify({"error": f"Error al enviar formulario: {str(e)}"}), 500

if __name__ == '__main__':
    # Local development
    app.run(host='0.0.0.0', port=PORT, debug=True)
