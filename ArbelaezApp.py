
from flask import request, jsonify, send_file
from app import app
from Configuration import *
from bson import json_util
import uuid
from bson import ObjectId
import os
import datetime

dbArbelaez = clientArbelaez.get_database("ArbelaezApp")

usersArbelaez = dbArbelaez["Users"]
itemsArbelaez = dbArbelaez["Items"]
listCurrencyArbelaez = dbArbelaez["ListCurrency"]
itemsFavorites = dbArbelaez["ItemsFavorites"]

charsValidateNumbers = "0123456789"
charsValidateNumbers = "0123456789"

@app.route("/addOrRemoveFavorite", methods=["POST"])
def addOrRemoveFavorite(): 
    data = request.get_json()
    idItem = data["idItem"]
    idUser = data["idUser"]

    if not isinstance(idItem, str) :
        return jsonify({"error": "el campo idItem debe ser un String"}), 400 
    if idItem == "" :
        return jsonify({"error": "el campo idItem no puede ir vacio"}), 400

    if not isinstance(idUser, str) :
        return jsonify({"error": "el campo idUser debe ser un String"}), 400 
    if idUser == "" :
        return jsonify({"error": "el campo idUser no puede ir vacio"}), 400
    
    onjectId = ObjectId(idUser)
    user = usersArbelaez.find_one({"_id": onjectId})

    if not user :
        return jsonify({"error": "El usuario no exite"}), 400
    
    objectItemId = ObjectId(idItem)
    item = itemsArbelaez.find_one({"_id": objectItemId})

    if not item :
        return jsonify({"error": "El Item no exite"}), 400

    try :
        usersFavorite = item["UsersFavorite"]
        idUserExist = next((x for x in usersFavorite if x["idUser"] == idUser), None)
        if not idUserExist :
            usersFavorite.append({"idUser": idUser, "date": datetime.datetime.utcnow()})
            item["UsersFavorite"] = usersFavorite
            itemsArbelaez.update_one({"_id": objectItemId}, { "$set": item})
            return jsonify({"message": "Usuario Agregado"}), 200
        else :
            usersFavorite = [x for x in usersFavorite if not x["idUser"] == idUser]
            item["UsersFavorite"] = usersFavorite
            itemsArbelaez.update_one({"_id": objectItemId}, { "$set": item})
            return jsonify({"message": "Usuario Eliminado"}), 200
    except :
        item["UsersFavorite"] = [{"idUser": idUser, "date": datetime.datetime.utcnow()}]
        itemsArbelaez.update_one({"_id": objectItemId}, { "$set": item})
        return jsonify({"message": "Usuario Agregado"}), 200

@app.route("/getListItems", methods=["POST"])
def getListItems(): 
    data = request.get_json()
    idUser = data["idUser"]
    listItemsArbelaez = itemsArbelaez.find()
    listCurrency1 = listCurrencyArbelaez.find()
    listItemsArbelaezData = []
    listItemsArbelaezDataDelete = []
    for documento in listItemsArbelaez :
        isDelete:bool = False
        try :
            isDelete = documento["isDelete"]
        except :
            print
        usersFavorite = documento.get("UsersFavorite", [])
        userExist = next((x for x in usersFavorite if x["idUser"] == idUser), None)
        
        if isDelete :
            data = {"id": str(documento["_id"])}
            data["name"] = documento["name"]
            data["description"] = documento["description"]
            data["currency"] = checkCurrency(listCurrency1, str(documento["idCurrency"]["_id"]))["currency"]
            data["price"] = documento["price"]
            data["urlImage"] = documento["urlImage"]
            data["isFavorite"] = userExist is not None

            listItemsArbelaezDataDelete.append(data)
        else :
            data = {"id": str(documento["_id"])}
            data["name"] = documento["name"]
            data["description"] = documento["description"]
            data["currency"] = checkCurrency(listCurrency1, str(documento["idCurrency"]["_id"]))["currency"]
            data["price"] = documento["price"]
            data["urlImage"] = documento["urlImage"]
            data["isFavorite"] = userExist is not None
            listItemsArbelaezData.append(data)

    return {"data": listItemsArbelaezData, "dataDelete": listItemsArbelaezDataDelete}, 200
        







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

@app.route("/updateItem", methods=["POST"])
def updateItem(): 
    data = request.form
    #data = request.get_json()
    if not isinstance(data["id"], str) :
        return jsonify({"error": "el campo id debe ser un String"}), 400 
    if data["id"] == "" :
        return jsonify({"error": "el campo id no puede ir vacio"}), 400
    if not isinstance(data["name"], str) :
        return jsonify({"error": "el campo name debe ser un String"}), 400 

    # Obtener el archivo de la solicitud
    if not request.files['file'] :
        url = ""
    else :
        file = request.files['file']
        uid = uuid.uuid4()
        filename = str(uid) + file.filename
        file.save(os.path.join('uploads', filename))
        url = request.host_url + 'uploads/' + filename
    if not isinstance(data["description"], str) :
        return jsonify({"error": "el campo description debe ser un String"}), 400 

    if not isinstance(data["idCurrency"], str) :
        return jsonify({"error": "el campo idCurrency debe ser un String"}), 400 

    sstrIdCurrency = str(data["idCurrency"])
    idCurrency = ObjectId(sstrIdCurrency)
    currency = listCurrencyArbelaez.find_one({"_id": idCurrency}) 
    if not currency :
        return jsonify({"error": "el id currency no esta registrado"}), 400 
    try:
        priceValue = float(data["pr54ice"])
    except :
        return jsonify({"error": "el campo price debe ser un duoble"}), 400 
    idd = data["id"]
    onjectId = ObjectId(idd)
    item = itemsArbelaez.find_one({"_id": onjectId})
    if  not item : 
        return jsonify({"error": "el item no existe"}), 400 
    dataSet: map = {}
    if data["name"] != "" :
        dataSet["name"] = data["name"]
    if url != "" :
        dataSet["urlImage"] = url
    if item:
        dataSet["name"] = currency
    
    itemsArbelaez.update_one({"_id": onjectId}, { "$set": {"name": str(data["name"]), "description": str(data["description"]), "idCurrency": currency, "price": priceValue, "urlImage": url} })
    return jsonify({"message": "Item actualizado"}), 200

@app.route("/deleteItem", methods=["POST"])
def deleteItem(): 
    data = request.get_json()
    if not isinstance(data["id"], str) :
        return jsonify({"error": "el campo id debe ser un String"}), 400 
    if data["id"] == "" :
        return jsonify({"error": "el campo id no puede ir vacio"}), 400
    idd = data["id"]
    onjectId = ObjectId(idd)
    item = itemsArbelaez.find_one({"_id": onjectId})
    if  not item : 
        return jsonify({"error": "el item no existe"}), 400 
    itemsArbelaez.update_one({"_id": onjectId}, { "$set": {"isDelete": True} })
    return jsonify({"message": "Item Eliminado"}), 200

@app.route('/uploads/<nombre>', methods=['GET'])
def obtener_imagen(nombre):
    try:
        # Ruta completa del archivo de imagen
        ruta = f"uploads/{nombre}"
        
        # Devolver la imagen
        return send_file(ruta, mimetype='image/jpeg')
    except Exception as e:
        return str(e)


def checkCurrency(listCurrency, idCurrency):
    currency = {"currency": "$"}
    for document in listCurrency:
        if str(document["_id"]) == idCurrency :
            currency = document
            break

    return currency