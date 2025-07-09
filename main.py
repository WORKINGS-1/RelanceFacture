# 📁 Projet GitHub : Relance Automatique de Factures (version complète)
# --------------------------------------------------
# Ce script lit un fichier Excel avec des libellés bancaires,
# utilise GPT-4 pour retrouver le commerçant, recherche l'email de contact,
# et envoie un mail personnalisé depuis un compte Gmail.

import pandas as pd
import openai
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration de vos clés API (remplis-les dans Replit ou dans un .env local)
OPENAI_API_KEY = "TON_OPENAI_API_KEY"
SERPER_API_KEY = "TA_CLE_SERPER"
GMAIL_ADDRESS = "ton.email@gmail.com"
GMAIL_APP_PASSWORD = "ton_mot_de_passe_application"

openai.api_key = OPENAI_API_KEY

# --------- Fonction 1 : Extraction nom commerçant avec GPT-4 ---------
def extraire_commercant(libelle):
    prompt = f"""
    Tu reçois un libellé bancaire comme : {libelle}.
    Ton travail est d'en déduire le nom de l'entreprise commerçante réelle associée au paiement.
    Réponds uniquement avec le nom clair et utilisable de l'entreprise, sans autre texte.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Erreur GPT : {e}")
        return ""

# --------- Fonction 2 : Recherche email via Serper.dev ---------
def trouver_email(nom_commercant):
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": f"{nom_commercant} email contact facturation"}

    try:
        r = requests.post(url, headers=headers, json=payload)
        resultats = r.json()
        for res in resultats.get("organic", []):
            if "@" in res.get("snippet", ""):
                # Simple détection d'email dans le texte
                mots = res["snippet"].split()
                for mot in mots:
                    if "@" in mot and "." in mot:
                        return mot.strip(".,")
        return None
    except Exception as e:
        print(f"Erreur recherche email : {e}")
        return None

# --------- Fonction 3 : Envoi email ---------
def envoyer_email(destinataire, sujet, contenu):
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_ADDRESS
        msg['To'] = destinataire
        msg['Subject'] = sujet
        msg.attach(MIMEText(contenu, 'plain'))

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, destinataire, msg.as_string())
        server.quit()
        print(f"✅ Email envoyé à {destinataire}")
    except Exception as e:
        print(f"Erreur d'envoi à {destinataire} : {e}")

# --------- Fonction principale ---------
def traiter_fichier(fichier_excel):
    df = pd.read_excel(fichier_excel)
    for index, row in df.iterrows():
        libelle = str(row['Libellé'])
        montant = row['Montant']
        date = row['Date']

        print(f"\n🔍 Traitement : {libelle}")
        nom_commercant = extraire_commercant(libelle)
        print(f"🧠 Commerçant détecté : {nom_commercant}")

        email = trouver_email(nom_commercant)
        if not email:
            print("❌ Email introuvable. Ligne sautée.")
            continue

        sujet = f"Demande de facture – {nom_commercant}"
        contenu = f"""
Bonjour,

Merci de m’envoyer la facture correspondant au paiement de {montant} effectué le {date}.
(Libellé bancaire : {libelle})

Cordialement,
{GMAIL_ADDRESS}
        """
        envoyer_email(email, sujet, contenu)

# --------- Exécution ---------
if __name__ == "__main__":
    traiter_fichier("transactions.xlsx")
