import json

#
# PUBLIC INTERFACE
#

def save_json(obj, path):
    file = open(path, 'w')
    json.dump(obj, file, indent=4)
    file.close()

def get_json(path):
    print("Json path: "+path)
    file = open(path, 'r')
    json_obj = json.load(file)
    file.close()

    return json_obj