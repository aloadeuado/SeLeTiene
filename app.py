from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient("mongodb://Lordviril:Gorposi0717@100.24.31.104:11981/")
db = client["SeLeTiene"]
users = db["Users"]

@app.route("/lologramos", methods=["GET"])
def lologramos():
    return jsonify({"test": "complete"})

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    # Autogenerated ID
    data["_id"] = "ObjectId()"
    # Insert new user
    users.insert_one(data)
    return jsonify({"message": "User created successfully"})


if __name__ == '__main__':
    app.run(debug=True)
