import requests
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import smtplib
from email.message import EmailMessage
import datetime
import os
import json

def buscar_empleos():
    api_key = os.environ["SERPAPI_KEY"]

    params = {
        "engine": "google",
        "q": 'empleos Córdoba Capital',
        "hl": "es",
        "gl": "ar",
        "tbs": "qdr:d",
        "api_key": api_key
    }

    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    historial = []
    if os.path.exists("historial.json"):
        with open("historial.json", "r") as f:
            historial = json.load(f)

    nuevos = []

    if "organic_results" in data:
        for result in data["organic_results"]:
            titulo = result.get("title")
            link = result.get("link")
            snippet = result.get("snippet", "")

            if link and link not in historial:
                nuevos.append((titulo, link, snippet))
                historial.append(link)

    with open("historial.json", "w") as f:
        json.dump(historial, f)

    return nuevos[:20]

def generar_pdf(ofertas):
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"empleos_{fecha}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("REPORTE DIARIO EMPLEOS CORDOBA CAPITAL", styles["Heading1"]))
    elements.append(Spacer(1, 0.5 * inch))

    for titulo, link, snippet in ofertas:
        elements.append(Paragraph(f"<b>{titulo}</b>", styles["Normal"]))
        elements.append(Paragraph(snippet, styles["Normal"]))
        elements.append(Paragraph(link, styles["Normal"]))
        elements.append(Spacer(1, 0.4 * inch))

    doc.build(elements)
    return filename

def enviar_email(pdf_path):
    EMAIL = os.environ["EMAIL_USER"]
    PASS = os.environ["EMAIL_PASS"]

    msg = EmailMessage()
    msg["Subject"] = "Reporte Diario Empleos Córdoba"
    msg["From"] = EMAIL
    msg["To"] = "rios.agus3333@gmail.com"
    msg.set_content("Adjunto reporte diario automático.")

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=pdf_path
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, PASS)
        smtp.send_message(msg)

if __name__ == "__main__":
    ofertas = buscar_empleos()

    if not ofertas:
        print("No hay empleos nuevos hoy. No se envía correo.")
    else:
        pdf = generar_pdf(ofertas)
        enviar_email(pdf)
        print("Correo enviado con nuevos empleos.")
