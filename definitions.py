import re
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
    elif re.findall('^[A-Za-z_]+\w*$', token):
        return 'identifier'
    else:
        raise Exception("Can't parse token: {token}".format(token=token))

expr_symbols = [
    '&',
    '*',
    '+',
    '-',
    '/',
    '|',
    '&lt;',
    '=',
    '&gt;',
]

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
    'null',
    'return',
    'static',
    'this',
    'true',
    'var',
    'void',
    'while',
]
