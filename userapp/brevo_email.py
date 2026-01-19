import requests
from django.conf import settings

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

def send_email_brevo(to_email, subject, html_content,
                     sender_email="sangamithra@uniqnex360.com",
                     sender_name="uniqnex360"):
    """
    Sends an email using Brevo (Sendinblue) API.
    Requires settings.BREVO_API_KEY to be set.
    """
    payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content
    }

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json"
    }

    response = requests.post(BREVO_API_URL, json=payload, headers=headers)
    
   
 
    
    return response.status_code, response.json()
