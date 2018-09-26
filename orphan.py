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
    listenerSet = set([])
    callbackObjects = set([])

    try:
        f = open(fname, 'r')
    except:
        sys.stderr.write('Error opening file' + fname + '\n')
        exit(-1)

    prev = next(f)

    # Find all CallbackObject, it could be multiple CallbackObject points to the same mCallback.
    for l in f:
        if l == matchstr:
            callbackObjects.add(prev)
        prev = l

    # expect string like '0xa9e8b440 [rc=1] CallbackObject', try to find edge pattern '> 0xa9e8b440 mListeners event=onanimationend listenerType=3 [i]'
    if callbackObjects:
        # print 'There are ' + str(len(callbackObjects)) + ' CallbackObject.'
        for listenerString in callbackObjects:
            listenerAddr = ''
            nodePatt = re.compile ('([a-zA-Z0-9]+) \[(?:rc=[0-9]+|gc(?:.marked)?)\] (.*)$')
            nm = nodePatt.match(listenerString)
            if nm:
                # print 'found matched listener'
                listenerAddr = nm.group(1)
                listenerPatt = re.compile('^> %s mListeners (.*)$'%listenerAddr)
                # reset file pointer and iter again.
                f.seek(0)
                for l in f:
                    nmiter = listenerPatt.finditer(l)
                    if nmiter:
                        for m in nmiter:
                            # print 'found ' + m.group(1)
                            listenerSet.add(m.group(1))

    f.close()
    return listenerSet

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
            try:
                gAddr, explainRoot = g.find_roots.findGCRootsWithBlackOnly(addr)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                continue

        #print 'getting who holds that cc'
        print 'Explaining root : %s  ' % explainRoot

        if explainRoot == 'mCallback':
            # Find pattern like "> 0xaf048f70 mCallback", this leads us to find which event listener (usually named CallbackObject) is using mCallback.
            listeners = parseFile(sys.argv[1], '> %s mCallback\n'%gAddr)
            print 'There are ' + str(len(listeners)) + ' suspecting listener are: \n'
            print '---------------------------------------------'

            for listenerString in listeners:
                print ('\x1b[6;30;42m  ' + listenerString + '\x1b[0m')
            print '---------------------------------------------\n'
            print 'Please check these event listener(s) has been correctly removed.\n'
        if gAddr:
            cc.find_roots.findOrphanCCRoots(gAddr)
        print '######################## End #####################################'
        print
        print
else:
    sys.stderr.write('Expected log file name to start with cc or gc.\n')
