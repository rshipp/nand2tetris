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

pop_value_to_m = [
    '@SP',
    'AM=M-1',
]

pop_two = pop_value_to_m + [
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

return_ = [
    # FRAME = LCL
    '@LCL',
    'D=M',
    '@R13',
    'M=D',
    # RET = *(FRAME-5)
    '@5',
    'A=D-A',
    'D=M',
    '@R14',
    'M=D',
    # *ARG = pop()
    ] + pop_value_to_m + [
    'D=M',
    '@ARG',
    'A=M',
    'M=D',
    # SP = ARG+1
    '@ARG',
    'D=M+1',
    '@SP',
    'M=D',
    # THAT = *(FRAME-1)
    '@R13',
    'AM=M-1',
    'D=M',
    '@THAT',
    'M=D',
    # THIS = *(FRAME-2)
    '@R13',
    'AM=M-1',
    'D=M',
    '@THIS',
    'M=D',
    # ARG = *(FRAME-3)
    '@R13',
    'AM=M-1',
    'D=M',
    '@ARG',
    'M=D',
    # LCL = *(FRAME-4)
    '@R13',
    'AM=M-1',
    'D=M',
    '@LCL',
    'M=D',
    # goto RET
    '@R14',
    'A=M',
    '0;JMP',
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

def function(nlocals):
    if nlocals:
        return [
            '({id})',
            '@0',
            'D=A',
        ] + push_from_d * int(nlocals)
    else:
        return ['({id})']

def call(f, n):
    return [
        # push return-address
        '@{id}',
        'D=A',
    ] + push_from_d + [
        # push LCL
        '@LCL',
        'D=M',
    ] + push_from_d + [
        # push ARG
        '@ARG',
        'D=M',
    ] + push_from_d + [
        # push THIS
        '@THIS',
        'D=M',
    ] + push_from_d + [
        # push THAT
        '@THAT',
        'D=M',
    ] + push_from_d + [
        # ARG = SP-n-5
        '@{num}'.format(num=int(n)+5),
        'D=A',
        '@SP',
        'D=M-D',
        '@ARG',
        'M=D',
        # LCL = SP
        '@SP',
        'D=M',
        '@LCL',
        'M=D',
        # goto f
        '@{f}'.format(f=f),
        '0;JMP',
        # (return-address)
        '({id})',
    ]

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
    'label': ['({id})'],
    'if-goto': pop_value_to_m + ['D=M', '@{id}', 'D;JNE'],
    'goto': ['@{id}', '0;JMP'],
    'function': function,
    'return': return_,
    'call': call,
}

# Bootstrap code
bootstrap = [
    # SP=256
    '@256',
    'D=A',
    '@SP',
    'M=D',
    # call Sys.init
] + [l.format(id='BOOTSTRAP') for l in call('Sys.init', 0)]
