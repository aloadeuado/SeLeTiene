from contextlib import nullcontext
from flask import Flask, jsonify, request, send_file
from pymongo import MongoClient
from bson import json_util
import os
import uuid
from bson import ObjectId
import pymongo

app = Flask(__name__)
client = MongoClient("mongodb://Lordviril:Gorposi0717@100.26.132.234:27017/SeLeTiene")
clientArbelaez = MongoClient("mongodb://miguel:arbelaez@100.26.132.234:27017/Arbelaez")
db = client.get_database("SeLeTiene")
dbArbelaez = clientArbelaez.get_database("Arbelaez")
users = db["Pruebas"]
usersArbelaez = dbArbelaez["Users"]
itemsArbelaez = dbArbelaez["Items"]
listCurrencyArbelaez = dbArbelaez["ListCurrency"]

charsValidateNumbers = "0123456789"
charsValidateNumbers = "0123456789"
@app.route("/lologramos", methods=["GET"])
def lologramos():
    return jsonify({"test": "complete"})

@app.route("/users", methods=["POST"])
def create_user():   
    data = request.get_json()
    # Autogenerated ID
    #data["_id"] = "usertest"
    # Insert new user
    users.insert_one(data)
    return jsonify({"message": "Complete"})

@app.route("/usersArbelaez", methods=["POST"])
def create_user_arbelaez():   
    data = request.get_json()
    mobilePhone = data["mobilePhone"]
    if len(mobilePhone) != 10 :
        return jsonify({"error": "El numero de telefono debe ser de 10 caracteres"}), 400   
    
    if not mobilePhone.isdigit() :
        return jsonify({"error": "El numero de telefono debe tener solo numeros"}), 400 
    
    mobilePhoneExisat = usersArbelaez.find_one({"mobilePhone": mobilePhone})
    if mobilePhoneExisat :
        return jsonify({"error": "El numero de telefono ya esta registrado"}), 400 
    
    name = data["name"] 
    if not name.isalpha() :
        return jsonify({"error": "El nombre solo debe contener caracteres alfabeticos"}), 400 
    
    lastName = data["lastName"]
    if not lastName.isalpha() :
        return jsonify({"error": "El apellido solo debe contener caracteres alfabeticos"}), 400 
    
    password = data["password"]
    if len(password) <= 7 :
        return jsonify({"error": "El password no tiene 8 caracteres como minimo"}), 400       
    
    email = data["email"]
    emailExist = usersArbelaez.find_one({"email": email})

    if  emailExist : 
        return jsonify({"error": "El email ya existe"}), 400 
    else :
        usersArbelaez.insert_one(data)
        return jsonify({"message": "Complete"}), 201 

@app.route("/login", methods=["POST"])
def login():   
    data = request.get_json()
    email = data["email"]
    emailExist = usersArbelaez.find_one({"email": email})
    if not emailExist :
        return jsonify({"error": "no fue posible autenticarse"}), 400
    if emailExist["password"] == data["password"] :
        return json_util.dumps(emailExist), 200 
    return jsonify({"error": "no fue posible autenticarse"}), 400

@app.route("/createCurrency", methods=["POST"])
def createCurrency(): 
    data = request.get_json()
    listCurrencyArbelaez.insert_one(data)
    return jsonify({"message": "Currency creado"}), 201 

@app.route("/getListCurrency", methods=["GET"])
def getListCurrency(): 
    listCurrency = listCurrencyArbelaez.find()
    listCurrencyData = []
    for documento in listCurrency :
        data = {"id": str(documento["_id"])}
        data["moneda"] = documento["moneda"]
        data["currency"] = documento["currency"]
        data["code"] = documento["code"]
        listCurrencyData.append(data)
    return {"data": listCurrencyData}, 200

@app.route("/addItem", methods=["POST"])
def createItems(): 
    data = request.form
    #data = request.get_json()
    if not isinstance(data["name"], str) :
        return jsonify({"error": "el campo name debe ser un String"}), 400 
    if data["name"] == "" :
        return jsonify({"error": "el campo name no puede ir vacio"}), 400
    # Obtener el archivo de la solicitud
    item = itemsArbelaez.find_one({"name": str(data["name"])})
    if  item : 
        return jsonify({"error": "el nombre del producto ya existe"}), 400 
    file = request.files['file']
    uid = uuid.uuid4()
    filename = str(uid) + file.filename
    file.save(os.path.join('uploads', filename))
    url = request.host_url + 'uploads/' + filename
    if not isinstance(data["description"], str) :
        return jsonify({"error": "el campo description debe ser un String"}), 400 
    if data["description"] == "" :
        return jsonify({"error": "el campo description no puede ir vacio"}), 400 
    if not isinstance(data["idCurrency"], str) :
        return jsonify({"error": "el campo idCurrency debe ser un String"}), 400 
    if data["idCurrency"] == "" :
        return jsonify({"error": "el campo idCurrency no puede ir vacio"}), 400 
    sstrIdCurrency = str(data["idCurrency"])
    idCurrency = ObjectId(sstrIdCurrency)
    currency = listCurrencyArbelaez.find_one({"_id": idCurrency}) 
    if not currency :
        return jsonify({"error": "el id currency no esta registrado"}), 400 
    try:
        priceValue = float(data["price"])
    except error:
        return jsonify({"error": "el campo price debe ser un duoble"}), 400 

    itemsArbelaez.insert_one({"name": str(data["name"]), "description": str(data["description"]), "idCurrency": currency, "price": priceValue, "urlImage": url})
    return jsonify({"message": "Producto creado"}), 201 

@app.route('/uploads/<nombre>', methods=['GET'])
def obtener_imagen(nombre):
    try:
        # Ruta completa del archivo de imagen
        ruta = "uploads/{nombre}"
        
        # Devolver la imagen
        return send_file(ruta, mimetype='image/jpeg')
    except Exception as e:
        return str(e)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)