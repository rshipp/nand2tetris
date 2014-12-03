"""Jack parser for CSCI410 HW10."""

import os
import sys

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
            tokens = (t for t in xmlhandler.parse(f.read()))
            shortname = os.path.basename(tfile)[:-len('T.xml')]

            # Parse.
            parser = Parser(tokens)
            xml = parser.compile_class()

            with open(''.join([shortname, '.xml']), "w") as t:
                t.write(xml)


class Parser:
    """Parses XML input from the tokenizer."""
    def __init__(self, tokens):
        """'tokens' should be a generator expression."""
        self.tokens = tokens
        next = self.tokens.next()
        self.next_token = next[1]
        self.next_type = next[0]

    def advance(self):
        try:
            next = self.tokens.next()
            self.next_token = next[1]
            self.next_type = next[0]
        except StopIteration:
            pass

    def compile_class(self):
        if self.next_token == 'class':
            return '<class>\n' + self.compile_terminal('class') + \
                   self.compile_terminal() + self.compile_terminal('{') + \
                   self.compile_classVarDec() + self.compile_subroutineDecs() + \
                   self.compile_terminal('}') + '</class>\n'

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
        return '<classVarDec>\n' + self.compile_terminal() + \
               self.compile_terminal() + self.compile_terminal() + \
               self.compile_varIdentifiers() + self.compile_terminal() + \
               '</classVarDec>\n' + self.compile_classVarDec()

    def compile_varDec(self):
        xml = '<varDec>\n' + self.compile_terminal('var') + \
               self.compile_terminal() + self.compile_terminal()
        while self.next_token == ',':
            xml += self.compile_terminal(',') + self.compile_terminal()
        return xml + self.compile_terminal(';') + '</varDec>\n'

    def compile_varIdentifiers(self):
        if self.next_token != ',':
            # Empty
            return ''
        # Non-empty
        return self.compile_terminal(',') + self.compile_terminal() + \
               self.compile_varIdentifiers()

    def compile_subroutineDecs(self):
        if not self.next_token in ['constructor', 'function', 'method']:
            # Empty
            return ''
        # Non-empty
        return '<subroutineDec>\n' + self.compile_terminal() + \
               self.compile_terminal() + self.compile_terminal() + \
               self.compile_terminal('(') + self.compile_parameterList() + \
               self.compile_terminal(')') + self.compile_subroutineBody() + \
               '</subroutineDec>\n' + self.compile_subroutineDecs()

    def compile_parameterList(self):
        if self.next_token == ')':
            # Empty
            return '<parameterList>\n</parameterList>\n'
        # Non-empty
        xml = '<parameterList>\n' + self.compile_terminal() + self.compile_terminal()
        while self.next_token == ',':
            xml += self.compile_terminal(',') + self.compile_terminal() + \
                   self.compile_terminal()
        return xml + '</parameterList>\n'

    def compile_subroutineBody(self):
        xml = '<subroutineBody>\n' + self.compile_terminal('{')
        while self.next_token == 'var':
            xml += self.compile_varDec()
        xml += self.compile_statements() + self.compile_terminal('}')
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
        if self.next_token != ';':
            xml += self.compile_expression()
        xml += self.compile_terminal(';')
        return xml + '</returnStatement>\n'

    def compile_letStatement(self):
        xml = '<letStatement>\n' + self.compile_terminal('let') + self.compile_terminal()
        if self.next_token != '=':
            xml += self.compile_terminal('[') + self.compile_expression() + \
                   self.compile_terminal(']')
        xml += self.compile_terminal('=') + self.compile_expression() + \
               self.compile_terminal(';')
        return xml + '</letStatement>\n'

    def compile_doStatement(self):
        return '<doStatement>\n' + self.compile_terminal('do') + \
               self.compile_terminal() + self.compile_subroutineCall() + \
               self.compile_terminal(';') + '</doStatement>\n'

    def compile_subroutineCall(self):
        xml = ''
        if self.next_token == '.':
            xml += self.compile_terminal('.') + self.compile_terminal()
        xml += self.compile_terminal('(') + self.compile_expressionList() + \
               self.compile_terminal(')')
        return xml

    def compile_expressionList(self):
        if self.next_token == ')':
            return '<expressionList>\n</expressionList>\n'
        xml = '<expressionList>\n' + self.compile_expression()
        while self.next_token == ',':
            xml += self.compile_terminal() + self.compile_expression()
        return xml + '</expressionList>\n'

    def compile_expression(self):
        xml = '<expression>\n' + self.compile_term()
        while self.next_token in definitions.expr_symbols:
            xml += self.compile_terminal() + self.compile_term()
        return xml + '</expression>\n'

    def compile_term(self):
        xml = '<term>\n'
        if self.next_type in ['keyword', 'integerConstant', 'stringConstant']:
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
