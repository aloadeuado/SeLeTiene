from Configuration import *

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
