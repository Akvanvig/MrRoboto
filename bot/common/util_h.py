import asyncio
import re
import json
import xml.etree.ElementTree as ET

from urllib.request import urlopen
from urllib.parse import urlparse
from functools import wraps, partial

#
# CONSTANTS
#

MSG_LIMIT = 1990

#
# PRIVATE
#

_HTML_RE = re.compile(r'<[^>]+>')
_NEWLINE_RE = re.compile(r'\n\s*\n')

class RequirementError(Exception):
    def __init__(self):
        super().__init__("The extension did not pass the requirement check")

def _blocking_network_io(request, format_):
    try:
        with urlopen(request) as response:
            content = response.read()

        if format_ is dict:
            return json.loads(content)
        elif format_ is ET:
            return ET.fromstring(content)
        else:
            return content
    except Exception as e:
        print(e)

#
# PUBLIC
#

def requirement_check(check):
    def decorator(func):
        @wraps(func)
        def wrapper(client):
            if not check(client):
                raise RequirementError()
            func(client)
        return wrapper
    return decorator

def is_valid_url(text):
    try:
        url = urlparse(text)
    except:
        return False

    return all([url.scheme, url.netloc, url.path])

def read_website_content(request, format_=None, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    return loop.run_in_executor(None, partial(_blocking_network_io, request, format_))

# Splits a message into requested length parts
# Gives option to split on custom symbol
def message_split(message, length=MSG_LIMIT, split='\n'):
    result_list = []

    while len(message) > length:
        split_point = message.rfind(split, 0, length) + 1

        if split_point <= 0: #If requested symbol doesn't exist, use full length
            split_point = length

        part = message[:split_point]
        message = message[len(part):]

        result_list.append(part)

    result_list.append(message)

    return result_list

def message_truncate(message, length, suffix='...'):
    if len(message) <= length:
        return message

    return ' '.join(message[:length+1-len(suffix)].split(' ')[0:-1]).rstrip() + suffix

def remove_html_tags(text):
    return _HTML_RE.sub('', text)

def remove_multi_newlines(text):
    return _NEWLINE_RE.sub('\n\n', text)

def save_json(obj, path):
    file = open(path, 'w')
    json.dump(obj, file, indent=4)
    file.close()

def get_json(path):
    file = open(path, 'r')
    json_obj = json.load(file)
    file.close()

    return json_obj