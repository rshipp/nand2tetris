"""Jack compiler for CSCI410 HW11."""

import os
import sys

import tokenizer
import xmlhandler
import definitions
import symboltable

def parse(filename):
    if os.path.isdir(filename):
        files = (os.path.join(filename, f) for f in os.listdir(filename) if f.endswith('.jack'))
    else:
        files = [filename]

    # Tokenize and analyze code.
    for tfile in files:
        with open(tfile, "r") as f:
            tokens = (t for t in xmlhandler.parse(tokenizer.tokenize(f.read())))
            shortname = os.path.basename(tfile)[:-len('T.xml')]

            # Parse.
            parser = Parser(tokens)
            xml = parser.compile_class()

            with open(''.join([shortname, '.vm']), "w") as t:
                t.write('\n'.join(parser.code)+'\n')


class Parser:
    """Parses XML input from the tokenizer."""
    def __init__(self, tokens):
        """'tokens' should be a generator expression."""
        self.tokens = tokens
        next = self.tokens.next()
        self.next_token = next[1]
        self.next_type = next[0]
        self.symbols = symboltable.SymbolTable()
        self.code = []

    def advance(self):
        try:
            next = self.tokens.next()
            self.next_token = next[1]
            self.next_type = next[0]
        except StopIteration:
            pass

    def compile_class(self):
        if self.next_token == 'class':
            xml = '<class>\n' + self.compile_terminal('class')
            self.symbols.set_class(self.next_token)
            xml += self.compile_terminal() + self.compile_terminal('{') + \
                   self.compile_classVarDec() + self.compile_subroutineDecs() + \
                   self.compile_terminal('}') + '</class>\n'
            return xml

    def compile_terminal(self, match=False):
        terminal = (self.next_type, self.next_token)
        if match and match != self.next_token:
            raise SyntaxError("Expected '{e}', but got '{a}'".format(e=match, a=self.next_token))
        self.advance()
        return xmlhandler.unparse([terminal])

    def compile_classVarDec(self):
        if not self.next_token in ['field', 'static']:
            # Empty
            return ''
        # Non-empty
        kind = self.next_token
        xml = '<classVarDec>\n' + self.compile_terminal()
        type = self.next_token
        xml += self.compile_terminal()
        self.symbols.track(self.next_token, type, kind)
        xml += self.compile_terminal() + self.compile_varIdentifiers(type, kind) + \
               self.compile_terminal(';') + '</classVarDec>\n' + \
               self.compile_classVarDec()
        return xml

    def compile_varDec(self):
        xml = '<varDec>\n' + self.compile_terminal('var')
        kind = 'local'
        type = self.next_token
        xml += self.compile_terminal()
        self.symbols.track(self.next_token, type, kind)
        xml += self.compile_terminal()
        while self.next_token == ',':
            xml += self.compile_terminal(',')
            self.symbols.track(self.next_token, type, kind)
            xml += self.compile_terminal()
        return xml + self.compile_terminal(';') + '</varDec>\n'

    def compile_varIdentifiers(self, type=None, kind=None):
        if self.next_token != ',':
            # Empty
            return ''
        # Non-empty
        xml = self.compile_terminal(',')
        self.symbol.track(self.next_token, type, kind)
        return xml + self.compile_terminal() + \
               self.compile_varIdentifiers()

    def compile_subroutineDecs(self):
        if not self.next_token in ['constructor', 'function', 'method']:
            # Empty
            return ''
        # Non-empty
        kind = self.next_token
        xml = '<subroutineDec>\n' + self.compile_terminal() + \
              self.compile_terminal()
        self.symbols.set_function(self.next_token)
        return xml + self.compile_terminal() + \
               self.compile_terminal('(') + self.compile_parameterList() + \
               self.compile_terminal(')') + self.compile_subroutineBody() + \
               '</subroutineDec>\n' + self.compile_subroutineDecs()

    def compile_parameterList(self):
        if self.next_token == ')':
            # Empty
            return '<parameterList>\n</parameterList>\n'
        # Non-empty
        kind = 'argument'
        type = self.next_token
        xml = '<parameterList>\n' + self.compile_terminal() 
        self.symbols.track(self.next_token, type, kind)
        xml += self.compile_terminal()
        while self.next_token == ',':
            xml += self.compile_terminal(',')
            type = self.next_token
            xml += self.compile_terminal()
            self.symbols.track(self.next_token, type, kind)
            xml += self.compile_terminal()
        return xml + '</parameterList>\n'

    def compile_subroutineBody(self):
        xml = '<subroutineBody>\n' + self.compile_terminal('{')
        numlocals = 0
        while self.next_token == 'var':
            xml += self.compile_varDec()
            numlocals += 1
        self.code += ["function {c}.{f} {n}".format(c=self.symbols.get_class(),
                                                    f=self.symbols.get_function(),
                                                    n=numlocals)]
        self.hasreturn = False
        xml += self.compile_statements() + self.compile_terminal('}')
        if not self.hasreturn:
            self.code += [
                "push constant 0",
                "return",
            ]
        return xml + '</subroutineBody>\n'

    def compile_statements(self):
        xml = '<statements>\n'
        statement_types = {
            'while': self.compile_whileStatement,
            'if': self.compile_ifStatement,
            'return': self.compile_returnStatement,
            'let': self.compile_letStatement,
            'do': self.compile_doStatement,
        }
        while self.next_token in statement_types:
            if self.next_token == 'return':
                self.hasreturn = True
            xml += statement_types[self.next_token]()
        return xml + '</statements>\n'

    def compile_whileStatement(self):
        return '<whileStatement>\n' + self.compile_terminal('while') + \
               self.compile_terminal('(') + self.compile_expression() + \
               self.compile_terminal(')') + self.compile_terminal('{') + \
               self.compile_statements() + self.compile_terminal('}') + \
               '</whileStatement>\n'

    def compile_ifStatement(self):
        xml = '<ifStatement>\n' + self.compile_terminal('if') + \
              self.compile_terminal('(') + self.compile_expression() + \
              self.compile_terminal(')') + self.compile_terminal('{') + \
              self.compile_statements() + self.compile_terminal('}')
        if self.next_token == 'else':
            xml += self.compile_terminal('else') + \
                    self.compile_terminal('{') + self.compile_statements() + \
                    self.compile_terminal('}')
        return xml + '</ifStatement>\n'

    def compile_returnStatement(self):
        xml = '<returnStatement>\n' + self.compile_terminal('return')
        if self.next_token == ';':
            self.code += [
                "push constant 0",
                "return",
            ]
        else:
            xml += self.compile_expression()
        xml += self.compile_terminal(';')
        return xml + '</returnStatement>\n'

    def compile_letStatement(self):
        xml = '<letStatement>\n' + self.compile_terminal('let')
        varname = self.next_token
        xml += self.compile_terminal()
        if self.next_token != '=':
            xml += self.compile_terminal('[') + self.compile_expression() + \
                   self.compile_terminal(']')
        xml += self.compile_terminal('=') + self.compile_expression() + \
               self.compile_terminal(';')
        info = self.symbols.lookup(varname)
        if info['kind'] == 'field':
            segment = 'this'
        else:
            segment = info['kind']
        print(segment)
        self.code += ['pop {s} {o}'.format(s=segment, o=info['num'])]
        return xml + '</letStatement>\n'

    def compile_doStatement(self):
        xml = '<doStatement>\n' + self.compile_terminal('do') + \
              self.compile_subroutineCall() + \
              self.compile_terminal(';') + '</doStatement>\n'
        self.code += ['pop temp 0']
        return xml

    def compile_subroutineCall(self):
        name = self.next_token
        xml = self.compile_terminal()
        self.numexpressions = 0
        if self.next_token == '.':
            xml += self.compile_terminal('.')
            info = self.symbols.lookup(name)
            if info:
                code += ['push {v}'.format(v=name)]
                self.numexpressions += 1 # Is this right?
                vmname = info['type'] + '.' + self.next_token
            else:
                vmname = name + '.' + self.next_token
            xml += self.compile_terminal()
        else:
            vmname = self.symbols.get_class() + '.' + name
        xml += self.compile_terminal('(') + self.compile_expressionList() + \
               self.compile_terminal(')')
        self.code += ['call {v} {n}'.format(v=vmname,
                                            n=self.numexpressions)]
        return xml

    def compile_expressionList(self):
        if self.next_token == ')':
            return '<expressionList>\n</expressionList>\n'
        xml = '<expressionList>\n' + self.compile_expression()
        self.numexpressions += 1
        while self.next_token == ',':
            xml += self.compile_terminal() + self.compile_expression()
            self.numexpressions += 1
        return xml + '</expressionList>\n'

    def compile_expression(self):
        xml = '<expression>\n' + self.compile_term()
        while self.next_token in definitions.ops:
            op = self.next_token
            xml += self.compile_terminal() + self.compile_term()
            self.code += [definitions.ops[op]]
        return xml + '</expression>\n'

    def compile_term(self):
        xml = '<term>\n'
        if self.next_type in ['keyword', 'integerConstant', 'stringConstant']:
            if self.next_type == 'integerConstant':
                self.code += ['push constant {c}'.format(c=self.next_token)]
            xml += self.compile_terminal()
        elif self.next_token in ['~', '-']:
            # Notted/negated
            xml += self.compile_terminal() + self.compile_term()
        elif self.next_token == '(':
            # Parentheses
            xml += self.compile_terminal() + self.compile_expression() + \
                   self.compile_terminal(')')
        else:
            xml += self.compile_terminal()
            # Array handling
            if self.next_token == '[':
                xml += self.compile_terminal('[') + \
                       self.compile_expression() + self.compile_terminal(']')
            # Subroutine call
            elif self.next_token in ['.', '(']:
                xml += self.compile_subroutineCall()
        return xml + '</term>\n'


if __name__ == "__main__":
    parse(sys.argv[1])
