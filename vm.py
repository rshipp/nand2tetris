"""Virtual machine translator for CSCI410 HW07.

"""

import sys

import definitions

def translate(filename):
    with open(filename, "r") as f:
        code = [line.split('/')[0].strip()
                for line in (l.strip() for l in f.read().splitlines())
                if line and not line.startswith('/')]

        for line in code:
            command, *args = line.split()
            for translated_line in definitions.commands[command](args):
                print(translated_line)

if __name__ == "__main__":
    translate(sys.argv[1])
