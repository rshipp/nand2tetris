"""Jack tokenizer for CSCI410 HW10."""

import cgi
import os
import sys
import shlex
import re

import definitions

def tokenize(data):
    code = (line.split('//')[0].strip()
            for line in (l.strip() for l in re.sub('/\*.*?\*/', '', data, flags=re.DOTALL).split('\n'))
            if line and not line.startswith('//'))

    xml = '<tokens>\n'
    for line in code:
        for token in shlex.shlex(line):
            xml += '<{type}> {token} </{type}>\n'.format(
                token=cgi.escape(token).replace('"', ''),
                type=definitions.type(token)
            )
    xml += '</tokens>\n'
    return xml

def main(filename):
    if os.path.isdir(filename):
        files = (os.path.join(filename, f) for f in os.listdir(filename) if f.endswith('.jack'))
    else:
        files = [filename]

    # Tokenize code.
    for jfile in files:
        with open(jfile, "r") as f:
            shortname = os.path.basename(jfile)[:-len('.jack')]
            xml = tokenize(f.read())
            with open(''.join([shortname, 'T.xml']), "w") as t:
                t.write(xml)

if __name__ == "__main__":
    main(sys.argv[1])
