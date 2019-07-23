# pylint: disable=W0102
# pylint: disable=W0212
# pylint: disable=W0221
# pylint: disable=W0231
# pylint: disable=W0640
# pylint: disable=C0103
"""Module for containing representing UDS graphs"""

import os
import json
import requests

from pkg_resources import resource_filename
from os.path import basename, splitext
from glob import glob
from logging import info, warning
from functools import lru_cache
from typing import Union, Optional, Dict, List, Tuple, Any, TextIO
from io import BytesIO
from zipfile import ZipFile
from memoized_property import memoized_property
from pyparsing import ParseException
from rdflib import Graph
from rdflib.query import Result
from rdflib.plugins.sparql.sparql import Query
from rdflib.plugins.sparql import prepareQuery
from networkx import DiGraph, adjacency_data, adjacency_graph
from .predpatt import PredPattCorpus
from ..graph import RDFConverter

ROOT_QUERY = prepareQuery("""
                          SELECT ?n
                          WHERE { ?n <type> <root> .
                                }
                          """)

SYNTAX_NODES_QUERY = prepareQuery("""
                                  SELECT ?n
                                  WHERE { ?n <domain> <syntax> .
                                          ?n <type> <token> .
                                        }
                                  """)

SEMANTICS_NODES_QUERY = prepareQuery("""
                                     SELECT ?n
                                     WHERE { ?n <domain> <semantics> .
                                             { ?n <type> <predicate> .
                                             } UNION
                                             { ?n <type> <argument> .
                                             }
                                           }
                                     """)

PREDICATE_NODES_QUERY = prepareQuery("""
                                     SELECT ?n
                                     WHERE { ?n <domain> <semantics> .
                                             ?n <type> <predicate> .
                                           }
                                     """)

ARGUMENT_NODES_QUERY = prepareQuery("""
                                    SELECT ?n
                                    WHERE { ?n <domain> <semantics> .
                                            ?n <type> <argument> .
                                          }
                                    """)

SEMANTICS_EDGES_DEFAULT_QUERY = prepareQuery("""
                                             SELECT ?e
                                             WHERE { ?e <domain> <semantics> .
                                                   { ?e <type> <dependency> .
                                                   } UNION
                                                   { ?e <type> <head> .
                                                   }
                                                   }
                                             """)

ARGUMENT_EDGES_DEFAULT_QUERY = prepareQuery("""
                                            SELECT ?e
                                            WHERE { ?n1 ?e ?n2 .
                                                    ?e <domain> <semantics> .
                                                    ?e <type> <dependency> .
                                                  }
                                            """)

ARGUMENT_HEAD_EDGES_DEFAULT_QUERY = prepareQuery("""
                                             SELECT ?e
                                             WHERE { ?n1 ?e ?n2 .
                                                     ?e <domain> <semantics> .
                                                     ?e <type> <head> .
                                                   }
                                                 """)

SYNTAX_EDGES_DEFAULT_QUERY = prepareQuery("""
                                          SELECT ?e
                                          WHERE { ?e <domain> <syntax> .
                                                  ?e <type> <dependency> .
                                                }
                                          """)


class UDSCorpus(PredPattCorpus):
    """Container for collection of Universal Decompositional Semantics graphs

    Parameters
    ----------
    graphs
        the predpatt graphs to associate the annotations with
    annotations
        additional annotations to associate with predpatt nodes; in
        most cases, no such annotations will be passed, since the
        standard UDS annotations are automatically loaded
    splitname
        the split to load: "train", "dev", or "test"
    """

    DATA_DIR = resource_filename('decomp', 'data/')

    CORPUS_PATHS = {splitext(basename(p))[0].split('-')[-1]: p
                    for p in glob(os.path.join(DATA_DIR, '*.json'))}

    ANNOTATION_DIR = os.path.join(DATA_DIR, 'annotations/')
    ANNOTATION_PATHS = glob(os.path.join(ANNOTATION_DIR, '*.json'))

    def __init__(self,
                 graphs: Optional[PredPattCorpus] = None,
                 annotations: List['UDSAnnotation'] = [],
                 splitname: Optional[str] = None):

        if not (splitname is None or splitname in ['train', 'dev', 'test']):
            errmsg = 'splitname must be "train", "dev", or "test"'
            raise ValueError(errmsg)

        if graphs is None and self.__class__.CORPUS_PATHS:
            self._graphs = {}

            if splitname is not None:
                fpath = self.__class__.CORPUS_PATHS[splitname]
                corp_split = self.__class__.from_json(fpath)
                self._graphs.update(corp_split._graphs)

            else:
                for fpath in self.__class__.CORPUS_PATHS.values():
                    corp_split = self.__class__.from_json(fpath)
                    self._graphs.update(corp_split._graphs)

        elif graphs is None:
            url = 'https://github.com/UniversalDependencies/' +\
                  'UD_English-EWT/archive/r1.2.zip'

            udewt = requests.get(url).content

            self._graphs = {}

            annpaths = self.__class__.ANNOTATION_PATHS

            with ZipFile(BytesIO(udewt)) as zf:
                conll_names = [fname for fname in zf.namelist()
                               if splitext(fname)[-1] == '.conllu']

                for fn in conll_names:
                    with zf.open(fn) as conll:
                        conll_str = conll.read().decode('utf-8')
                        sname = splitext(basename(fn))[0].split('-')[-1]
                        spl = self.__class__.from_conll(conll_str,
                                                        annpaths,
                                                        name='ewt-'+sname)

                        # in case additional annotations are passed;
                        # this should generally NOT happen, since this
                        # branch is only entered on first build, but
                        # if someone imported this class directly from
                        # the semantics module without first building
                        # the dataset, they could in principle try to
                        # pass annotations, so we want to do something
                        # reasonable here
                        for ann in annotations:
                            spl.add_annotation(ann)

                        if sname == splitname or splitname is None:
                            json_name = 'uds-ewt-'+sname+'.json'
                            json_path = os.path.join(self.__class__.DATA_DIR,
                                                     json_name)
                            spl.to_json(json_path)
                            self._graphs.update(spl._graphs)

                            self.__class__.CORPUS_PATHS[sname] = json_path

        else:
            self._graphs = graphs

            for ann in annotations:
                self.add_annotation(ann)

    @classmethod
    def from_conll(cls,
                   corpus: Union[str, TextIO],
                   annotations: List[Union[str, TextIO]] = [],
                   name: str = None) -> 'UDSCorpus':
        """Load UDS graph corpus from CoNLL (dependencies) and JSON (annotations)

        This method should only be used if the UDS corpus is being
        (re)built. Otherwise, loading the corpus from the JSON shipped
        with this package using UDSCorpus.from_json is suggested.

        Parameters
        ----------
        corpus
            (path to) Universal Dependencies corpus in conllu format
        annotations
            (paths to) annotations in JSON; in most cases, no such
            paths/annotations will be passed, since the standard UDS
            annotations are automatically loaded
        name
            corpus name to be appended to the beginning of graph ids
        """

        predpatt_corpus = PredPattCorpus.from_conll(corpus, name=name)
        predpatt_graphs = {name: UDSGraph(g, name)
                           for name, g in predpatt_corpus.items()}

        annotations = [UDSAnnotation.from_json(ann) for ann in annotations]

        return cls(predpatt_graphs, annotations)

    @classmethod
    def from_json(cls, jsonfile: Union[str, TextIO]) -> 'UDSCorpus':
        """Load annotated UDS graph corpus (including annotations) from JSON

        This is the suggested method for loading the UDS corpus.

        Parameters
        ----------
        jsonfile
            file containing Universal Decompositional Semantics corpus
            in JSON format
        """

        ext = splitext(basename(jsonfile))[-1]

        if isinstance(jsonfile, str) and ext == '.json':
            with open(jsonfile) as infile:
                graphs_json = json.load(infile)

        elif isinstance(jsonfile, str):
            graphs_json = json.loads(jsonfile)

        else:
            graphs_json = json.load(jsonfile)

        graphs = {name: UDSGraph.from_dict(g_json, name)
                  for name, g_json in graphs_json.items()}

        return cls(graphs)

    def add_annotation(self, annotation: 'UDSAnnotation') -> None:
        """Add annotations to UDS graphs in the corpus

        Parameters
        ----------
        annotation
            the annotations to add to the graphs in the corpus
        """

        for gname, (node_attrs, edge_attrs) in annotation.items():
            if gname in self._graphs:
                self._graphs[gname].add_annotation(node_attrs, edge_attrs)

    def to_json(self,
                outfile: Optional[Union[str, TextIO]] = None) -> Optional[str]:
        """Serialize corpus to json

        Parameters
        ----------
        outfile
            file to write corpus to
        """

        graphs_serializable = {name: graph.to_dict()
                               for name, graph in self.graphs.items()}

        if outfile is None:
            return json.dumps(graphs_serializable)

        elif isinstance(outfile, str):
            with open(outfile, 'w') as out:
                json.dump(graphs_serializable, out)

        else:
            json.dump(graphs_serializable, outfile)

    @memoized_property
    def node_attribute_names(self):
        """The union of node attributes in the corpus"""

        return set([k
                    for g in self._graphs.values()
                    for nid, attrs in g.semantics_nodes.items()
                    for k, v in attrs.items()
                    if isinstance(v, float)])

    @memoized_property
    def edge_attribute_names(self):
        """The union of edge attributes in the corpus"""

        return set([k
                    for g in self._graphs.values()
                    for _, attrs in g.semantics_edges().items()
                    for k, v in attrs.items()
                    if isinstance(v, float)])

    @memoized_property
    def attribute_names(self):
        """The union of edge attributes in the corpus"""

        return self.node_attribute_names | self.edge_attribute_names


class UDSGraph:
    """Class for representing Universal Decompositional Semantics graphs

    Parameters
    ----------
    graph
    name
    """

    def __init__(self, graph: DiGraph, name: str):
        self.name = name
        self.graph = graph

        #self.graph._add_performative_nodes()

        self.nodes = self.graph.nodes
        self.edges = self.graph.edges

    @memoized_property
    def rdf(self) -> Graph:
        """The graph as RDF"""

        return RDFConverter.networkx_to_rdf(self.graph)

    @memoized_property
    def rootid(self):
        """The ID of the graph's root node"""

        return list(self.query(ROOT_QUERY))[0][0].toPython()

    def _add_performative_nodes(self):
        self.graph.add_node(self.graph.name+'-semantics-arg')

    @lru_cache(maxsize=128)
    def query(self, query: Union[str, Query]) -> Result:
        """Query graph using SPARQL 1.1 SELECT

        Parameters
        ----------
        query
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

        return results

    def _node_query(self, query: Union[str, Query]) -> Dict[str,
                                                            Dict[str, Any]]:

        results = [r[0].toPython() for r in self.query(query)]

        return {nodeid: self.nodes[nodeid] for nodeid in results}

    def _edge_query(self, query: Union[str, Query]) -> Dict[Tuple[str, str],
                                                            Dict[str, Any]]:

        results = [tuple(edge[0].toPython().split('%%'))
                   for edge in self.query(query)]

        return {edge: self.edges[edge]
                for edge in results}

    @memoized_property
    def sentence(self) -> str:
        """The sentence the graph annotates"""

        return self.graph.nodes[self.rootid]['sentence']

    @memoized_property
    def syntax_nodes(self) -> Dict[str, Dict[str, Any]]:
        """The syntax nodes in the graph"""

        return self._node_query(SYNTAX_NODES_QUERY)

    @memoized_property
    def semantics_nodes(self) -> Dict[str, Dict[str, Any]]:
        """The semantics nodes in the graph"""

        return self._node_query(SEMANTICS_NODES_QUERY)

    @memoized_property
    def predicate_nodes(self) -> Dict[str, Dict[str, Any]]:
        """The predicate (semantics) nodes in the graph"""

        return self._node_query(PREDICATE_NODES_QUERY)

    @memoized_property
    def argument_nodes(self) -> Dict[str, Dict[str, Any]]:
        """The argument (semantics) nodes in the graph"""

        return self._node_query(ARGUMENT_NODES_QUERY)

    @memoized_property
    def syntax_subgraph(self) -> DiGraph:
        """The part of the graph with only syntax nodes"""

        return self.graph.subgraph(list(self.syntax_nodes))

    @memoized_property
    def semantics_subgraph(self) -> DiGraph:
        """The part of the graph with only semantics nodes"""

        return self.graph.subgraph(list(self.semantics_nodes))

    @lru_cache(maxsize=128)
    def semantics_edges(self,
                        nodeid: Optional[str] = None) -> Dict[Tuple[str, str],
                                                              Dict[str, Any]]:
        """The edges between semantics nodes"""

        if nodeid is None:
            querystr = SEMANTICS_EDGES_DEFAULT_QUERY

        else:
            querystr = """
                       SELECT ?e
                       WHERE { { <"""+nodeid+"""> ?e ?n1 .
                               } UNION
                               { ?n1 ?e <"""+nodeid+"""> .
                               }
                               ?e <domain> <semantics> .
                               { ?e <type> <dependency> .
                               } UNION
                               { ?e <type> <head> .
                               }
                             }
                       """

        return self._edge_query(querystr)

    @lru_cache(maxsize=128)
    def argument_edges(self,
                       nodeid: Optional[str] = None) -> Dict[Tuple[str, str],
                                                             Dict[str, Any]]:
        """The edges between predicates and their arguments"""

        if nodeid is None:
            querystr = ARGUMENT_EDGES_DEFAULT_QUERY

        else:
            querystr = """
                       SELECT ?e
                       WHERE { { <"""+nodeid+"""> ?e ?n1 .
                               } UNION
                               { ?n1 ?e <"""+nodeid+"""> .
                               }
                               ?e <domain> <semantics> .
                               ?e <type> <dependency> .
                             }
                       """

        return self._edge_query(querystr)

    @lru_cache(maxsize=128)
    def argument_head_edges(self,
                            nodeid: Optional[str] = None) -> Dict[Tuple[str,
                                                                        str],
                                                                  Dict[str,
                                                                       Any]]:
        """The edges between nodes and their semantic heads"""

        if nodeid is None:
            querystr = ARGUMENT_HEAD_EDGES_DEFAULT_QUERY

        else:
            querystr = """
                       SELECT ?e
                       WHERE { { <"""+nodeid+"""> ?e ?n1 .
                               } UNION
                               { ?n1 ?e <"""+nodeid+"""> .
                               }
                               ?e <domain> <semantics> .
                               ?e <type> <head> .
                             }
                       """

        return self._edge_query(querystr)

    @lru_cache(maxsize=128)
    def syntax_edges(self,
                     nodeid: Optional[str] = None) -> Dict[Tuple[str, str],
                                                           Dict[str, Any]]:
        """The edges between syntax nodes"""

        if nodeid is None:
            querystr = SYNTAX_EDGES_DEFAULT_QUERY

        else:
            querystr = """
                       SELECT ?e
                       WHERE { { <"""+nodeid+"""> ?e ?n1 .
                               } UNION
                               { ?n1 ?e <"""+nodeid+"""> .
                               }
                               ?e <domain> <syntax> .
                               ?e <type> <dependency> .
                             }
                       """

        return self._edge_query(querystr)

    @lru_cache(maxsize=128)
    def instance_edges(self,
                       nodeid: Optional[str] = None) -> Dict[Tuple[str, str],
                                                             Dict[str, Any]]:
        """The edges between syntax nodes and semantics nodes"""

        if nodeid is None:
            querystr = """
                       SELECT DISTINCT ?e
                       WHERE { ?n1 ?e ?n2 .
                               ?e <domain> <interface> .
                             }
                       """

        else:
            querystr = """
                       SELECT ?e
                       WHERE { { <"""+nodeid+"""> ?e ?n1 .
                               } UNION
                               { ?n1 ?e <"""+nodeid+"""> .
                               }
                               ?e <domain> <interface> .
                             }
                       """

        return self._edge_query(querystr)

    def span(self,
             nodeid: str,
             attrs: List[str] = ['form']) -> Dict[int, List[Any]]:
        """The span corresponding to a semantics node

        Parameters
        ----------
        nodeid
            the node identifier for a semantics node
        attrs
            a list of syntax node attributes to return

        Returns
        -------
        a mapping from positions in the span to the requested
        attributes in those positions
        """

        if self.nodes[nodeid]['domain'] != 'semantics':
            errmsg = 'Only semantics nodes have (nontrivial) spans'
            raise ValueError(errmsg)

        return {self.nodes[e[1]]['position']: [self.nodes[e[1]][a]
                                               for a in attrs]
                for e in self.instance_edges(nodeid)}

    def head(self,
             nodeid: str,
             attrs: List[str] = ['form']) -> Tuple[int, List[Any]]:
        """The head corresponding to a semantics node

        Parameters
        ----------
        nodeid
            the node identifier for a semantics node
        attrs
            a list of syntax node attributes to return

        Returns
        -------
        a pairing of the head position and the requested
        attributes
        """

        if self.nodes[nodeid]['domain'] != 'semantics':
            errmsg = 'Only semantics nodes have heads'
            raise ValueError(errmsg)

        return [(self.nodes[e[1]]['position'],
                 [self.nodes[e[1]][a] for a in attrs])
                for e, attr in self.instance_edges(nodeid).items()
                if attr['type'] == 'head'][0]

    def maxima(self, nodeids: Optional[List[str]] = None) -> List[str]:
        """The nodes in nodeids not dominated by any other nodes in nodeids"""

        if nodeids is None:
            nodeids = self.nodes

        return [nid for nid in nodeids
                if all(e[0] == nid
                       for e in self.edges
                       if e[0] in nodeids
                       if e[1] in nodeids
                       if nid in e)]

    def minima(self, nodeids: Optional[List[str]] = None) -> List[str]:
        """The nodes in nodeids not dominating any other nodes in nodeids"""

        if nodeids is None:
            nodeids = self.nodes

        return [nid for nid in nodeids
                if all(e[0] != nid
                       for e in self.edges
                       if e[0] in nodeids
                       if e[1] in nodeids
                       if nid in e)]

    def to_dict(self) -> Dict:
        """Convert the graph to a dictionary"""

        return adjacency_data(self.graph)

    @classmethod
    def from_dict(cls, graph: Dict, name: str = 'UDS') -> 'UDSGraph':
        """Construct a UDSGraph from a dictionary

        Parameters
        ----------
        graph
            a dictionary constructed by networkx.adjacency_data
        name
            identifier to append to the beginning of node ids
        """

        return cls(adjacency_graph(graph), name)

    def add_annotation(self,
                       node_attrs: Dict[str, Dict[str, Any]],
                       edge_attrs: Dict[str, Dict[str, Any]],
                       add_heads: bool = True,
                       add_subargs: bool = False,
                       add_subpreds: bool = False,
                       add_orphans: bool = False) -> None:
        """Add node and or edge annotations to the graph

        Parameters
        ----------
        node_attrs
        edge_attrs
        add_heads
        add_subargs
        add_subpreds
        add_orphans
        """

        for node, attrs in node_attrs.items():
            self._add_node_annotation(node, attrs,
                                      add_heads, add_subargs,
                                      add_subpreds, add_orphans)

        for edge, attrs in edge_attrs.items():
            self._add_edge_annotation(edge, attrs)

    def _add_node_annotation(self, node, attrs,
                             add_heads, add_subargs,
                             add_subpreds, add_orphans):
        if node in self.graph.nodes:
            self.graph.nodes[node].update(attrs)

        elif 'headof' in attrs and attrs['headof'] in self.graph.nodes:
            edge = (attrs['headof'], node)

            if not add_heads:
                infomsg = 'head edge ' + str(edge) + ' in ' + self.name +\
                          ' found in annotations but not added'
                info(infomsg)

            else:
                infomsg = 'adding head edge ' + str(edge) + ' to ' + self.name
                info(infomsg)

                attrs = dict(attrs,
                             **{'domain': 'semantics',
                                'type': 'argument',
                                'frompredpatt': False})

                self.graph.add_node(node,
                                    **{k: v
                                       for k, v in attrs.items()
                                       if k != 'headof'})
                self.graph.add_edge(*edge, domain='semantics', type='head')

                instedge = (node, node.replace('semantics-subarg', 'syntax'))
                self.graph.add_edge(*instedge, domain='interface', type='head')

        elif 'subargof' in attrs and attrs['subargof'] in self.graph.nodes:
            edge = (attrs['subargof'], node)

            if not add_subargs:
                infomsg = 'subarg edge ' + str(edge) + ' in ' + self.name +\
                          ' found in annotations but not added'
                info(infomsg)

            else:
                infomsg = 'adding subarg edge ' + str(edge) + ' to ' +\
                          self.name
                info(infomsg)

                attrs = dict(attrs,
                             **{'domain': 'semantics',
                                'type': 'argument',
                                'frompredpatt': False})

                self.graph.add_node(node,
                                    **{k: v
                                       for k, v in attrs.items()
                                       if k != 'subargof'})
                self.graph.add_edge(*edge,
                                    domain='semantics',
                                    type='subargument')

                instedge = (node, node.replace('semantics-subarg', 'syntax'))
                self.graph.add_edge(*instedge, domain='interface', type='head')

        elif 'subpredof' in attrs and attrs['subpredof'] in self.graph.nodes:
            edge = (attrs['subpredof'], node)

            if not add_subpreds:
                infomsg = 'subpred edge ' + str(edge) + ' in ' + self.name +\
                          ' found in annotations but not added'
                info(infomsg)

            else:
                infomsg = 'adding subpred edge ' + str(edge) + ' to ' +\
                          self.name
                info(infomsg)

                attrs = dict(attrs,
                             **{'domain': 'semantics',
                                'type': 'predicate',
                                'frompredpatt': False})

                self.graph.add_node(node,
                                    **{k: v
                                       for k, v in attrs.items()
                                       if k != 'subpredof'})

                self.graph.add_edge(*edge,
                                    domain='semantics',
                                    type='subpredicate')

                instedge = (node, node.replace('semantics-subpred', 'syntax'))
                self.graph.add_edge(*instedge, domain='interface', type='head')

        elif not add_orphans:
            infomsg = 'orphan node ' + node + ' in ' + self.name +\
                      ' found in annotations but not added'
            info(infomsg)

        else:
            warnmsg = 'adding orphan node ' + node + ' in ' + self.name
            warning(warnmsg)

            attrs = dict(attrs,
                         **{'domain': 'semantics',
                            'type': 'predicate',
                            'frompredpatt': False})

            self.graph.add_node(node,
                                **{k: v
                                   for k, v in attrs.items()
                                   if k != 'subpredof'})

            synnode = node.replace('semantics-pred', 'syntax')
            synnode = synnode.replace('semantics-arg', 'syntax')
            synnode = synnode.replace('semantics-subpred', 'syntax')
            synnode = synnode.replace('semantics-subarg', 'syntax')
            instedge = (node, synnode)
            self.graph.add_edge(*instedge, domain='interface', type='head')

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
    annotation
        mapping from node ids or pairs of node ids separated by _ to
        attribute-value pairs; node ids must not contain _
    """

    CACHE = {}

    def __init__(self, annotation: Dict[str, Dict[str, Any]]):
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
    def from_json(cls, jsonfile: Union[str, TextIO]) -> 'UDSAnnotation':
        """Load Universal Decompositional Semantics annotation from JSON

        The format of the JSON passed to this class method must be:

        ::

            {GRAPHID_1: {NODEID_1_1: {ATTRIBUTE_I: VALUE,
                                      ATTRIBUTE_J: VALUE,
                                      ...},
                         ...},
             GRAPHID_2: {NODEID_2_1: {ATTRIBUTE_K: VALUE,
                                      ATTRIBUTE_L: VALUE,
                                      ...},
                         ...},
             ...
            }


        Graph and node identifiers must match the graph and node
        identifiers of the predpatt graphs to which the annotations
        will be added

        Parameters
        ----------
        jsonfile
            (path to) file containing annotations as JSON
        """

        if jsonfile in cls.CACHE:
            return cls.CACHE[jsonfile]

        ext = splitext(basename(jsonfile))[-1]

        if isinstance(jsonfile, str) and ext == '.json':
            with open(jsonfile) as infile:
                annotation = json.load(infile)

        elif isinstance(jsonfile, str):
            annotation = json.loads(jsonfile)

        else:
            annotation = json.load(jsonfile)

        cls.CACHE[jsonfile] = cls(annotation)

        return cls.CACHE[jsonfile]
