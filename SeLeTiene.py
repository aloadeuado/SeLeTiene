import jwt
import datetime
from flask import request, jsonify
from app import app
from Configuration import *
from Util import *
from Validators import *
from Messages import *
from User import *
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route("/lologramos", methods=["GET"])
def lologramos():
    return jsonify({"test": "complete"})

@app.route('/api/registro', methods=['POST'])
def registro():
    data = request.get_json()
    logging.info(f"Inicio de la función registro con data: {data}")
    lang = request.headers.get('Accept-Language')
    env = request.headers.get('Env')

    if lang is None:
        logging.warning('Cabecera Accept-Language vacía')
        return jsonify({"error": validation_messages['missing_language_header'].get('en')}), 400

    if env is None:
        logging.warning('Cabecera Env vacía')
        return jsonify({"error": validation_messages['missing_env_header'].get(lang, validation_messages['missing_env_header']['en'])}), 400

    name = data.get('name', '').strip()
    mobilePhone = data.get('mobilePhone', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    accessToken = data.get('accessToken', '')
    appleId = data.get('appleId', '')

    if not (name and mobilePhone and email):
        logging.warning('Campos requeridos vacíos')
        return jsonify({"error": validation_messages['required_fields'].get(lang, validation_messages['required_fields']['en'])}), 400

    if not validar_email(email):
        logging.warning('Formato de email incorrecto')
        return jsonify({"error": validation_messages['email_format'].get(lang, validation_messages['email_format']['en'])}), 400

    user_data = {
        'name': name,
        'mobilePhone': mobilePhone,
        'email': email,
        'password': password,
        'accessToken': accessToken,
        'appleId': appleId,
        'dateRegister': datetime.datetime.utcnow(),  # Agrega el campo dateRegister
        'isActive': True
    }

    user = User(getEnviromentMongo(env))
    user_id = user.create(user_data)
    user_data['_id'] = str(user_id)

    # Generar JWT
    jwt_secret = 'your_jwt_secret'  # Reemplaza esto con tu propia clave secreta para JWT
    payload = {
        'user_data': user_data,
        'registered_at': str(datetime.datetime.utcnow())
    }
    token = jwt.encode(payload, jwt_secret, algorithm='HS256')

    response_data = {
        "message": validation_messages['user_registered'].get(lang, validation_messages['user_registered']['en']),
        "token": token,
        "data": user_data
    }
    logging.info(f"Fin de la función registro con respuesta: {response_data}")

    return jsonify(response_data), 201