from pymongo import MongoClient

client = MongoClient("mongodb://Armentor:L0rdv1r1l0717@44.215.48.103:27017/SeLeTieneQa")
clientArbelaez = MongoClient("mongodb://essenza:Lordviril0510@44.215.48.103:27017/ArbelaezApp")
SERVICE_KEY = "321668ec2852bdb9e7c2791e38e4c2774fe39ebcd62461ea48272bbec12985fc"
environment = {
    "qa": "Qa",
    "prd":"Prd",
    "all": "All"
}
#Email spmt
SMTP_HOST = 'smtp.gmail.com'
SMPT_PORT = 587
SENDER_EMAIL = "essenzasocial88@gmail.com"
SENDER_PASSWORD = "moqhxrgwcebmhbhp"