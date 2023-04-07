import jwt as jwt
import datetime
from flask import request, jsonify
from app import app
from bson import ObjectId
from Configuration import *
from Util import *
from Validators import *
from Messages import *
from User import *
import logging
import bcrypt

## Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/api/tempRegisterGoogle', methods=['POST'])
def tempRegisterGoogle():
    language = request.headers.get('Language', 'en')
    env = request.headers.get('Env')

    if not env:
        return jsonify({"error": validation_messages["env_required"][language]}), 400
    if not language:
        return jsonify({"error": validation_messages["missing_language_header"][language]}), 400

    name = request.json.get('name', '').strip()
    email = request.json.get('email', '').strip()
    googleId = request.json.get('googleId', '').strip()

    if not googleId:
        return jsonify({"error": validation_messages["missing_required_fields"][language]}), 400

    user = User(getEnviromentMongo(env))

    existing_user = user.find_by_accessToken(googleId)

    if existing_user:
        user_dataResponse = existing_user
        user_dataResponse["id"] = str(existing_user["_id"])
        user_send = {
            "name": user_dataResponse["name"],
            "email": user_dataResponse["email"],
            "id": user_dataResponse["id"],
            "mobilePhone": user_dataResponse["mobilePhone"],
            "googleId": user_dataResponse["googleId"],
        }

        logging.info(f'Response: {user_dataResponse}')
        return jsonify(user_send), 200

    existing_email_user = user.find_by_email(email)

    if existing_email_user:
        user_data = {
            'googleId': googleId,
        }
        user.update(existing_email_user["_id"], user_data)
        user_dataResponse = existing_email_user
        user_dataResponse["id"] = str(existing_email_user["_id"])
        user_send = {
            "name": user_dataResponse["name"],
            "email": user_dataResponse["email"],
            "id": user_dataResponse["id"],
            "mobilePhone": user_dataResponse["mobilePhone"],
            "googleId": user_dataResponse["googleId"],
        }

        logging.info(f'Response: {user_send}')
        return jsonify(user_send), 200

    user_data = {
        'name': name,
        'email': email,
        'password': "",
        'appleId': "",
        'dateRegister': datetime.datetime.utcnow(),
        'mobilePhone': "",
        'isActive': False,
        'isEmailVerified': False,
        'isMobilePhoneVerified': False,
        "isRegister": False,
        "jwtKey": "",
        "googleId": googleId
    }

    user.create(user_data)
    logging.info(f'Nuevo usuario registrado: {user_data}')
    user_dataResponse = user_data
    user_dataResponse["id"] = str(user_data["_id"])
    user_send = {
            "name": user_dataResponse["name"],
            "email": user_dataResponse["email"],
            "id": user_dataResponse["id"],
            "mobilePhone": user_dataResponse["mobilePhone"],
            "googleId": user_dataResponse["googleId"],
        }

    logging.info(f'Response: {user_send}')
    return jsonify(user_send), 200



@app.route('/api/tempRegisterApleId', methods=['POST'])
def temp_register():
    language = request.headers.get('Language', 'en')
    env = request.headers.get('Env')

    if not env:
        return jsonify({"error": validation_messages["env_required"][language]}), 400
    if not language:
        return jsonify({"error": validation_messages["missing_language_header"][language]}), 400

    name = request.json.get('name', '').strip()
    email = request.json.get('email', '').strip()
    apple_id = request.json.get('appleId', '').strip()

    if not apple_id:
        return jsonify({"error": validation_messages["missing_required_fields"][language]}), 400

    user = User(getEnviromentMongo(env))

    existing_user = user.find_by_apple_id(apple_id)

    if existing_user:
        user_dataResponse = existing_user
        user_dataResponse["id"] = str(existing_user["_id"])
        user_send = {
            "name": user_dataResponse["name"],
            "email": user_dataResponse["email"],
            "id": user_dataResponse["id"],
            "mobilePhone": user_dataResponse["mobilePhone"],
            "appleId": user_dataResponse["appleId"],
        }

        logging.info(f'Response: {user_dataResponse}')
        return jsonify(user_send), 200

    existing_email_user = user.find_by_email(email)

    if existing_email_user:
        user_data = {
            'appleId': apple_id,
        }
        user.update(existing_email_user["_id"], user_data)
        user_dataResponse = existing_email_user
        user_dataResponse["id"] = str(existing_email_user["_id"])
        user_send = {
            "name": user_dataResponse["name"],
            "email": user_dataResponse["email"],
            "id": user_dataResponse["id"],
            "mobilePhone": user_dataResponse["mobilePhone"],
            "appleId": user_dataResponse["appleId"],
        }
        logging.info(f'Response: {user_dataResponse}')
        return jsonify(user_send), 200

    user_data = {
        'name': name,
        'email': email,
        'password': "",
        'appleId': apple_id,
        'dateRegister': datetime.datetime.utcnow(),
        'isActive': False,
        'mobilePhone': "",
        'isEmailVerified': False,
        'isMobilePhoneVerified': False,
        "isRegister": False,
        "jwtKey": "",
        "googleId": ""
    }

    user.create(user_data)
    logging.info(f'Nuevo usuario registrado: {user_data}')
    user_dataResponse = user_data
    user_dataResponse["id"] = str(user_data["_id"])
    user_send = {
            "name": user_dataResponse["name"],
            "email": user_dataResponse["email"],
            "id": user_dataResponse["id"],
            "mobilePhone": user_dataResponse["mobilePhone"],
            "appleId": user_dataResponse["appleId"],
        }
    logging.info(f'Response: {user_dataResponse}')
    return jsonify(user_send), 200


@app.route('/api/registro', methods=['POST'])
def registro():
    language = request.headers.get('Language', 'en')
    env = request.headers.get('Env')

    if not env:
        return jsonify({"error": validation_messages["env_required"][language]}), 400

    name = request.json.get('name', '').strip()
    mobilePhone = request.json.get('mobilePhone', '').strip()
    email = request.json.get('email', '').strip()
    password = request.json.get('password', '').strip()
    googleId = request.json.get('googleId', '').strip()
    appleId = request.json.get('appleId', '').strip()

    if not name or not mobilePhone or not email or not password:
        return jsonify({"error": validation_messages["missing_required_fields"][language]}), 400

    if not validar_email(email):
        return jsonify({"error": validation_messages["invalid_email_format"][language]}), 400

    user = User(getEnviromentMongo(env))

    # Validar que el correo electrónico y el teléfono móvil no estén duplicados
    existing_user_email = user.find_by_email(email)
    existing_user_mobile = user.find_by_mobile_phone(mobilePhone)

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user_read = {}
    if existing_user_email:
        user_read = existing_user_email
        if existing_user_email.get("isRegister", True) or existing_user_email.get("isActive", True):
            return jsonify({"error": validation_messages["email_already_registered"][language]}), 400
        
    if existing_user_mobile:
        user_read = existing_user_mobile
        if existing_user_mobile.get("isRegister", True) or existing_user_mobile.get("isActive", True):
            return jsonify({"error": validation_messages["mobile_already_registered"][language]}), 400
    

    user_send = {}
    objectId = ObjectId()
    if googleId != "" and existing_user_email:
        try:
            user.update(existing_user_email["_id"], {"googleId": googleId, "isRegister": True, "isActive": True, "name": name, "mobilePhone": mobilePhone, "password": hashed_password })
        except Exception as e:
            app.logger.error(f'Error creating JWT token: {e}')
            return jsonify({'error': validation_messages['invalid_access_token'][language]}), 401
        
        objectId = user_read["_id"]
        user_send["id"] = str(user_read["_id"])
        user_send["name"] = name
        user_send["email"] = str(user_read["email"])
        user_send["mobilePhone"] = mobilePhone

    elif appleId != "" and existing_user_mobile:
        try:
            user.update(existing_user_email["_id"], {"appleId": appleId, "isRegister": True, "isActive": True, "name": name, "mobilePhone": mobilePhone, "password": hashed_password })
        except Exception as e:
            app.logger.error(f'Error creating JWT token: {e}')
            return jsonify({'error': validation_messages['invalid_apple_id'][language]}), 401
        
        objectId = user_read["_id"]
        user_send["id"] = str(user_read["_id"])
        user_send["name"] = name
        user_send["email"] = str(user_read["email"])
        user_send["mobilePhone"] = mobilePhone

    elif not existing_user_mobile and not existing_user_email:
        user_data = {
        'name': name,
        'mobilePhone': mobilePhone,
        'email': email,
        'password': hashed_password,
        'googleId': googleId,
        'appleId': appleId,
        'dateRegister': datetime.datetime.utcnow(),
        'isActive': True,
        'isRegister': True,
        'isEmailVerified': False,
        'isMobilePhoneVerified': False,
        }

        user.create(user_data)

        objectId = user_data["_id"]
        user_send["id"] = str(user_data["_id"])
        user_send["name"] = str(user_data["name"])
        user_send["email"] = str(user_data["email"])
        user_send["mobilePhone"] = str(user_data["mobilePhone"])

        logging.info(f'Nuevo usuario registrado: {user_data}')
    else :
        app.logger.error(validation_messages['missing_social_id'][language])
        return jsonify({'error': validation_messages['missing_social_id'][language]}), 401
    # Crear token JWT
    jwt_payload = {
        'id': user_send["id"],
        'email': user_send["email"],
        'name': user_send["name"],
        "mobilePhone": user_send["mobilePhone"],
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }

    jwt_secret = generate_secret_key()

    try:
        token = jwt.encode(jwt_payload, jwt_secret, algorithm='HS256')
        user.updateJwt(token, objectId)
    except Exception as e:
        app.logger.error(f'Error creating JWT token: {e}')
        return jsonify({'error': validation_messages['jwt_creation_error'][language]}), 401
    

    response_data = {
        'token': token,
        'data': user_send
    }
    logging.info(f'Response: {response_data}')

    return jsonify(response_data), 200

@app.route('/api/login', methods=['POST'])
def loginAuth():
    language = request.headers.get('Accept-Language', 'en')
    env = request.headers.get('Env')

    if not env:
        return jsonify({'error': validation_messages['missing_env_header'][language]}), 400

    email = request.json.get('email', '').strip()
    password = request.json.get('password', '').strip()

    if not email or not password:
        return jsonify({'error': validation_messages['required_fields'][language]}), 400

    user = User(getEnviromentMongo(env))
    existing_user = user.find_by_email(email)

    if not existing_user or not check_password(existing_user["password"], password):
        return jsonify({'error': validation_messages['invalid_credentials'][language]}), 401

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
        return jsonify({'error': validation_messages['jwt_creation_error'][language]}), 501
    
    try:
        user = User(getEnviromentMongo(env))
        user.updateJwt(token, onjectId)
        token = jwt.encode(jwt_payload, jwt_secret, algorithm='HS256')
    except Exception as e:
        app.logger.error(f'Error creating JWT token: {e}')
        return jsonify({'error': validation_messages['jwt_creation_error'][language]}), 401
    
    response_data = {
        'token': token,
        'data': user_data
    }

    logging.info(f'Response: {response_data}')
    return jsonify(response_data), 200

@app.route('/api/loginApple', methods=['POST'])
def loginApple():
    language = request.headers.get('Accept-Language', 'en')
    env = request.headers.get('Env')

    if not env:
        return jsonify({'error': validation_messages['missing_env_header'][language]}), 400

    email = request.json.get('email', '').strip()
    appleId = request.json.get('appleId', '').strip()

    if not email or not appleId:
        return jsonify({'error': validation_messages['required_fields'][language]}), 400

    user = User(getEnviromentMongo(env))
    existing_user = user.find_by_apple_id(appleId)

    if not existing_user :
        return jsonify({'error': validation_messages['invalid_apple_id'][language]}), 401

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
        return jsonify({'error': validation_messages['jwt_creation_error'][language]}), 501
    
    try:
        user = User(getEnviromentMongo(env))
        user.updateJwt(token, onjectId)
        token = jwt.encode(jwt_payload, jwt_secret, algorithm='HS256')
    except Exception as e:
        app.logger.error(f'Error creating JWT token: {e}')
        return jsonify({'error': validation_messages['jwt_creation_error'][language]}), 401
    
    response_data = {
        'token': token,
        'data': user_data
    }

    logging.info(f'Response: {response_data}')
    return jsonify(response_data), 200


@app.route('/api/loginGoogle', methods=['POST'])
def loginGoogle():
    language = request.headers.get('Accept-Language', 'en')
    env = request.headers.get('Env')

    if not env:
        return jsonify({'error': validation_messages['missing_env_header'][language]}), 400

    googleId = request.json.get('googleId', '').strip()

    if not googleId:
        return jsonify({'error': validation_messages['required_fields'][language]}), 400

    user = User(getEnviromentMongo(env))
    existing_user = user.find_by_accessToken(googleId)

    if not existing_user :
        return jsonify({'error': validation_messages['invalid_access_token'][language]}), 401

    if not existing_user.get("isRegister", False) :
        return jsonify({'error': validation_messages['invalid_access_token'][language]}), 401
    
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
        user = User(getEnviromentMongo(env))
        user.updateJwt(token, onjectId)
    except Exception as e:
        app.logger.error(f'Error creating JWT token: {e}')
        return jsonify({'error': validation_messages['jwt_creation_error'][language]}), 401
    
    response_data = {
        'token': token,
        'data': user_data
    }

    logging.info(f'Response: {response_data}')
    return jsonify(response_data), 200