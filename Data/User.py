from pymongo import MongoClient
from Configuration import *
from bson.objectid import ObjectId
import bcrypt

class User:
    def __init__(self, db):
        self.db = db
        self.users = self.db["Users"]

    def create(self, user_data):
        self.users.insert_one(user_data)

    def find_by_email(self, email):
        return self.users.find_one({'email': email})

    def find_by_mobile_phone(self, mobile_phone):
        return self.users.find_one({'mobilePhone': mobile_phone})
    
    def find_by_id(self, id):
        result = self.users.find_one({"_id": ObjectId(id)})
        if result:
            return result
        return None

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def updateJwt(self, jwt, objectItemId) :
        self.users.update_one({"_id": objectItemId}, { "$set": {"jwtKey": jwt}})
    
    def find_by_apple_id(self, apple_id):
        return self.users.find_one({'appleId': apple_id})

    def find_by_accessToken(self, googleId):
        return self.users.find_one({'googleId': googleId})
    
    def update(self, user_id, user_data):
        result = self.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_data})
        return result.modified_count > 0
    
    def get_user_validate_token(self, id, token):
        result = self.users.find_one({"_id": ObjectId(id), "jwtKey": token})
        return result
    