from pymongo import MongoClient
from Configuration import *

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