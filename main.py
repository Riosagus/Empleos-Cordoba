# Empleos-Cordoba
import requests
from bs4 import BeautifulSoup
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import smtplib
from email.message import EmailMessage
import datetime
import os

def buscar_empleos():
    query = "empleos Córdoba Capital site:ar"
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    resultados = []

    for g in soup.find_all("div", class_="g"):
        titulo = g.find("h3")
        link = g.find("a")
        if titulo and link:
            resultados.append((titulo.text, link["href"]))

    return resultados

def generar_pdf(ofertas):
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"empleos_{fecha}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("REPORTE DIARIO EMPLEOS CORDOBA CAPITAL", styles["Heading1"]))
    elements.append(Spacer(1, 0.5 * inch))

    for titulo, link in ofertas:
        elements.append(Paragraph(f"<b>{titulo}</b>", styles["Normal"]))
        elements.append(Paragraph(link, styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))

    doc.build(elements)
    return filename

def enviar_email(pdf_path):
    try:
        EMAIL = os.environ["EMAIL_USER"]
        PASS = os.environ["EMAIL_PASS"]

        msg = EmailMessage()
        msg["Subject"] = "Reporte Diario Empleos Córdoba"
        msg["From"] = EMAIL
        msg["To"] = "ríos.agus3333@gmail.com"
        msg.set_content("Adjunto reporte diario automático.")

        with open(pdf_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=pdf_path)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL, PASS)
            smtp.send_message(msg)

        print("EMAIL ENVIADO CORRECTAMENTE")

    except Exception as e:
        print("ERROR AL ENVIAR EMAIL:")
        print(e)
        raise e

if __name__ == "__main__":
    ofertas = buscar_empleos()
    pdf = generar_pdf(ofertas)
    enviar_email(pdf)
