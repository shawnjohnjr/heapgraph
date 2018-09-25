#!/usr/bin/python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Find nsIMessageListener leakage

import sys
import cc.find_roots
import cc.parse_cc_graph

def find_messageListener(g, ga):
  js_holders = set([])

  for src, dsts in g.iteritems():
    if src in ga.rcNodes:
      for d in dsts:
        if d in ga.gcNodes:
          if ga.nodeLabels[src].startswith('nsXPCWrappedJS (nsIMessageListener)'):
              print 'Found ' + ga.nodeLabels[src] + ', Address: ' + src
              js_holders.add(src)
  return js_holders

def load_graph(fname):
  sys.stderr.write ('Parsing {0}. '.format(fname))
  sys.stderr.flush()
  (g, ga, res) = cc.parse_cc_graph.parseCCEdgeFile(fname)
  sys.stderr.write ('Done loading graph.\n')

  return (g, ga)

(g, ga) = load_graph (sys.argv[1])
holders = find_messageListener(g, ga)

for x in holders:
  print '######################## Begin #####################################'
  cc.find_roots.findOrphanCCRoots(x)
  print '######################## End #####################################'
  print
  print