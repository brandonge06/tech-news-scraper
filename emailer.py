import resend
from jinja2 import Environment, FileSystemLoader
from config import RESEND_API_KEY, FROM_EMAIL, RECIPIENT_EMAIL

resend.api_key = RESEND_API_KEY


def send_digest(date, tech_summary, ai_summary, stock_summary, internship_listings,
                tech_sources="", ai_sources="", stock_links=""):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("digest.html")
    html = template.render(
        date=date,
        tech_summary=tech_summary,
        ai_summary=ai_summary,
        stock_summary=stock_summary,
        internship_listings=internship_listings,
        tech_sources=tech_sources,
        ai_sources=ai_sources,
        stock_links=stock_links,
    )

    response = resend.Emails.send({
        "from": FROM_EMAIL,
        "to": RECIPIENT_EMAIL,
        "subject": f"TechPulse — {date}",
        "html": html,
    })

    print(f"[emailer] digest sent to {RECIPIENT_EMAIL} (id: {response.get('id')})")
