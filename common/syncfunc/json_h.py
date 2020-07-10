import json

#
# PUBLIC INTERFACE
#

def saveJson(obj, path):
    file = open(path, 'w')
    json.dump(obj, file, indent=4)
    file.close()

def getJson(path):
    file = open(path, 'r')
    jsonObj = json.load(file)
    file.close()

    return jsonObj