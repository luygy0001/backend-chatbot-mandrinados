import smtplib
from email.mime.text import MIMEText
import getpass

def test_smtp():
    print("=== PRUEBA DE ENVÍO DE CORREO (HOSTINGER) ===")
    print("Esta prueba conecta directamente con Hostinger para verificar tu contraseña.")
    
    sender_email = "bot@mandrinadosanaid.com"
    receiver_email = "info@mandrinadosanaid.com"
    smtp_server = "smtp.hostinger.com"
    smtp_port = 465

    print(f"\n📧 De: {sender_email}")
    print(f"📧 A:  {receiver_email}")
    
    # Securely ask for password
    password = getpass.getpass(f"🔑 Introduce la contraseña de {sender_email}: ")

    if not password:
        print("❌ Error: No has introducido ninguna contraseña.")
        return

    try:
        print("\n⏳ Conectando con smtp.hostinger.com...")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        
        print("🔐 Iniciando sesión...")
        server.login(sender_email, password)
        print("✅ ¡Login CORRECTO! La contraseña es válida.")

        # Prepare message
        msg = MIMEText("Si lees esto, el BOT funciona y la contraseña es correcta.")
        msg["Subject"] = "PRUEBA DE CONEXIÓN - HOSTINGER"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        print("📤 Enviando correo de prueba...")
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        
        print("\n✅✅✅ CORREO ENVIADO CON ÉXITO.")
        print("Revisa ahora mismo la bandeja de entrada de info@mandrinadosanaid.com (Mira también en SPAM).")

    except smtplib.SMTPAuthenticationError:
        print("\n❌ ERROR DE AUTENTICACIÓN (535).")
        print("La contraseña que has puesto NO es correcta para bot@mandrinadosanaid.com.")
        print("Por favor, entra en Hostinger y cámbiala de nuevo.")

    except Exception as e:
        print(f"\n❌ ERROR TÉCNICO: {e}")

if __name__ == "__main__":
    test_smtp()
    input("\nPulsa ENTER para cerrar...")
