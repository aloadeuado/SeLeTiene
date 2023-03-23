from pymongo import MongoClient
from Configuration import *

class User:
    def __init__(self, db):
        self.db = db
        self.users = self.db["Users"]

    def create(self, user_data):
        self.users.insert_one(user_data)