import imaplib
import email
from email.header import decode_header
import time
from twilio.rest import Client
import os


# ==============================
# Load Environment Variables
# ==============================

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TARGET_SENDER = os.getenv("TARGET_SENDER")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP")
YOUR_WHATSAPP = os.getenv("YOUR_WHATSAPP")

# Validate environment variables
required_vars = [
    EMAIL_USER,
    EMAIL_PASS,
    TARGET_SENDER,
    TWILIO_SID,
    TWILIO_AUTH,
    TWILIO_WHATSAPP,
    YOUR_WHATSAPP
]

if not all(required_vars):
    raise Exception("One or more environment variables are missing!")

# ==============================

# Initialize Twilio client
client = Client(TWILIO_SID, TWILIO_AUTH)

def send_whatsapp(message):
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP,
            to=YOUR_WHATSAPP
        )
        print("WhatsApp sent:", msg.sid)
    except Exception as e:
        print("Error sending WhatsApp:", e)

def check_email():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, f'(UNSEEN FROM "{TARGET_SENDER}")')
        mail_ids = messages[0].split()

        for mail_id in mail_ids:
            status, msg_data = mail.fetch(mail_id, "(RFC822)")

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    sender = msg.get("From")

                    whatsapp_message = f"""
📧 New Email Alert!

From: {sender}
Subject: {subject}
                    """

                    send_whatsapp(whatsapp_message)

        mail.logout()

    except Exception as e:
        print("Error checking email:", e)

if __name__ == "__main__":
    print("Agent started... Monitoring emails...")
    while True:
        check_email()
        time.sleep(30)  # checks every 30 seconds