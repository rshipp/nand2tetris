push_from_d = [
    '@SP',
    'AM=M+1',
    'A=A-1',
    'M=D',
]

pop_to_m = [
    '@SP',
    'A=M-1',
]

pop_two = [
    '@SP',
    'AM=M-1',
    'D=M',
    'A=A-1',
]

compare = [
    'D=M-D',
    'M=-1',
    '@{op}END_{id}',
    'D;J{op}',
    '@SP',
    'A=M-1',
    'M=0',
    '({op}END_{id})',
]

def push(args):
    if args[0] == 'constant':
        return [
            '@{n}'.format(n=args[1]),
            'D=A',
        ] + push_from_d
    elif args[1] == 'static':
        return ['// push static not implemented']

def pop(args):
    return ['// pop not implemented.']

commands = {
    'push': push,
    'pop': pop,
    'eq': pop_two + [l.replace('{op}', 'EQ') for l in compare],
    'lt': pop_two + [l.replace('{op}', 'LT') for l in compare],
    'gt': pop_two + [l.replace('{op}', 'GT') for l in compare],
    'add': pop_two + ['M=M+D'],
    'sub': pop_two + ['M=M-D'],
    'neg': pop_to_m + ['M=-M'],
    'and': pop_two + ['M=M&D'],
    'or': pop_two + ['M=M|D'],
    'not': pop_to_m + ['M=!M'],
}
