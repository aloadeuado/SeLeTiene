from pymongo import MongoClient

client = MongoClient("mongodb://Lordviril:Gorposi0717@44.215.48.103:27017/SeLeTiene")
clientArbelaez = MongoClient("mongodb://essenza:Lordviril0510@44.215.48.103:27017/ArbelaezApp")

environment = {
    "qa": "Qa",
    "prd":"Prd",
    "all": "All"
}