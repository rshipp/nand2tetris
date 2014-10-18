"""Assembly language translations for the VM translator."""

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

segments = {
    'local': 'LCL',
    'argument': 'ARG',
    'this': 'THIS',
    'that': 'THAT',
}

d_setup = [
    '@{n}',
    'D=A',
]

push_setd = [
    'A=M+D',
    'D=M',
]

pop_setd = [
    'D=M+D',
]

d_to_m = [
    '@R13',
    'M=D',
    '@SP',
    'AM=M-1',
    'D=M',
    '@R13',
    'A=M',
    'M=D',
]

def push(args):
    if args[0] == 'constant':
        return [l.format(n=args[1]) for l in d_setup] + push_from_d
    elif args[0] in segments:
        return [l.format(n=args[1]) for l in d_setup] + [
            '@{type}'.format(type=segments[args[0]]),
        ] + push_setd + push_from_d
    elif args[0] == 'temp':
        return [l.format(n=args[1]) for l in d_setup] + [
            '@R5', # Temp0
            'A=A+D',
            'D=M',
        ] + push_from_d
    elif args[0] == 'static':
        id = '.'.join(['{id}', args[1]])
        return [l.format(n=id) for l in d_setup] + [
            'D=M'
        ] + push_from_d
    elif args[0] == 'pointer':
        return [
            '@{n}'.format(n=int(args[1])+3), # THIS or THAT
            'D=M',
        ] + push_from_d
    else:
        return ['// push {type} not implemented'.format(type=args[0])]

def pop(args):
    if args[0] in segments:
        return [l.format(n=args[1]) for l in d_setup] + [
            '@{type}'.format(type=segments[args[0]]),
        ] + pop_setd + d_to_m
    elif args[0] == 'temp':
        return [l.format(n=args[1]) for l in d_setup] + [
            '@R5', # Temp0
            'D=A+D',
        ] + d_to_m
    elif args[0] == 'static':
        return [
            '@SP',
            'AM=M-1',
            'D=M',
            '.'.join(['@{id}', args[1]]),
            'M=D',
        ]
    elif args[0] == 'pointer':
        return [
            '@SP',
            'AM=M-1',
            'D=M',
            '@{n}'.format(n=int(args[1])+3), # THIS or THAT
            'M=D',
        ]
    else:
        return ['// pop {type} not implemented'.format(type=args[0])]

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
