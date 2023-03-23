from Configuration import *
import secrets
import bcrypt

dbQa = client.get_database("SeLeTieneQa")
dbPrd = client.get_database("SeLeTiene")

def saveEnviromentMongo(data, env):
    if env == environment["qa"]:
        dbQa.insert_one(data)
    elif env == environment["prd"]:
        dbPrd.insert_one(data)
    else:
        dbQa.insert_one(data)
        dbPrd.insert_one(data)

def getEnviromentMongo(env):
    if env == environment["qa"]:
        return dbQa
    elif env == environment["prd"]:
        return dbPrd
    else:
        raise ValueError("Invalid environment")
    
def generate_secret_key():
    return secrets.token_hex(32)

def check_password(hashed_password, password):
    password_bytes = password.encode('utf-8') if isinstance(password, str) else str(password).encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
    return bcrypt.checkpw(password_bytes, hashed_bytes)
