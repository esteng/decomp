# pylint: disable=W0102
# pylint: disable=W0212
# pylint: disable=W0221
# pylint: disable=W0231
# pylint: disable=W0640
# pylint: disable=C0103
"""Module for containing representing UDS graphs"""

import json

from logging import info, warning
from networkx import adjacency_data, adjacency_graph
from .predpatt import PredPattCorpus


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

        self.rootid = list(self.filter_nodes({'type': 'root'}))[0]

    def filter_nodes(self, keep):
        """Filter nodes satisfying keep and not satisfying reject

        Parameters
        ----------
        keep : dict(str, str | list(str | object -> bool))
            a mapping from node attributes to lists of characteristic
            functions on the values of those attributes; if a node is
            true on all of these characteristic functions, it will be
            kept

        Returns
        -------
        dict(str, dict(str, object))
        """

        return self.__class__._filter(self.graph.nodes, keep)

    def filter_edges(self, keep):
        """Filter nodes satisfying keep and not satisfying reject

        Parameters
        ----------
        keep : dict(str, object | list(object | object -> bool))
            a mapping from edge attributes to lists of characteristic
            functions on the values of those attributes; if an edge is
            true on all of these characteristic functions, it will be
            kept

        Returns
        -------
        dict(str, dict(str, object))
        """

        return self.__class__._filter(self.graph.edges, keep)

    @staticmethod
    def _filter(data, keep):
        for k, val in keep.items():
            if isinstance(val, list):
                for i, elem in enumerate(val):
                    val[i] = lambda x: x == elem

                keep[k] = val

            else:
                keep[k] = lambda x: x == val

        return {ident: attr
                for ident, attr
                in data.items()
                if all(f(attr[k])
                       for k, f
                       in keep.items())}

    @property
    def sentence(self):
        """The sentence the graph annotates"""

        return self.graph.nodes[self.rootid]['sentence']

    @property
    def syntax_nodes(self):
        """The syntax nodes in the graph"""

        return self.filter_nodes({'type': 'syntax'})

    @property
    def semantics_nodes(self):
        """The semantics nodes in the graph"""

        return self.filter_nodes({'type': 'semantics'})

    @property
    def predicate_nodes(self):
        """The predicate (semantics) nodes in the graph"""

        return self.filter_nodes({'type': 'semantics',
                                  'subtype': 'predicate'})

    @property
    def argument_nodes(self):
        """The argument (semantics) nodes in the graph"""

        return self.filter_nodes({'type': 'semantics',
                                  'subtype': 'argument'})

    @property
    def syntax_subgraph(self):
        """The part of the graph with only syntax nodes"""

        return self.graph.subgraph(list(self.syntax_nodes.keys()))

    @property
    def semantics_subgraph(self):
        """The part of the graph with only semantics nodes"""

        return self.graph.subgraph(list(self.semantics_nodes.keys()))

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
                            'subtype': 'argument',
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
                            'subtype': 'predicate',
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
                            'subtype': 'predicate',
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
