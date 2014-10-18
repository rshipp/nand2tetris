push_from_d = [
    '@SP',
    'A=M',
    'M=D',
    '@SP',
    'M=M+1',
]

pop_to_d = [
    '@SP',
    'M=M-1',
    'A=M',
    'D=M',
]

def push(args):
    if args[0] == 'constant':
        return [
            '@{n}'.format(n=args[1]),
            'D=A',
        ] + push_from_d
    elif args[1] == 'static':
        pass

def pop(args):
    return ['// pop not implemented.']

def eq(args):
    return ['// eq not implemented.']

def lt(args):
    return ['// lt not implemented.']

def gt(args):
    return ['// gt not implemented.']

def add(args):
    return pop_to_d + [
        '@SP',
        'M=M-1',
        'A=M',
        'D=D+M',
    ] + push_from_d

def sub(args):
    return ['// sub not implemented.']

def neg(args):
    return ['// neg not implemented.']

def and_(args):
    return ['// and not implemented.']

def or_(args):
    return ['// or not implemented.']

def not_(args):
    return ['// not not implemented.']

commands = {
    'push': push,
    'pop': pop,
    'eq': eq,
    'lt': lt,
    'gt': gt,
    'add': add,
    'sub': sub,
    'neg': neg,
    'and': and_,
    'or': or_,
    'not': not_,
}

