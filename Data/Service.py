from pymongo import MongoClient
from Configuration import *
from bson.objectid import ObjectId
import bcrypt

class Service:
    def __init__(self, db):
        self.db = db
        self.services = self.db["Services"]

    def __init__(self, name, description, initial, nameEs, descriptionEs, initialEs, imgUrl, timeInitDay, timeFinalDay, isActive, isShow, user_id, db):
        self.name = name
        self.description = description
        self.initial = initial
        self.descriptionEs = descriptionEs
        self.nameEs = nameEs
        self.initialEs = initialEs
        self.imgUrl = imgUrl
        self.timeInitDay = timeInitDay
        self.timeFinalDay = timeFinalDay
        self.isActive = isActive
        self.isShow = isShow
        self.user_id =  user_id
        self.db = db
        self.services = self.db["Services"]

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'initial': self.initial,
            'descriptionEs': self.descriptionEs,
            'nameEs': self.nameEs,
            'initialEs': self.initialEs,
            'imgUrl': self.imgUrl,
            'timeInitDay': self.timeInitDay,
            'timeFinalDay': self.timeFinalDay,
            'isActive': self.isActive,
            'isShow': self.isShow,
            'user_id': self.user_id
        }

    @staticmethod
    def from_dict(data):
        return Service(**data)
    
    def find_by_id(self, id):
        result = self.services.find_one({"_id": ObjectId(id)})
        if result:
            return result
        return None
    
    def find_by_name(self, name):
        result = self.services.find_one({"name": name})
        if result:
            return result
        return None
    
    def create(self) :
        try:
            query = self.to_dict()
            response = self.services.insert_one(query)
            return response
        except Exception as e:
            return None
        
    def getServices(self) :
        try:
            response = self.services.find({"isActive": True, "isShow": True})
            return response
        except Exception as e:
            return None
