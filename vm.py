"""Virtual machine translator for CSCI410 HW07.

"""

import os
import sys

import definitions

def translate(filename):
    with open(filename, "r") as f:
        code = [line.split('/')[0].strip()
                for line in (l.strip() for l in f.read().splitlines())
                if line and not line.startswith('/')]

        for c, line in enumerate(code):
            command, *args = line.split()
            if command in ['push', 'pop']:
                for translated_line in definitions.commands[command](args):
                    print(translated_line)
            else:
                for translated_line in definitions.commands[command]:
                    id = '_'.join([os.path.basename(filename)[:-len('.vm')], str(c)])
                    print(translated_line.format(id=id))

if __name__ == "__main__":
    translate(sys.argv[1])
