import jwt as jwt
import datetime
from flask import request, jsonify
from app import app
from bson import ObjectId
from Configuration import *
from Util.Util import *
from Util.Validators import *
from Util.Messages import *
from Data.User import *
import logging
import bcrypt
import random

## Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@app.route('/api/getUser', methods=['GET'])
def get_user():
    
    language = request.headers.get('Language', 'en')
    env = request.headers.get('Env')
    token = request.headers.get('Token', '')

    if not env:
        logging.error(f"Error: Env header is required - Request: {request.url}")
        return jsonify({"error": validation_messages["env_required"][language]}), 400
    if not language:
        logging.error(f"Error: Accept-Language header is missing - Request: {request.url}")
        return jsonify({"error": validation_messages["missing_language_header"][language]}), 400
    if not token:
        logging.error(f"Error: token header is missing - Request: {request.url}")
        return jsonify({"error": validation_messages["invalid_jwt_token"][language]}), 400
    # Validar que el ID no esté vacío
    if not id:
        error_message = {"error": validation_messages["missing_id"][language]}
        logging.error(f"Error: ID cannot be empty - Request: {request.url} - Response: {error_message}")
        return jsonify(error_message), 400

    user_dic = getDataJwt(token)
    if not user_dic :
        error_message = {"error": validation_messages["user_no_exist"][language]}
        logging.error(f"Error: User not found - Request: {request.url} - Response: {error_message}")
        return jsonify(error_message), 401
    
    try:
        # Buscar el usuario por ID
        userData = User(getEnviromentMongo(env))
        user = userData.get_user_validate_token(user_dic["id"], token)

        if user:
            # Si se encontró el usuario, devolver sus datos
            response = {
                "id": str(user["_id"]),
                "name": user["name"],
                "mobilePhone": user["mobilePhone"],
                "email": user["email"],
                "isEmailVerified": user["isEmailVerified"]
            }
            logging.info(f"Success - Request: {request.url} - Response: {response}")
            return jsonify(response), 200
        else:
            # Si no se encontró el usuario, devolver un mensaje de error
            error_message = {"error": validation_messages["user_no_exist"][language]}
            logging.error(f"Error: User not found - Request: {request.url} - Response: {error_message}")
            return jsonify(error_message), 401
    except Exception as e:
        # En caso de error, devolver un mensaje de error genérico
        error_message = {"error": validation_messages["generic_error"][language]}
        logging.error(f"Error: {str(e)} - Request: {request.url} - Response: {error_message}")
        return jsonify(error_message), 400



@app.route('/api/verificationCodeEmailChangePassword', methods=['POST'])
def verificationCodeEmailChangePassword():
    language = request.headers.get('Language', 'en')
    env = request.headers.get('Env')

    if not env:
        return jsonify({"error": validation_messages["env_required"][language]}), 400
    if not language:
        return jsonify({"error": validation_messages["missing_language_header"][language]}), 400
    
    code = request.json.get("code", "")
    password = request.json.get("password", "")
    email = request.json.get("email", "")

    if not code:
        return jsonify({"error": validation_messages["missing_code"][language]}), 400
    if not email:
        return jsonify({"error": validation_messages["required_fields_email"][language]}), 400
    if not password:
        return jsonify({"error": validation_messages["missing_password"][language]}), 400
    
    user = User(getEnviromentMongo(env))
    existing_email = user.find_by_email(email)
    if not existing_email :
        return jsonify({'error': validation_messages['user_no_exist'][language]}), 400
    if existing_email["resetPasswordCodeEmil"] != code :
        return jsonify({'error': validation_messages['verification_failed'][language]}), 400
    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user.update(str(existing_email["_id"]), {"resetPasswordCodeEmil": "", "password": hashed_password})

    return {"message": validation_messages["password_updated"][language]}, 200


@app.route('/api/sendCodeEmailChangePassword', methods=['POST'])
def sendCodeEmailChangePassword():
    language = request.headers.get('Language', 'en')
    env = request.headers.get('Env')


    if not env:
        return jsonify({"error": validation_messages["env_required"][language]}), 400
    if not language:
        return jsonify({"error": validation_messages["missing_language_header"][language]}), 400
    
    email = request.json.get("email", "")
    if not email:
        return jsonify({"error": validation_messages["required_fields_email"][language]}), 400
    
    user = User(getEnviromentMongo(env))
    existing_email = user.find_by_email(email)
    if not existing_email :
        return jsonify({'error': validation_messages['user_no_exist'][language]}), 400
    
    code = random.randint(10000, 99999)
    user.update(str(existing_email["_id"]), {"resetPasswordCodeEmil": f"{code}"})
    sendEmail(validation_messages['reset_code'][language].replace("{code}", f"{code}"), validation_messages['reset_code_instructions'][language].replace("{code}", f"{code}"), existing_email["email"])
    return {"message": validation_messages["send_email_full"][language]}, 200

@app.route('/api/sendEmailVerification/<id>', methods=['GET'])
def sendEmailVerification(id):
    language = request.headers.get('Language', 'en')
    env = request.headers.get('Env')

    if not env:
        return jsonify({"error": validation_messages["env_required"][language]}), 400
    if not language:
        return jsonify({"error": validation_messages["missing_language_header"][language]}), 400

    if not id:
        return jsonify({"error": validation_messages["missing_id"][language]}), 400
    
    user = User(getEnviromentMongo(env))
    existing_email = user.find_by_id(id)
    if not existing_email :
        return jsonify({'error': validation_messages['user_no_exist'][language]}), 400
    
    code = random.randint(10000, 99999)
    user.update(id, {"verificationCodeEmil": f"{code}"})
    sendEmail(validation_messages['verification_code_send'][language], validation_messages['code_generated'][language].replace("{code}", f"{code}"), existing_email["email"])
    return {"message": validation_messages["send_email_full"][language]}, 200


@app.route('/api/verifiedEmailVerification/<id>/<code>', methods=['GET'])
def verifiedEmailVerification(id, code):
    language = request.headers.get('Language', 'en')
    env = request.headers.get('Env')

    if not env:
        return jsonify({"error": validation_messages["env_required"][language]}), 400
    if not language:
        return jsonify({"error": validation_messages["missing_language_header"][language]}), 400

    if not code:
        return jsonify({"error": validation_messages["missing_code"][language]}), 400
    
    if not id:
        return jsonify({"error": validation_messages["missing_id"][language]}), 400
    
    user = User(getEnviromentMongo(env))
    existing_email = user.find_by_id(id)
    if not existing_email :
        return jsonify({'error': validation_messages['user_no_exist'][language]}), 400
    
    if existing_email["verificationCodeEmil"] != code :
        return jsonify({'error': validation_messages['verification_failed'][language]}), 400
    
    user.update(id, {"isEmailVerified": True})
    code = random.randint(10000, 99999)
    user.update(id, {"verificationCodeEmil": ""})

    return {"message": validation_messages["email_verified"][language]}, 200

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
        user.updateJwt(f"{token}", objectId)
    except Exception as e:
        app.logger.error(f'Error creating JWT token: {e}')
        return jsonify({'error': validation_messages['jwt_creation_error'][language]}), 401
    

    response_data = {
        'token': f"{token}",
        'data': user_send
    }
    logging.info(f'Response: {response_data}')

    try :
        code = random.randint(10000, 99999)
        user.update(id, {"verificationCodeEmil": f"{code}"})
        sendEmail(validation_messages['verification_code_send'][language], validation_messages['code_generated'][language].replace("{code}", f"{code}"), user_send["email"])
    except Exception as e :    
        app.logger.error(f'Error creating JWT token: {e}')

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
        user = User(getEnviromentMongo(env))
        user.updateJwt(f"{token}", onjectId)
    except Exception as e:
        app.logger.error(f'Error creating JWT token: {e}')
        return jsonify({'error': validation_messages['jwt_creation_error'][language]}), 501
    
    response_data = {
        'token': f"{token}",
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
        user.updateJwt(f"{token}", onjectId)
        token = jwt.encode(jwt_payload, jwt_secret, algorithm='HS256')
    except Exception as e:
        app.logger.error(f'Error creating JWT token: {e}')
        return jsonify({'error': validation_messages['jwt_creation_error'][language]}), 401
    
    response_data = {
        'token': f"{token}",
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
        user.updateJwt(f"{token}", onjectId)
    except Exception as e:
        app.logger.error(f'Error creating JWT token: {e}')
        return jsonify({'error': validation_messages['jwt_creation_error'][language]}), 401
    
    response_data = {
        'token': f"{token}",
        'data': user_data
    }

    logging.info(f'Response: {response_data}')
    return jsonify(response_data), 200