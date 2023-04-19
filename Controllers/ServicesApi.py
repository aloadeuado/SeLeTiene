import os
import uuid
import jwt as jwt
import datetime
from flask import request, jsonify, send_file
from Data.Service import Service
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


@app.route('/api/createServices', methods=['POST'])
def createServices():
    
    language = request.headers.get('Language', 'en')
    env = request.headers.get('Env')
    token = request.headers.get('Token', '')
    if validatorsHeaders(env,language, token, logging, request.url) :
        return jsonify(validatorsHeaders(env,language, token, logging, request.url)), 400

    name = request.form.get("name", "")
    description = request.form.get("description", "")
    image = request.files["image"]

    if not name or not description or not image :
        error_message = validation_messages["missing_fields"][language].replace("{fields}", "name, description, image")
        logging.error(f"Error: User not found - Request: {request.url} - Response: {error_message}")
        return jsonify({"error": error_message}), 400
    
    response = validateToken(env,language, token, logging, request.url)

    if response.get("error", None) :
        return jsonify(response), 401

    uid = uuid.uuid4()
    filename = str(uid) + name + ".png"
    image.save(os.path.join('image', filename))
    url = request.host_url + 'image/' + filename

    service = Service(name, description, url, 0, 0, True, True, response.get("_id", None), getEnviromentMongo(env))
    is_exist_service = service.find_by_name(name)
    if is_exist_service :
        return jsonify({"error": "No add services"}), 400
    
    response = service.create()
    if not response :
        return jsonify({"error": validation_messages["service_already_exists"][language]}), 400
    
    return jsonify({"message": "Servicio creado"}), 200



@app.route('/api/Services/getServices', methods=['GET'])
def getServices():
    res = validateHeadersToken(request, logging)
    if res.get("error", None) :
        return jsonify(res), 401

    language = request.headers.get('Language', 'en')
    env = request.headers.get('Env')
    token = request.headers.get('Token', '')

    services = Service("", "", "", 0, 0, True, True, res, getEnviromentMongo(env))
    servicess = services.getServices()

    if not servicess :
        return jsonify({"error": validation_messages["no_services_registered"][language]})

    
    listServicesData = []
    for documento in servicess :
        data = {"id": str(documento["_id"])}
        data["name"] = documento["name"]
        data["description"] = documento["description"]
        data["imgUrl"] = documento["imgUrl"]
        listServicesData.append(data)
    return {"data": listServicesData}, 200


@app.route('/image/<nombre>', methods=['GET'])
def obtener_imagen_full(nombre):
    try:
        # Ruta completa del archivo de imagen
        ruta = f"uploads/{nombre}"
        
        # Devolver la imagen
        return send_file(ruta, mimetype='image/jpeg')
    except Exception as e:
        return str(e)
