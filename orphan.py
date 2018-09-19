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

def parseFile (fname, matchstr):
    listenerString = ''
    try:
        f = open(fname, 'r')
    except:
        sys.stderr.write('Error opening file' + fname + '\n')
        exit(-1)

    prev = next(f)

    for l in f:
        if l == matchstr:
            listenerString = prev
            break
        prev = l

    # expect string like '0xa9e8b440 [rc=1] CallbackObject', try to find edge pattern '> 0xa9e8b440 mListeners event=onanimationend listenerType=3 [i]'
    if listenerString != '':
        listenerAddr = ''
        nodePatt = re.compile ('([a-zA-Z0-9]+) \[(?:rc=[0-9]+|gc(?:.marked)?)\] (.*)$')
        nm = nodePatt.match(listenerString)
        if nm:
            listenerAddr = nm.group(1)
            listenerPatt = re.compile('^> %s mListeners (.*)$'%listenerAddr)
            for l in f:
                m = listenerPatt.match(l)
                if m:
                    listenerString = m.group(1)

    f.close()
    return listenerString

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
    orphans = cc.dom_grouper.parseFile(sys.argv[1])
    for x in orphans:
        print '######################## Begin #####################################'
        # print '--------------- Orphan node: %s ----------------------------' % x
        #print 'orphan nodes:  %(label)s ' % {'label': x}
        addr = cc.find_roots.findOrphanCCRoots(x)
        print 'getting cc root address %s' % addr
        if addr:
            gAddr, explainRoot = g.find_roots.findGCRootsWithBlackOnly(addr)
        print 'getting who holds that cc'
        print 'Explaining root : %s  ' % explainRoot

        if explainRoot == 'mCallback':
            print 'Suspecting listener is: \n'
            print '---------------------------------------------'
            print ('\x1b[6;30;42m  ' + parseFile(sys.argv[1], '> %s mCallback\n'%gAddr) + '\x1b[0m')
            print '---------------------------------------------\n'
            print 'Please check this event listener has been correctly removed\n'
        if gAddr:
            cc.find_roots.findOrphanCCRoots(gAddr)
        print '######################## End #####################################'
        print
        print
else:
    sys.stderr.write('Expected log file name to start with cc or gc.\n')
