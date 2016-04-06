"""Assembler for Jack.

This design is pretty hackish, but it works, and has a few simple
optimizations built in. The design described in the book is far more complex
than it needs to be.

The assignment didn't specify how to do error handling, so I'm just raising
from a custom exception class - this could be extended later to be something
more useful.
"""

import sys

import tables

MAX_ACONST = 32767

class Error(Exception):
    pass

def assemble(filename):
    with open(filename, "r") as f:
        code = [line.split('/')[0].strip()
                for line in (l.strip() for l in f.read().splitlines())
                if line and not line.startswith('/')]

    # Pass 1
    count = 0
    for line in code:
        if line.startswith('('):
            tables.symbols[line.strip('()')] = count
        else:
            count = count + 1

    # Pass 2
    for line in code:
        if line.startswith('@'):
            print(assemble_a(line))
        elif line.startswith('('):
            continue
        else:
            print(assemble_c(line))

def assemble_a(line):
    def a_inst(value):
        return bin(int(value))[2:].zfill(16)

    value = line[1:]
    try:
        if int(value) <= MAX_ACONST and int(value) >= 0:
            return a_inst(value)
        else:
            raise Error('A-instruction used invalid const: {line}'.format(line=line))
    except ValueError:
        if value not in tables.symbols:
            tables.symbols[value] = tables.symbols[None]
            tables.symbols[None] = tables.symbols[None] + 1
        return a_inst(tables.symbols[value])

def assemble_c(line):
    try:
        dest, rest = line.split('=')
    except ValueError:
        dest, rest = 'null', line
    try:
        comp, jump = rest.split(';')
    except ValueError:
        comp, jump = rest, 'null'

    try:
        comp = tables.comp[comp]
        dest = tables.dest[dest]
        jump = tables.jump[jump]
    except KeyError:
        raise Error('Bad C-instruction: {line}'.format(line=line))

    return '111{comp}{dest}{jump}'.format(comp=comp,
                                          dest=dest.zfill(3),
                                          jump=jump.zfill(3))

if __name__ == "__main__":
    assemble(sys.argv[1])
