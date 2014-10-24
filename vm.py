"""Virtual machine translator for CSCI410 HW08."""

import os
import sys

import definitions

def translate(filename):
    with open(filename, "r") as f:
        code = [line.split('/')[0].strip()
                for line in (l.strip() for l in f.read().splitlines())
                if line and not line.startswith('/')]

        shortname = os.path.basename(filename)[:-len('.vm')]
        for c, line in enumerate(code):
            command, *args = line.split()
            if command in ['push', 'pop']:
                for translated_line in definitions.commands[command](args):
                    print(translated_line.format(id=shortname))
            else:
                for translated_line in definitions.commands[command]:
                    print(translated_line.format(id='_'.join([shortname, str(c)])))

if __name__ == "__main__":
    translate(sys.argv[1])
