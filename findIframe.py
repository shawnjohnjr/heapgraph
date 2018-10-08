#!/usr/bin/python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import re
import cc.find_roots
import cc.dom_grouper
import g.find_roots
import os

def parseFile (fname):
    htmlIframes = set([])

    try:
        f = open(fname, 'r')
    except:
        sys.stderr.write('Error opening file' + fname + '\n')
        exit(-1)

    # Find all CallbackObject, it could be multiple CallbackObject points to the same mCallback.
    for l in f:
        nodePatt = re.compile ('([a-zA-Z0-9]+) \[(?:rc=[0-9]+|gc(?:.marked)?)\] JS Object \(HTMLIFrameElement\)$')
        nm = nodePatt.match(l)
        if nm:
           htmlIframes.add(nm.group(1))

    f.close()
    return htmlIframes

if len(sys.argv) < 2:
    sys.stderr.write('Expected at least one argument, the edge file name.\n')
    sys.exit(1)

# This is a top-level driver script for the GC and CC log find_roots
# scripts.  It just looks at the first two letters of the file name
# passed in as an argument.  If the file starts with 'cc', it assumes
# you must want the CC script.  If the file starts with 'gc', it
# assumes you must want the GC script.

baseFileName = os.path.basename(sys.argv[1])

if baseFileName.startswith('cc'):
    print '######################## Prepare to parse cc/gc log #####################################'
    print "Under this folder: " + os.getcwd() + "\n"
    print '######################## Begin #####################################'
    iframes = parseFile(baseFileName)

    for iframe in iframes:
        cc.find_roots.findOrphanCCRoots(iframe)

    print '######################## End #####################################'
    print
    print
else:
    sys.stderr.write('Expected log file name to start with cc or gc.\n')
