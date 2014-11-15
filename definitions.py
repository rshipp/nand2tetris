import string

def type(token):
    if token in list(string.punctuation):
        return 'symbol'
    elif token.isdigit():
        return 'integerConstant'
    elif token.startswith('"') and token.endswith('"'):
        return 'stringConstant'
    elif token in keywords:
        return 'keyword'
    else:
        return 'identifier'

keywords = [
    'boolean',
    'char',
    'class',
    'constructor',
    'do',
    'else',
    'false',
    'field',
    'function',
    'if',
    'int',
    'let',
    'method',
    'return',
    'this',
    'true',
    'var',
    'void',
    'while',
]
