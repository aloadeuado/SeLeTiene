import jwt as jwt
import datetime
from flask import request, jsonify
from app import app
from Configuration import *
from Util import *
from Validators import *
from Messages import *
from User import *
import logging
import bcrypt

## Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/api/registro', methods=['POST'])
def registro():
    language = request.headers.get('Language', 'en')
    env = request.headers.get('Env')

    if not env:
        return jsonify({"message": validation_messages["env_required"][language]}), 400

    name = request.json.get('name', '').strip()
    mobilePhone = request.json.get('mobilePhone', '').strip()
    email = request.json.get('email', '').strip()
    password = request.json.get('password', '').strip()
    accessToken = request.json.get('accessToken', '').strip()
    appleId = request.json.get('appleId', '').strip()

    if not name or not mobilePhone or not email:
        return jsonify({"message": validation_messages["missing_required_fields"][language]}), 400

    if not validar_email(email):
        return jsonify({"message": validation_messages["invalid_email_format"][language]}), 400

    user = User(getEnviromentMongo(env))

    # Validar que el correo electrónico y el teléfono móvil no estén duplicados
    existing_user_email = user.find_by_email(email)
    existing_user_mobile = user.find_by_mobile_phone(mobilePhone)

    if existing_user_email:
        return jsonify({"message": validation_messages["email_already_registered"][language]}), 400
    if existing_user_mobile:
        return jsonify({"message": validation_messages["mobile_already_registered"][language]}), 400

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    user_data = {
        'name': name,
        'mobilePhone': mobilePhone,
        'email': email,
        'password': hashed_password,
        'accessToken': accessToken,
        'appleId': appleId,
        'dateRegister': datetime.datetime.utcnow(),
        'isActive': True,
        'isEmailVerified': False,
        'isMobilePhoneVerified': False,
    }

    user.create(user_data)
    logging.info(f'Nuevo usuario registrado: {user_data}')

    # Crear token JWT
    jwt_payload = {
        'id': str(user_data["_id"]),
        'email': email,
        'name': name,
        "mobilePhone": mobilePhone,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }

    jwt_secret = generate_secret_key()

    try:
        token = jwt.encode(jwt_payload, jwt_secret, algorithm='HS256')
    except Exception as e:
        app.logger.error(f'Error creating JWT token: {e}')
        return jsonify({'error': validation_messages['jwt_creation_error'][language]}), 500
    

    try:
        user.updateJwt(token, user_data["_id"])
        token = jwt.encode(jwt_payload, jwt_secret, algorithm='HS256')
    except Exception as e:
        app.logger.error(f'Error creating JWT token: {e}')
        return jsonify({'message': validation_messages['jwt_creation_error'][language]}), 401
    
    user_dataResponse = user_data
    user_dataResponse["id"] = str(user_data["_id"])
    del user_dataResponse["_id"]
    del user_dataResponse["password"]
    del user_dataResponse["accessToken"]
    del user_dataResponse["appleId"]
    del user_dataResponse["dateRegister"]
    del user_dataResponse["isActive"]
    del user_dataResponse["isEmailVerified"]
    del user_dataResponse["isMobilePhoneVerified"]

    response_data = {
        'token': token,
        'data': user_dataResponse
    }
    logging.info(f'Response: {response_data}')

    return jsonify(response_data), 201

@app.route('/api/login', methods=['POST'])
def loginAuth():
    language = request.headers.get('Accept-Language', 'en')
    env = request.headers.get('Env')

    if not env:
        return jsonify({'message': validation_messages['missing_env_header'][language]}), 400

    email = request.json.get('email', '').strip()
    password = request.json.get('password', '').strip()

    if not email or not password:
        return jsonify({'message': validation_messages['required_fields'][language]}), 400

    user = User(getEnviromentMongo(env))
    existing_user = user.find_by_email(email)

    if not existing_user or not check_password(existing_user["password"], password):
        return jsonify({'message': validation_messages['invalid_credentials'][language]}), 401

    onjectId = existing_user["_id"]
    user_data = {
        'id': str(onjectId),
        'email': existing_user["email"],
        'name': existing_user["name"],
        'mobilePhone': existing_user["mobilePhone"],
    }

    jwt_secret = generate_secret_key()
    jwt_payload = {
        'id': user_data['id'],
        'email': user_data['email'],
        'name': user_data['name'],
        'mobilePhone': user_data['mobilePhone'],
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }

    try:
        token = jwt.encode(jwt_payload, jwt_secret, algorithm='HS256')
    except Exception as e:
        app.logger.error(f'Error creating JWT token: {e}')
        return jsonify({'message': validation_messages['jwt_creation_error'][language]}), 501
    
    try:
        user = User(getEnviromentMongo(env))
        user.updateJwt(token, onjectId)
        token = jwt.encode(jwt_payload, jwt_secret, algorithm='HS256')
    except Exception as e:
        app.logger.error(f'Error creating JWT token: {e}')
        return jsonify({'message': validation_messages['jwt_creation_error'][language]}), 401
    
    response_data = {
        'token': token,
        'data': user_data
    }

    logging.info(f'Response: {response_data}')
    return jsonify(response_data), 200