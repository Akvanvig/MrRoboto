import json

def saveJson(obj, path):
    file = open(path, 'w')
    json.dump(obj, file, indent=4)

def getJson(path):
    file = open(path, 'r')
    return json.load(file)