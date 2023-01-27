from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient("mongodb://Lordviril:Gorposi0717@localhost:27017/")
db = client["SeLeTiene"]
users = db["Users"]
db.authenticate('Lordviril', 'Gorposi0717')

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
    return jsonify({"message": "User created successfully"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
