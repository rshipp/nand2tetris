"""Jack parser for CSCI410 HW10."""

import os
import sys
import re

import xmlhandler
import definitions

def parse(filename):
    if os.path.isdir(filename):
        files = (os.path.join(filename, f) for f in os.listdir(filename) if f.endswith('T.xml'))
    else:
        files = [filename]

    # Analyze code.
    for tfile in files:
        with open(tfile, "r") as f:
            tokens = [t for t in xmlhandler.parse(f.read())]
            shortname = os.path.basename(tfile)[:-len('T.xml')]

            # Parse.
            xml = compile(tokens)

            with open(''.join([shortname, '.xml']), "w") as t:
                t.write(xml)

def match_structure(structure, tokens):
    start, end = structure
    for c, element in enumerate(start):
        if element and tokens[c][1] != element:
            return False
    for c in range(1, len(end)+1):
        if not end[-c] and tokens[-c][1] != end[-c]:
            return False
    return True

def compile(tokens):
    return terms[tokens[0][1]](tokens)

def compile_class(tokens):
    """ class Identifier { tokens } """
    head = xmlhandler.unparse(tokens[0:3])
    mid = tokens[3:-1]
    tail = xmlhandler.unparse(tokens[-1:])
    return '<class>\n' + head + compile(mid) + tail + '</class>\n'

def compile_subroutineDec(tokens):
    """ Keyword Keyword Identifier ( parameterList ) { tokens } """
    head = xmlhandler.unparse(tokens[0:4])
    parameterList = []
    c = 0
    for token in tokens[4:]:
        if token[1] != ')':
            parameterList.append(token)
        else:
            break
        c += 1
    second = tokens[4+c]
    mid = tokens[4+c+1:-1]
    tail = xmlhandler.unparse(tokens[-1:])
    return '<subroutineDec>\n' + head + compile(mid) + tail + '</subroutineDec>\n'


structures = {
    (('class', None, '{'), ('}')): compile_class,
#    (('function', None, '{'
}

nonterminals = {
    #'class': '',
    #'classVarDec': '',
    #'subroutineDec': '',
    ##'parameterList': '',
    ##'subroutineBody': '',
    #'varDec': '',
    ##'statements': '',
    #'whileStatement': '',
    #'ifStatement': '',
    #'returnStatement': '',
    #'letStatement': '',
    #'doStatement': '',
    ##'expression': '',
    ##'term': '',
    ##'expressionList': '',
}

terms = {
    'class': compile_class,
    'constructor': compile_subroutineDec,
    'do': compile_doStatement,
    'field': compile_classVarDec,
    'function': compile_subroutineDec,
    'if': compile_ifStatement,
    'let': compile_letStatement,
    'method': compile_subroutineDec,
    'return': compile_returnStatement,
    'static': compile_classVarDec,
    'var': compile_varDec,
    'while': compile_whileStatement,
}

if __name__ == "__main__":
    parse(sys.argv[1])
