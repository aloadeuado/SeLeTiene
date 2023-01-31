from contextlib import nullcontext
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient("mongodb://Lordviril:Gorposi0717@100.26.132.234:27017/SeLeTiene")
clientArbelaez = MongoClient("mongodb://miguel:arbelaez@100.26.132.234:27017/Arbelaez")
db = client.get_database("SeLeTiene")
dbArbelaez = clientArbelaez.get_database("Arbelaez")
users = db["Pruebas"]
usersArbelaez = dbArbelaez["Users"]

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
    emailExist = usersArbelaez.find({"email": email})

    if  emailExist : 
        return jsonify({"error": "El email ya existe"}), 400 
    else :
        usersArbelaez.insert_one(data)
        return jsonify({"message": "Complete"}), 200 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)