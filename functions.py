import os
import json

#Funksjoner
def saveJson(obj, path):
    with open(path, 'w') as fout:
        json.dump(obj, fout, indent=4)

def getJson(path):
    with open(path, 'r') as fout:
        return json.load(fout)

def createFolderIfNotExist(path):
    if not os.path.exists(path):
        os.makedirs(path)
