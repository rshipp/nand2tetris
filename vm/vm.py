"""Virtual machine translator"""

import os
import sys

import definitions

def translate(filename):
    if os.path.isdir(filename):
        files = (os.path.join(filename, f) for f in os.listdir(filename) if f.endswith('.vm'))
    else:
        files = [filename]

    # Write bootstrap code
    for line in definitions.bootstrap:
        print(line)

    # Translate code
    for vmfile in files:
        with open(vmfile, "r") as f:
            code = [line.split('/')[0].strip()
                    for line in (l.strip() for l in f.read().splitlines())
                    if line and not line.startswith('/')]

            shortname = os.path.basename(vmfile)[:-len('.vm')]
            function = ''
            for c, line in enumerate(code):
                command, *args = line.split()
                if command in ['push', 'pop']:
                    for translated_line in definitions.commands[command](args):
                        print(translated_line.format(id=shortname))
                elif command in ['label', 'goto', 'if-goto']:
                    for translated_line in definitions.commands[command]:
                        print(translated_line.format(id='{fn}${lbl}'.format(fn=function, lbl=args[0])))
                elif command in ['function']:
                    function = args[0]
                    for translated_line in definitions.commands[command](args[1]):
                        print(translated_line.format(id=function))
                elif command in ['call']:
                    for translated_line in definitions.commands[command](args[0], args[1]):
                        print(translated_line.format(id='_'.join([function, str(c), 'RTN'])))
                else:
                    for translated_line in definitions.commands[command]:
                        print(translated_line.format(id='_'.join([shortname, str(c)])))

if __name__ == "__main__":
    translate(sys.argv[1])
