from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required, current_identity
from pymongo import MongoClient
from oauth2client import client
from bson import json_util
import uuid
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
api = Api(app)

client = MongoClient("mongodb://Lordviril:Gorposi0717@100.26.132.234:27017/SeLeTiene")
db = client.get_database("SeLeTiene")
users = db["UsersTest"]
listTextSearch = db["ListTextSearchTest"]
listRecipeLocation = db["ListRecipeLocation"]

def solve(s):
   pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
   if re.match(pat,s):
      return True
   return False

@app.route("/yape/api/registerOrAuth", methods=["POST"])
def create_user_test_yape():   
    data = request.get_json()
    return jsonify({"message": "Complete", "data": {"email": data["email"], "password": data["password"], "token":"1032123456"}}), 201

@app.route("/yape/api/addTextSearch", methods=["POST"])
def addTextSearch():   
    data = request.get_json()
    return jsonify({"data": ["potato", "pasta", "sandwich", "rice", data["rice"]]}), 200


@app.route("/yape/api/getTextSearch", methods=["POST"])
def getListTextSearch():
    data = request.get_json()   
    return jsonify({"data": ["potato", "pasta", "sandwich", "rice"]}), 200


@app.route("/yape/api/getLocationsRecipes", methods=["GET"])
def getLocationsRecipes():
    return jsonify({"data": 
    [
        {
            "idRecipe": 716627,
            "lat": 4.7109886,
            "lot": -74.072092
        },
        {
            "idRecipe": 646738,
            "lat": 6.2476376,
            "lot": -75.5658153
        },
        {
            "idRecipe": 715421,
            "lat": 3.4516467,
            "lot": -76.5319854
        }
    ]
}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)