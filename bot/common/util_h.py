import re
import json

from urllib.request import urlopen
from functools import partial

#
# CONSTANTS
#

MSG_LIMIT = 1990

#
# PRIVATE
#

_HTML_RE = re.compile(r'<[^>]+>')

def _blocking_network_io(request):
    with urlopen(request) as response:
        return response.read()

#
# PUBLIC
#

def read_website_content(loop, request):
    return loop.run_in_executor(None, partial(_blocking_network_io, request))

# Splits a message into requested length parts
# Gives option to split on custom symbol
def message_split(message, length=MSG_LIMIT, split="\n"):
    resultlist = []
    while len(message) > length:
        split_point = message.rfind(split, 0, length) + 1
        if split_point <= 0: #If requested symbol doesn't exist, use full length
            split_point = length
        part = message[:split_point]
        message = message[len(part):]
        resultlist.append(part)
    resultlist.append(message)
    return resultlist

def remove_html_tags(text):
    return _HTML_RE.sub('', text)

def save_json(obj, path):
    file = open(path, 'w')
    json.dump(obj, file, indent=4)
    file.close()

def get_json(path):
    file = open(path, 'r')
    json_obj = json.load(file)
    file.close()

    return json_obj