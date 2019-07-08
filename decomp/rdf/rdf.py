"""Module for converting from networkx to RDF"""

from networkx import to_dict_of_dicts
from rdflib import Graph, URIRef, Literal

class RDFConverter:

    NODES = {}
    EDGES = {}
    PROPERTIES = {}
    VALUES = {}

    def __init__(self, nxgraph):
        self.nxgraph = nxgraph
        self.rdfgraph = Graph()

    @classmethod
    def networkx_to_rdf(cls, nxgraph):
        converter = cls(nxgraph)

        nxdict = to_dict_of_dicts(nxgraph)

        for nodeid1, edgedict in nxdict.items():
            converter.add_node_attributes(nodeid1)

            for nodeid2, properties in edgedict.items():
                converter.add_node_attributes(nodeid2)
                converter.add_edge_attributes(nodeid1, nodeid2, properties)

        cls._reset_attributes()

        return converter.rdfgraph

    def add_node_attributes(self, nodeid):
        for propid, val in self.nxgraph.nodes[nodeid].items():
            triple = self.__class__._construct_property(nodeid, propid, val)
            self.rdfgraph.add(triple)

    def add_edge_attributes(self, nodeid1, nodeid2, properties):
        triple = self.__class__._construct_edge(nodeid1, nodeid2)
        self.rdfgraph.add(triple)

        edgeid = triple[1]

        for propid, val in properties.items():
            triple = self.__class__._construct_property(edgeid, propid, val)
            self.rdfgraph.add(triple)

    @classmethod
    def _construct_node(cls, nodeid):
        if nodeid not in cls.NODES:
            cls.NODES[nodeid] = URIRef(nodeid)

        return cls.NODES[nodeid]

    @classmethod
    def _construct_edge(cls, nodeid1, nodeid2):
        node1 = cls._construct_node(nodeid1)
        node2 = cls._construct_node(nodeid2)

        edgeid = nodeid1 + '%%' + nodeid2

        if edgeid not in cls.EDGES:
            cls.EDGES[edgeid] = URIRef(edgeid)

        return (node1, cls.EDGES[edgeid], node2)

    @classmethod
    def _construct_property(cls, nodeid, propid, val):
        if nodeid not in cls.NODES:
            cls.NODES[nodeid] = URIRef(nodeid)

        if propid not in cls.NODES:
            cls.PROPERTIES[propid] = URIRef(propid)

        if propid in ['type', 'subtype']:
            if val not in cls.VALUES:
                cls.VALUES[val] = URIRef(val)

            return (cls.NODES[nodeid],
                    cls.PROPERTIES[propid],
                    cls.VALUES[val])

        else:
            return (cls.NODES[nodeid],
                    cls.PROPERTIES[propid],
                    Literal(val))

    @classmethod
    def _reset_attributes(cls):
        cls.NODES = {}
        cls.EDGES = {}
