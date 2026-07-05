import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL


def send_digest(date: str, tech_summary: str, ai_summary: str, stock_summary: str, internship_listings: str):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("digest.html")
    html = template.render(
        date=date,
        tech_summary=tech_summary,
        ai_summary=ai_summary,
        stock_summary=stock_summary,
        internship_listings=internship_listings,
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"TechPulse — {date}"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

    print(f"[emailer] digest sent to {RECIPIENT_EMAIL}")
