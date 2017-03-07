# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 11:59:22 2015
@author: Ingo Scholtes

(c) Copyright ETH Zurich, Chair of Systems Design, 2015-2017
"""

import pathpy as pp
import numpy as _np

#########################
# TEST PATHWAY MODELING #
#########################

# Example without second-order correlations
paths = pp.Paths()

paths.addPath('a,c')
paths.addPath('b,c')
paths.addPath('c,d')
paths.addPath('c,e')

for k in range(3):
    paths.addPath('a,c,d')
    paths.addPath('b,c,e')
    paths.addPath('b,c,d')
    paths.addPath('a,c,e')

m = pp.MultiOrderModel(paths, maxOrder=2)
assert m.estimateOrder(paths) == 1, "Error, wrongly detected higher-order correlations"

# Example with second-order correlations
paths = pp.Paths()

paths.addPath('a,c')
paths.addPath('b,c')
paths.addPath('c,d')
paths.addPath('c,e')

for k in range(3):
    paths.addPath('a,c,d')
    paths.addPath('b,c,e')   

m = pp.MultiOrderModel(paths, maxOrder=2)
assert m.estimateOrder(paths) == 2, "Error, did not detect second-order correlations"

x = list(map(str, _np.random.choice(range(10), 100000)))
ms = pp.MarkovSequence(x)
assert ms.estimateOrder(maxOrder=2, method='BIC') == 1, "Error, wrongly detected higher-order correlations"
assert ms.estimateOrder(maxOrder=2, method='AIC') == 1, "Error, wrongly detected higher-order correlations"

g1 = pp.HigherOrderNetwork(paths, k=1)
print(g1)
assert g1.vcount() == 5, "Error, wrong number of nodes in first-order network"
assert g1.ecount() == 4, "Error, wrong number of links in first-order network"

g2 = pp.HigherOrderNetwork(paths, k=2)
print(g2)
assert g2.vcount() == 4, "Error, wrong number of nodes in second-order network"
assert g2.ecount() == 2, "Error, wrong number of links in second-order network"

g2.reduceToGCC()

print(g2)
assert g2.vcount() == 1, "Error, wrong number of nodes in giant connected component"
assert g2.ecount() == 0, "Error, wrong number of links in giant connected component"


# Example with single strongly connected component in first- and two connected components in second-order network
paths = pp.Paths()

paths.addPath('a,b,c')
paths.addPath('b,c,b')
paths.addPath('c,b,a')
paths.addPath('b,a,b')

paths.addPath('e,b,f')
paths.addPath('b,f,b')
paths.addPath('f,b,e')
paths.addPath('b,e,b')

g1 = pp.HigherOrderNetwork(paths, k=1)
print(g1)
g1.reduceToGCC()
assert g1.vcount() == 5, "Error, wrong number of nodes in first-order network"
assert g1.ecount() == 8, "Error, wrong number of links in first-order network"

g2 = pp.HigherOrderNetwork(paths, k=2)
print(g2)
g2.reduceToGCC()
assert g2.vcount() == 4, "Error, wrong number of nodes in second-order network"
assert g2.ecount() == 4, "Error, wrong number of links in second-order network"

# test mapping of higher-order nodes and paths 
assert g2.HigherOrderNodeToPath('a-b') == ('a', 'b'), "Error: mapping from higher-order node to first-order path failed"
assert g2.HigherOrderPathToFirstOrder(('a-b', 'b-c')) == ('a', 'b', 'c'), "Error: mapping from higher-order path to first-order path failed"

# test PageRank
g2.PageRank() 


#########################
# TEST TEMPORAL NETWORK #
#########################

t = pp.TemporalNetwork()
# Path of length two
t.addEdge("c", "e", 1)
t.addEdge("e", "f", 2)

# Path of length two
t.addEdge("a", "e", 3)
t.addEdge("e", "g", 4)

# Path of length two
t.addEdge("c", "e", 5)
t.addEdge("e", "f", 6)

# Path of length two
t.addEdge("a", "e", 7)
t.addEdge("e", "g", 8)

# Path of length two
t.addEdge("c", "e", 9)
t.addEdge("e", "f", 10)

# The next two edges continue the previous path to ( c-> e-> f-> e -> b )
t.addEdge("f", "e", 11)
t.addEdge("e", "b", 12)

# This is an isolated edge (i.e. path of length one)
t.addEdge("e", "b", 13)

# Path of length two
t.addEdge("c", "e", 14)
t.addEdge("e", "f", 15)

# Path of length two
t.addEdge("b", "e", 16)
t.addEdge("e", "g", 17)

# Path of length two
t.addEdge("c", "e", 18)
t.addEdge("e", "f", 19)

# Path of length two
t.addEdge("c", "e", 20)
t.addEdge("e", "f", 21)

# Extract (time-respecting) paths
paths = pp.Paths.fromTemporalNetwork(t, delta=1)
print(paths)

print("Test network has", paths.ObservationCount(), "(longest) time-respecting paths")
assert paths.ObservationCount() == 10, "Extracted wrong number of time-respecting paths"
assert paths.BetweennessPreference('e') == 1.2954618442383219


############################
# TEST DAG PATH EXTRACTION #
############################

dag = pp.DAG()
dag.addEdge('a', 'b')
dag.addEdge('a', 'c')
dag.addEdge('c', 'b')
dag.addEdge('b', 'e')
dag.addEdge('b', 'f')
dag.addEdge('f', 'g')
dag.addEdge('c', 'g')

dag.addEdge('h', 'i')
dag.addEdge('h', 'j')

dag.topsort()


# For this DAG, the following five paths between the root and the leaves exist: 
#   h -> i                  ( A -> B )
#   h -> j                  ( A -> A )
#   a -> b -> e             ( A -> B -> B )
#   a -> c -> g             ( A -> A -> A )
#   a -> b -> f -> g        ( A -> B -> B -> A )
#   a -> c -> b -> e        ( A -> A -> B -> B )
#   a -> c -> b -> f -> g   ( A -> A -> B -> B -> A )

assert dag.isAcyclic==True, 'Error: Wrongly detected cycle in DAG'

# Extract paths between nodes in DAG
paths = pp.Paths.fromDAG(dag)
assert paths.ObservationCount() == 7, 'Error: wrong number of paths in DAG'

# project paths based on node mapping
mapping = {'a': 'A', 'b': 'B', 'c': 'A', 'e': 'B', 'f': 'B', 'g': 'A', 'h': 'A','i': 'B', 'j': 'A' }
paths_mapped1 = paths.projectPaths(mapping)

# directly extract mapped paths
paths_mapped2 = pp.Paths.fromDAG(dag, node_mapping = mapping)
assert paths_mapped2.ObservationCount() == 7, 'Error: wrong number of paths in DAG'

# Add a cycle to the graph
dag.addEdge('b', 'c')
dag.topsort()
assert dag.edge_classes[('b', 'c')] == 'back' or dag.edge_classes[('c', 'b')] == 'back', 'Error: Did not detect back link'
assert dag.isAcyclic == False, 'Error: Did not detect cycle'

dag.makeAcyclic()
assert ('b', 'c') not in dag.edges or ('c', 'b') not in dag.edges, 'Error: did not remove correct link'
assert len(dag.edges) == 9, 'Error: makeAcyclic generated wrong number of links'
