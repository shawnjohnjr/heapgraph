#!/usr/bin/python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import cc.find_roots
import cc.dom_grouper
import g.find_roots
import os

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
      print '--------------- Orphan node: %s ----------------------------' % x
      print 'orphan nodes:  %(label)s ' % {'label': x}
      addr = cc.find_roots.findOrphanCCRoots(x)
      print 'getting cc root address %s' % addr
      gAddr = g.find_roots.findGCRootsWithBlackOnly(addr)
      print 'getting who holds that cc'
      cc.find_roots.findOrphanCCRoots(gAddr)
      print '######################## End #####################################'
      print
      print
else:
    sys.stderr.write('Expected log file name to start with cc or gc.\n')
