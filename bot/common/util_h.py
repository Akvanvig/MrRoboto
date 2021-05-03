import xml.etree.ElementTree as ET

#
# CONSTANTS
#

MSG_LIMIT = 1990

#
#
#

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

# Remove html tags
def remove_html_tags(text):
    return ''.join(ET.fromstring(text).itertext())