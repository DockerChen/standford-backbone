#!/usr/bin/env python

# Requires graph_tool library: http://graph-tool.skewed.de/

from graph_tool.all import *

#asCount = 0
#relCount = 0
#nodes =  dict()
#asNames = g.new_vertex_property("string")
#relNames = g.new_edge_property("string")
#asFilters = g.new_vertex_property("bool")
inputFile = "./net.txt"
edges = set()
nodes = dict()

g = Graph(directed=False)
node_types = g.new_vertex_property("string")
node_names = g.new_vertex_property("string")
node_switch = g.new_vertex_property("bool")
edge_names = g.new_edge_property("string")


# Scan for nodes and edges
with open(inputFile) as f:
    for line in f:
        if line[0:1] == "h" or line[0:1] == "s":
            tokens = line.strip().split()
            # Add node
            v = g.add_vertex()
            nodes[tokens[0]] = v
            node_names[v] = tokens[0]
            if line[0:1] == "h":
                node_types[v] = "0.1"
                node_switch[v] = False
            elif line[0:4] == "s100":
                node_types[v] = "0.2"
                node_switch[v] = True
            else:
                node_types[v] = "0.9"
                node_switch[v] = True
            for token in tokens:
                if token.find(":") != -1 and token != "lo:":
                    ports = token.strip().split(":")
                    if ports[0] > ports[1]:
                        token = ports[1] + ":" + ports[0]
                    edges.add(token)

print "Found %d edges, %d nodes" % (len(edges), len(nodes))


# Create graph
for edge in edges:
	#print edge
	ports = edge.split(":")
	#print ports
	v1 = nodes[ports[0].split("-")[0]]
	v2 = nodes[ports[1].split("-")[0]]
	e = g.add_edge(v1, v2)
	edge_names[e] = edge

print g
'''
        tokens = line.rstrip().split('|')
        v1 = addAS(tokens[0])
        v2 = addAS(tokens[1])
        relCount += 1
        #if (relCount > 10000):
        #	break
        print "new relationship #" + str(relCount) + ": " + line
        e = g.add_edge(v1, v2)
        #relNames[e] = (int(tokens[2]) + 2) / 3
        if tokens[2] == "0":
        	# Peer
        	relNames[e] = "red"
        	print "red"
        else:
        	# Provider > Customer
        	relNames[e] = "blue"
        	print "blue"
        	'''
'''
# BFS
print "bfs"
bfs_search(g, nodes["1"], VisitorExample(asNames, asFilters))
'''
# Plot
print "draw"
g.set_vertex_filter(node_switch)
#g.set_vertex_filter(asFilters)
#pos = fruchterman_reingold_layout(g, n_iter=1000)
pos = arf_layout(g, max_iter=100)
graph_draw(g, pos=pos, vertex_text=node_names, vertex_color=node_types, edge_text=edge_names, vertex_font_size=25, output_size=(1000, 1000), output="net.png")
