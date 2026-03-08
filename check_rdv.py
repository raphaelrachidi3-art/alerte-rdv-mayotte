import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# === CONFIGURATION ===
RECIPIENT_EMAIL = "raphaelrachidi3@gmail.com"
SENDER_EMAIL = os.environ.get("GMAIL_ADDRESS")
SENDER_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

# URL officielle RDV préfecture Mayotte - renouvellement titre de séjour
URL = "https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/6860/creneau/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

# Mots qui indiquent qu'il N'Y A PAS de créneau
NO_SLOT_KEYWORDS = [
    "aucun créneau",
    "aucune disponibilité",
    "pas de créneau",
    "no slot",
    "complet",
    "indisponible",
    "aucun rendez-vous disponible",
]

def send_alert_email(page_content_preview):
    """Envoie un email d'alerte quand un créneau est détecté."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🚨 CRÉNEAU DISPONIBLE - Préfecture de Mayotte !"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    now = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
      <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        
        <div style="background: #0a3d62; padding: 30px; text-align: center;">
          <h1 style="color: white; margin: 0; font-size: 24px;">🚨 CRÉNEAU DISPONIBLE !</h1>
          <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0;">Préfecture de Mayotte — Titre de séjour</p>
        </div>

        <div style="padding: 30px;">
          <p style="font-size: 16px; color: #333;">Un créneau de rendez-vous vient d'être détecté le <strong>{now}</strong>.</p>
          
          <div style="background: #fff3cd; border-left: 4px solid #f39c12; padding: 15px; border-radius: 6px; margin: 20px 0;">
            ⚡ <strong>Faites vite !</strong> Les créneaux partent en quelques secondes.
          </div>

          <a href="{URL}" style="display: block; background: #e84855; color: white; text-align: center; padding: 18px; border-radius: 10px; text-decoration: none; font-size: 18px; font-weight: bold; margin: 20px 0;">
            👉 RÉSERVER MON CRÉNEAU MAINTENANT
          </a>

          <p style="font-size: 13px; color: #999; text-align: center;">
            Détecté automatiquement par votre alerte RDV Préfecture de Mayotte
          </p>
        </div>
      </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    
    print(f"✅ Email d'alerte envoyé à {RECIPIENT_EMAIL} !")

def check_availability():
    """Vérifie si un créneau est disponible sur le site de la préfecture."""
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        content = response.text.lower()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Vérification... Status: {response.status_code}")

        # Si un des mots "pas de créneau" est trouvé → pas de dispo
        for keyword in NO_SLOT_KEYWORDS:
            if keyword in content:
                print(f"❌ Pas de créneau disponible (détecté: '{keyword}')")
                return False

        # Si la page contient des éléments de sélection de créneau → dispo !
        slot_indicators = ["créneau", "choisir", "disponible", "réserver", "matin", "après-midi", "08:", "09:", "10:", "11:", "14:", "15:", "16:"]
        found = [kw for kw in slot_indicators if kw in content]
        
        if found:
            print(f"✅ CRÉNEAU POTENTIELLEMENT DISPONIBLE ! (indicateurs: {found})")
            return True
        
        print("⚠️ Page ambiguë, envoi d'alerte par précaution")
        return True

    except requests.RequestException as e:
        print(f"⚠️ Erreur réseau: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Vérification des créneaux - Préfecture de Mayotte")
    
    if check_availability():
        print("📧 Envoi de l'email d'alerte...")
        send_alert_email("")
    else:
        print("😴 Aucun créneau pour l'instant. Prochaine vérification dans 1 minute.")
