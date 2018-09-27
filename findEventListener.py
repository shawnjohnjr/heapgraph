#!/usr/bin/python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import re
import cc.find_roots
import g.find_roots
import os

#
# Usage: findEventListener.py cc-edges.208.1537574869.log 0xac5a4820
# Where 0xac5a4820 is the address of mCallback.
#
# 0xaab41220 [rc=1] CallbackObject
# > 0xac5a4820 mCallback
# > 0xac8530d0 mIncumbentJSGlobal
# > 0xab842800 mIncumbentGlobal
#
# Then the script will find that event listeners
# > 0xaab41220 mListeners event=ontimeformatchange listenerType=3 [i]
#

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

# Find pattern like "> 0xaf048f70 mCallback", this leads us to find which event listener (usually named CallbackObject) is using mCallback.
listeners = parseFile(sys.argv[1], '> %s mCallback\n'%sys.argv[2])
print 'There are ' + str(len(listeners)) + ' suspecting listener are: \n'
print '---------------------------------------------'

for listenerString in listeners:
    print ('\x1b[6;30;42m  ' + listenerString + '\x1b[0m')
print '---------------------------------------------\n'
print 'Please check these event listener(s) has been correctly removed.\n'
