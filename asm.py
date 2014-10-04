import sys

import tables

class Error(Exception):
    pass

def assemble(filename):
    with open(filename, "r") as f:
        code = [line for line in (l.strip() for l in f.read().split('\r\n'))
                if line and not line.startswith('/')]

    count = 0
    for line in code:
        #if line.startswith('('):
        #    tables.symbols[line.strip('()')] = count + 1

        if line.startswith('@'):
            print(assemble_a(line))
        elif line.startswith('('):
            tables.symbols[line.strip('()')] = count + 1
            continue
        else:
            print(assemble_c(line))

        count = count + 1

def assemble_a(line):
    value = line[1:]
    if int(value) <= 16384:
        return bin(int(line[1:]))[2:].zfill(16)
    else:
        raise Error('A-instruction constant was too big: {line}'.format(line=line))

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
