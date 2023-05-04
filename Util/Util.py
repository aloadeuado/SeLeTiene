from Configuration import *
import secrets
import bcrypt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Data.User import User
from Util.Messages import *
import jwt

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
    return SERVICE_KEY

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

def getDataJwt(token) :
    try :
        secret_key = generate_secret_key()
        decoded_jwt = jwt.decode(token, secret_key, algorithms=['HS256'])
        return decoded_jwt
    except Exception as e:
        return None

def validatorsHeaders(env, language, token, logging, url) :
    if not env:
        logging.error(f"Error: Env header is required - Request: {url}")
        return {"error": validation_messages["env_required"][language]}
    if not language:
        logging.error(f"Error: Accept-Language header is missing - Request: {url}")
        return {"error": validation_messages["missing_language_header"][language]}
    if not token:
        logging.error(f"Error: token header is missing - Request: {url}")
        return {"error": validation_messages["invalid_jwt_token"][language]}
    return None

def validateToken(env, language, token, logging, url) :

    user_dic = getDataJwt(token)
    if not user_dic :
        error_message = {"error": validation_messages["user_no_exist"][language]}
        logging.error(f"Error: User not found - Request: {url} - Response: {error_message}")
        return {"error": validation_messages["user_no_exist"][language]}
    
    try:
        # Buscar el usuario por ID
        userData = User(getEnviromentMongo(env))
        user = userData.get_user_validate_token(user_dic["id"], token)

        if user:
            return user
        else:
            # Si no se encontró el usuario, devolver un mensaje de error
            error_message = {"error": validation_messages["user_no_exist"][language]}
            logging.error(f"Error: User not found - Request: {url} - Response: {error_message}")
            return {"error": validation_messages["user_no_exist"][language]}
    except Exception as e:
        # En caso de error, devolver un mensaje de error genérico
        error_message = {"error": validation_messages["generic_error"][language]}
        logging.error(f"Error: {str(e)} - Request: {url} - Response: {error_message}")
        return {"error": validation_messages["generic_error"][language]}
    
def validateHeadersToken(request, logging) :
    language = request.headers.get('Language', 'en')
    env = request.headers.get('Env')
    token = request.headers.get('Token', '')

    if not env:
        logging.error(f"Error: Env header is required - Request: {request.url}")
        return {"error": validation_messages["env_required"][language]}
    if not language:
        logging.error(f"Error: Accept-Language header is missing - Request: {request.url}")
        return {"error": validation_messages["missing_language_header"][language]}
    if not token:
        logging.error(f"Error: token header is missing - Request: {request.url}")
        return {"error": validation_messages["invalid_jwt_token"][language]}
    


    user_dic = getDataJwt(token)
    if not user_dic :
        error_message = {"error": validation_messages["user_no_exist"][language]}
        logging.error(f"Error: User not found - Request: {request.url} - Response: {error_message}")
        return {"error": validation_messages["user_no_exist"][language]}
    
    try:
        # Buscar el usuario por ID
        userData = User(getEnviromentMongo(env))
        user = userData.get_user_validate_token(user_dic["id"], token)

        if user:
            return user
        else:
            # Si no se encontró el usuario, devolver un mensaje de error
            error_message = {"error": validation_messages["user_no_exist"][language]}
            logging.error(f"Error: User not found - Request: {url} - Response: {error_message}")
            return {"error": validation_messages["user_no_exist"][language]}
    except Exception as e:
        # En caso de error, devolver un mensaje de error genérico
        error_message = {"error": validation_messages["generic_error"][language]}
        logging.error(f"Error: {str(e)} - Request: {url} - Response: {error_message}")
        return {"error": validation_messages["generic_error"][language]}