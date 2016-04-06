import re

def parse(xml):
    for element in re.findall('<\w*?>.*?</\w*?>', xml):
        data = element.replace('>', '<').split('<')
        if not data[1] == 'tokens':
            yield(data[1], data[2].strip())

def unparse(data):
    xml = ''
    for element in data:
        xml += '<{type}> {text} </{type}>\n'.format(type=element[0], text=element[1])
    return xml
