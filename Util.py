from Configuration import *
import secrets
import bcrypt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

dbQa = client.get_database("SeLeTieneQa")
dbPrd = client.get_database("SeLeTiene")

def saveEnviromentMongo(data, env):
    if env == environment["qa"]:
        dbQa.insert_one(data)
    elif env == environment["prd"]:
        dbPrd.insert_one(data)
    else:
        dbQa.insert_one(data)
        dbPrd.insert_one(data)

def getEnviromentMongo(env):
    if env == environment["qa"]:
        return dbQa
    elif env == environment["prd"]:
        return dbPrd
    else:
        raise ValueError("Invalid environment")
    
def generate_secret_key():
    return secrets.token_hex(32)

def check_password(hashed_password, password):
    password_bytes = password.encode('utf-8') if isinstance(password, str) else str(password).encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def sendEmail(subject, body, toEmail) :
    # Configuración del servidor SMTP de Gmail
    smtp_host = SMTP_HOST
    smtp_port = SMPT_PORT
    sender_email = SENDER_EMAIL
    sender_password = SENDER_PASSWORD
    
    # Creación del mensaje de correo electrónico
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = toEmail
    message['Subject'] = subject
    confirmation_text = body
    message.attach(MIMEText(confirmation_text, 'plain'))
    
    # Envío del correo electrónico
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, toEmail, message.as_string())
