# pylint: disable=W0102
# pylint: disable=W0212
# pylint: disable=W0221
# pylint: disable=W0231
# pylint: disable=W0640
# pylint: disable=C0103
"""Module for containing representing UDS graphs"""

import json

from logging import info, warning
from functools import lru_cache
from memoized_property import memoized_property
from pyparsing import ParseException
from rdflib.plugins.sparql import prepareQuery
from networkx import adjacency_data, adjacency_graph
from .predpatt import PredPattCorpus
from ..rdf import RDFConverter

ROOT_QUERY = prepareQuery("""
                          SELECT ?n
                          WHERE { ?n <type> "root" .
                                }
                          """)
SYNTAX_NODES_QUERY = prepareQuery("""
                                  SELECT ?n
                                  WHERE { ?n <type> "syntax" .
                                        }
                                  """)

SEMANTICS_NODES_QUERY = prepareQuery("""
                                     SELECT ?n
                                     WHERE { ?n <type> "semantics" .
                                           }
                                     """)

PREDICATE_NODES_QUERY = prepareQuery("""
                                     SELECT ?n
                                     WHERE { ?n <type> "semantics" .
                                             ?n <subtype> "pred" .
                                           }
                                     """)

ARGUMENT_NODES_QUERY = prepareQuery("""
                                    SELECT ?n
                                    WHERE { ?n <type> "semantics" .
                                            ?n <subtype> "arg" .
                                          }
                                    """)


class UDSCorpus(PredPattCorpus):
    """Class for containing Universal Decompositional Semantics graphs

    Parameters
    ----------
    graphs : PredPattCorpus
    annotations : list(UDSAnnotation), optional
        the annotations to associate with predpatt nodes (defaults to [])
    """

    def __init__(self, graphs, annotations=[]):
        self._graphs = graphs
        self._annotations = annotations

        for ann in annotations:
            self.add_annotation(ann)

    def add_annotation(self, annotation):
        """Add annotations to UDS graphs

        Parameters
        ----------
        annotation : UDSAnnotation
        """

        for gname, (node_attrs, edge_attrs) in annotation.items():
            if gname in self._graphs:
                self._graphs[gname].add_annotation(node_attrs, edge_attrs)

    def to_json(self, fpath=None):
        """Serialize corpus to json

        Parameters
        ----------
        fpath : str, optional
            path to file to write corpus to

        Returns
        -------
        str
        """

        graphs_serializable = {name: graph.to_dict()
                               for name, graph in self.graphs.items()}

        if fpath is not None:
            with open(fpath, 'w') as f:
                json.dump(graphs_serializable, f)

        return json.dumps(graphs_serializable)

    # def to_mrs(self, fpath):
    #     """Serialize corpus to CoNLL-like MRS

    #     Parameters
    #     ----------
    #     fpath : str
    #         path to file to write corpus to
    #     """

    #     with open(fpath, 'w') as f:
    #         for name, graph in self.graphs.items():
    #             try:
    #                 mrs = graph.to_mrs()
    #             except ValueError:
    #                 warnmsg = 'could not write ' + name + ' to MRS'
    #                 warning(warnmsg)
    #                 continue

    #             if mrs:
    #                 f.write('# sent-id: '+name+'\n')
    #                 f.write('# sentence: '+graph.sentence+'\n')

    #                 for line in mrs:
    #                     f.write('\t'.join(line)+'\n')

    #                 f.write('\n')

    @classmethod
    def from_conll(cls, corpus_fpath, annotation_fpaths=[], name=None):
        """Load UDS graph corpus from conll (dependencies) and json (annotations)

        Parameters
        ----------
        corpus_fpath : str
            path to Universal Dependencies corpus in conllu format
        annotation_fpaths : list(str), optional
            path to annotations in json
        name : str, optional
            corpus name to be used in graph ids
        """

        predpatt_corpus = PredPattCorpus.from_conll(corpus_fpath, name=name)
        annotations = [UDSAnnotation.from_json(ann_fpath)
                       for ann_fpath in annotation_fpaths]

        return cls({name: UDSGraph(g, name)
                    for name, g in predpatt_corpus.items()},
                   annotations)

    @classmethod
    def from_json(cls, json_fpath=None, json_str=None):
        """Load UDS graph corpus from conll (dependencies) and json (annotations)

        Parameters
        ----------
        json_fpath : str, optional
            path to Universal Decompositional Semantics corpus in json format
        json_str : str, optional
            serialized json of  Universal Decompositional Semantics corpus
        """

        try:
            assert json_fpath is None or json_str is None
            assert json_fpath is not None or json_str is not None
        except AssertionError:
            errmsg = 'must pass one and only one of "json_str" or "fpath"'
            raise ValueError(errmsg)

        if json_str is not None:
            graphs_json = json.loads(json_str)
        elif json_fpath is not None:
            with open(json_fpath) as f:
                graphs_json = json.load(f)

        graphs = {name: UDSGraph.from_dict(g_json, name)
                  for name, g_json in graphs_json.items()}

        return cls(graphs)


class UDSGraph:
    """Class for representing Universal Decompositional Semantics graphs

    Parameters
    ----------
    graph : networkx.DiGraph
    name : str, optional

    Attributes
    ----------
    name : str
    graph : networkx.DiGraph
    rootid : str
    syntax_nodes : list(str)
    semantics_nodes : list(str)
    predicate_nodes : list(str)
    argument_nodes : list(str)
    syntax_subgraph : networkx.DiGraph
    semantics_subgraph : networkx.DiGraph
    """

    def __init__(self, graph, name='UDS'):
        self.name = name
        self.graph = graph

        self.nodes = self.graph.nodes
        self.edges = self.graph.edges

    @memoized_property
    def rdf(self):
        """The graph as RDF"""

        return RDFConverter.networkx_to_rdf(self.graph)

    @memoized_property
    def rootid(self):
        """The ID of the graph's root node"""
        return self.query(ROOT_QUERY)[0][0]

    @lru_cache(maxsize=128)
    def query(self, query):
        """Query graph using SPARQL 1.1 SELECT

        Parameters
        ----------
        query : str | rdflib.plugins.sparql.sparql.Query
            a SPARQL 1.1 SELECT query

        Returns
        -------
        list(tuple)
        """

        try:
            results = self.rdf.query(query)
        except ParseException:
            errmsg = 'invalid SPARQL 1.1 query'
            raise ValueError(errmsg)

        return [tuple([elem.toPython()
                       for elem in res])
                for res in results]

    def _node_query(self, query):
        results = [r[0] for r in self.query(query)]

        return {nodeid: self.nodes[nodeid] for nodeid in results}

    def _edge_query(self, query):
        return {edge: self.edges[edge] for edge in self.query(query)}

    @memoized_property
    def sentence(self):
        """The sentence the graph annotates"""

        return self.graph.nodes[self.rootid]['sentence']

    @memoized_property
    def syntax_nodes(self):
        """The syntax nodes in the graph"""

        return self._node_query(SYNTAX_NODES_QUERY)

    @memoized_property
    def semantics_nodes(self):
        """The semantics nodes in the graph"""

        return self._node_query(SEMANTICS_NODES_QUERY)

    @memoized_property
    def predicate_nodes(self):
        """The predicate (semantics) nodes in the graph"""

        return self._node_query(PREDICATE_NODES_QUERY)

    @memoized_property
    def argument_nodes(self):
        """The argument (semantics) nodes in the graph"""

        return self._node_query(ARGUMENT_NODES_QUERY)

    @lru_cache(maxsize=128)
    def semantics_edges(self, nodeid=None):
        """The edges between semantics nodes"""

        if nodeid is None:
            querystr = """
                       SELECT DISTINCT ?n1 ?n2
                       WHERE { ?n1 ?e ?n2 .
                               ?n1 <type> "semantics" .
                               ?n2 <type> "semantics" .
                             }
                       """
        else:
            querystr = '''
                       SELECT DISTINCT ?n1 ?n2
                       WHERE { ?n1 ?e ?n2 .
                               { ?n1 <id> ?id "'''+nodeid+'''" .
                               } UNION
                               { ?n2 <id> "'''+nodeid+'''" .
                               }
                               ?n1 <type> "semantics" .
                               ?n2 <type> "semantics" .
                             }
                       '''

        return self._edge_query(querystr)

    @lru_cache(maxsize=128)
    def syntax_edges(self, nodeid=None):
        """The edges between semantics nodes"""

        if nodeid is None:
            querystr = """
                       SELECT DISTINCT ?n1 ?n2
                       WHERE { ?n1 ?e ?n2 .
                               ?n1 <type> "syntax" .
                               ?n2 <type> "syntax" .
                             }
                       """
        else:
            querystr = '''
                       SELECT DISTINCT ?n1 ?n2
                       WHERE { ?n1 ?e ?n2 .
                               { ?n1 <id> "'''+nodeid+'''" .
                               } UNION
                               { ?n2 <id> "'''+nodeid+'''" .
                               }
                               ?n1 <type> "syntax" .
                               ?n2 <type> "syntax" .
                             }
                       '''

        return self._edge_query(querystr)

    @lru_cache(maxsize=128)
    def semantics_syntax_edges(self, nodeid=None):
        """The edges between syntax nodes and semantics nodes"""

        if nodeid is None:
            querystr = """
                       SELECT DISTINCT ?n1 ?n2
                       WHERE { ?n1 ?e ?n2 .
                               ?n1 <type> "semantics" .
                               ?n2 <type> "syntax" .
                             }
                       """
        else:
            querystr = '''
                       SELECT DISTINCT ?n1 ?n2
                       WHERE { ?n1 ?e ?n2 .
                               { ?n1 <id> "'''+nodeid+'''" .
                               } UNION
                               { ?n2 <id> "'''+nodeid+'''" .
                               }
                               ?n1 <type> "semantics" .
                               ?n2 <type> "syntax" .
                             }
                       '''

        return self._edge_query(querystr)

    @property
    def syntax_subgraph(self):
        """The part of the graph with only syntax nodes"""

        return self.graph.subgraph(list(self.syntax_nodes.keys()))

    @property
    def semantics_subgraph(self):
        """The part of the graph with only semantics nodes"""

        return self.graph.subgraph(list(self.semantics_nodes.keys()))

    def span(self, nodeid, attrs=['form']):
        """The span corresponding to a semantics node

        Parameters
        ----------
        nodeid : str
            the node identifier for a semantics node
        attrs : list(str)
            a list of syntax node attributes to return

        Returns
        -------
        dict(int, list)
            a mapping from positions in the span to the requested
            attributes in those positions
        """

        if self.nodes[nodeid]['type'] != 'semantics':
            errmsg = 'Only semantics nodes have (nontrivial) spans'
            raise ValueError(errmsg)

        return {self.nodes[e[1]]['position']: [self.nodes[e[1]][a]
                                               for a in attrs]
                for e in self.semantics_syntax_edges(nodeid)}

    def head(self, nodeid, attrs=['form']):
        """The head corresponding to a semantics node

        Parameters
        ----------
        nodeid : str
            the node identifier for a semantics node
        attrs : list(str)
            a list of syntax node attributes to return

        Returns
        -------
        tuple(int, list)
            a pairing of the head position and the requested
            attributes
        """

        if self.nodes[nodeid]['type'] != 'semantics':
            errmsg = 'Only semantics nodes have heads'
            raise ValueError(errmsg)

        return [(self.nodes[e[1]]['position'],
                 [self.nodes[e[1]][a] for a in attrs])
                for e, attr in self.semantics_syntax_edges(nodeid).items()
                if attr['instantiation'] == 'head'][0]

    # def to_mrs(self):
    #     """CoNLL-like MRS-formatted parse"""

    #     return MRSWriter(self).to_string()

    def to_dict(self):
        """Convert the graph to a dictionary"""

        return adjacency_data(self.graph)

    @classmethod
    def from_dict(cls, graph, name='UDS'):
        """Construct a UDSGraph from a dictionary

        graph : dict
            a dictionary constructed by networkx.adjacency_data
        name : str, optional
        """

        return cls(adjacency_graph(graph), name)

    def add_annotation(self, node_attrs, edge_attrs):
        """Add node and or edge annotations to the graph

        Parameters
        ----------
        node_attrs : dict(str, object)
        edge_attrs : dict(str, object)
        """

        for node, attrs in node_attrs.items():
            self._add_node_annotation(node, attrs)

        for edge, attrs in edge_attrs.items():
            self._add_edge_annotation(edge, attrs)

    def _add_node_annotation(self, node, attrs):
        if node in self.graph.nodes:
            self.graph.nodes[node].update(attrs)

        elif 'subargof' in attrs and attrs['subargof'] in self.graph.nodes:
            edge = (attrs['subargof'], node)

            infomsg = 'adding subarg edge ' + str(edge) + ' to ' + self.name
            info(infomsg)

            attrs = dict(attrs,
                         **{'type': 'semantics',
                            'subtype': 'arg',
                            'frompredpatt': 'false'})

            self.graph.add_node(node,
                                **{k: v
                                   for k, v in attrs.items()
                                   if k != 'subargof'})
            self.graph.add_edge(*edge, semrel='subarg')

            instedge = (node, node.replace('semantics-subarg', 'syntax'))
            self.graph.add_edge(*instedge, instantiation='head')

        elif 'subpredof' in attrs and attrs['subpredof'] in self.graph.nodes:
            edge = (attrs['subpredof'], node)

            infomsg = 'adding subpred edge ' + str(edge) + ' to ' + self.name
            info(infomsg)

            attrs = dict(attrs,
                         **{'type': 'semantics',
                            'subtype': 'pred',
                            'frompredpatt': 'false'})

            self.graph.add_node(node,
                                **{k: v
                                   for k, v in attrs.items()
                                   if k != 'subpredof'})

            self.graph.add_edge(*edge, semrel='subpred')

            instedge = (node, node.replace('semantics-subpred', 'syntax'))
            self.graph.add_edge(*instedge, instantiation='head')

        else:
            warnmsg = 'adding orphan node ' + node + ' in ' + self.name
            warning(warnmsg)

            attrs = dict(attrs,
                         **{'type': 'semantics',
                            'subtype': 'pred',
                            'frompredpatt': 'false'})

            self.graph.add_node(node,
                                **{k: v
                                   for k, v in attrs.items()
                                   if k != 'subpredof'})

            synnode = node.replace('semantics-pred', 'syntax')
            synnode = synnode.replace('semantics-arg', 'syntax')
            instedge = (node, synnode)
            self.graph.add_edge(*instedge, instantiation='head')

            if self.rootid is not None:
                self.graph.add_edge(self.rootid, node)

    def _add_edge_annotation(self, edge, attrs):
        if edge in self.graph.edges:
            self.graph.edges[edge].update(attrs)
        else:
            warnmsg = 'adding unlabeled edge ' + str(edge) + ' to ' + self.name
            warning(warnmsg)
            self.graph.add_edges_from([(edge[0], edge[1], attrs)])


class UDSAnnotation:
    """Class for representing Universal Decompositional Semantics annotation

    Parameters
    ----------
    annotation : dict(str, dict(str, object))
        mapping from node ids or pairs of node ids separated by _ to
        attribute-value pairs; node ids must not contain _
    """

    def __init__(self, annotation):
        self.annotation = annotation

        self.node_attributes = {gname: {node: a
                                        for node, a in attrs.items()
                                        if '_' not in node}
                                for gname, attrs in self.annotation.items()}

        self.edge_attributes = {gname: {tuple(edge.split('_')): a
                                        for edge, a in attrs.items()
                                        if '_' in edge}
                                for gname, attrs in self.annotation.items()}

    def __getitem__(self, k):
        node_attrs = self.node_attributes[k]
        edge_attrs = self.edge_attributes[k]

        return node_attrs, edge_attrs

    def items(self):
        """Dictionary-like items generator for attributes

        Yields node_attriutes for a node as well as the attributes for
        all edges that touch it
        """

        for name, node_attrs in self.node_attributes.items():
            yield name, (node_attrs, self.edge_attributes[name])

    @classmethod
    def from_json(cls, fname):
        """Load Universal Decompositional Semantics annotation from json

        Parameters
        ----------
        fname : str
            path to file containing annotation as json
        """

        with open(fname) as f:
            annotation = json.load(f)

        return cls(annotation)
