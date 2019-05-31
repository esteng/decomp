import json

from sys import stderr
from warnings import warn
from networkx import DiGraph, adjacency_data, adjacency_graph
from .predpatt import PredPattCorpus
from .writer import MRSWriter

class UDSCorpus(PredPattCorpus):
    """A universal decompositional semantics corpus

    Parameters
    ----------
    predpatt_corpus : PredPattCorpus
    annotations : list(UDSAnnotation)
        the annotations to associate with predpatt nodes 
    """

    def __init__(self, graphs, annotations=[]):
        self._graphs = graphs
        self._annotations = annotations
        
        for ann in annotations:
            self.add_annotation(ann)

    def add_annotation(self, annotation):

        for gname, (node_attrs, edge_attrs) in annotation.items():
            if gname in self._graphs:
                self._graphs[gname].add_annotation(node_attrs, edge_attrs)

    def to_json(self, fpath=None):
        graphs_serializable = {name: graph.to_json()
                               for name, graph in self.graphs.items()}
        
        if fpath is None:
            return json.dumps(graphs_serializable)
        else:
            with open(fpath, 'w') as f:
                json.dump(graphs_serializable, f)

    def to_mrs(self, fpath):
        with open(fpath, 'w') as f:
            for name, graph in self.graphs.items():
                try:
                    mrs = graph.to_mrs()
                except:
                    warn('WARNING: could not write', name, 'to MRS')
                    continue

                if mrs:
                    f.write('# sent-id: '+name+'\n')
                    f.write('# sentence: '+graph.sentence+'\n')

                    for line in mrs:
                        f.write('\t'.join(line)+'\n')
                        
                    f.write('\n')
                    
    @classmethod
    def from_file(cls, ud_fpath, annotation_fpaths=[], name=None):
        predpatt_corpus = PredPattCorpus.from_file(ud_fpath, name=name)
        annotations = [UDSAnnotation.from_json(ann_fpath)
                       for ann_fpath in annotation_fpaths]

        return cls({name: UDSGraph(g, name)
                    for name, g in predpatt_corpus.items()},
                   annotations)

    @classmethod
    def from_json(cls, fpath=None, json_str=None):
        try:
            assert fpath is None or json_str is None
            assert fpath is not None or json_str is not None
        except AssertionError:
            errmsg = 'must pass one and only one of "json_str" or "fpath"'
            raise ValueError(errmsg)

        if json_str is not None:
            graphs_json = json.loads(json_str)
        elif fpath is not None:
            with open(fpath) as f:
                graphs_json = json.load(f)

        graphs = {name: UDSGraph.from_json(g_json, name)
                  for name, g_json in graphs_json.items()}
            
        return cls(graphs)

class UDSGraph(object):

    def __init__(self, graph, name='UDS'):
        self.name = name
        self.graph = graph

        self.add_root()

    @property
    def sentence(self):
        id_word = {int(nodeid.split('-')[-1]): self.graph.nodes[nodeid]['form']
                   for nodeid in self.syntax_nodes
                   if int(nodeid.split('-')[-1]) > 0}
        sentence = [id_word[i] for i in range(1, max(list(id_word.keys()))+1)]

        return ' '.join(sentence)
        
    @property
    def syntax_nodes(self):
        return [node
                for node in self.graph.nodes
                if 'syntax' in node]        

    @property
    def semantics_nodes(self):
        return [node
                for node in self.graph.nodes
                if 'semantics' in node]

    @property
    def predicate_nodes(self):
        return [node
                for node in self.graph.nodes
                if 'semantics-pred' in node]

    @property
    def argument_nodes(self):
        return [node
                for node in self.graph.nodes
                if 'semantics-arg' in node]

    @property
    def syntax_subgraph(self):
        return self.graph.subgraph(self.syntax_nodes)

    @property
    def semantics_subgraph(self):
        return self.graph.subgraph(self.semantics_nodes)

    def add_root(self):
        # the graph should have a dummy syntax root
        self.synroot = self.name+'-syntax-0'

        try:
            assert self.synroot in self.syntax_nodes
        except AssertionError:
            errmsg = 'no syntax root found in '+self.name
            raise ValueError(errmsg)

        # the graph may or may not have a semantics root
        self.semroot = self.name+'-semantics-root-0'

        # if it doesn't, add it
        if self.semroot not in self.graph.nodes:
            self.graph.add_node(self.semroot)
            self.graph.add_edge(self.semroot, self.synroot)

            edges = [(self.semroot, childid)
                     for childid in self.predicate_nodes]
            self.graph.add_edges_from(edges)

        self.root = self.semroot            

    def to_mrs(self):
        """CoNLL-like MRS-formatted parse
        
        Because the MRS format cannot natively handle anything beyond
        simple predicate-argument relations, this method filters any
        nodes not returned from PredPatt--e.g. subpredicate and
        subargument relations.
        """

        return MRSWriter.to_str(self)
                    
    def to_json(self):
        return adjacency_data(self.graph)

    @classmethod
    def from_json(cls, graph, name='UDS'):
        return cls(adjacency_graph(graph), name)

    def add_annotation(self, node_attrs, edge_attrs):
        for node, attrs in node_attrs.items():
            self._add_node_annotation(node, attrs)
            
        for edge, attrs in edge_attrs.items():
            self._add_edge_annotation(edge, attrs)
            
    def _add_node_annotation(self, node, attrs):
        if node in self.graph.nodes:
            self.graph.nodes[node].update(attrs)
            
        elif 'subargof' in attrs:
            edge = (attrs['subargof'], node)

            print('WARNING: adding subarg edge',
                  edge, 'to', self.name)

            attrs['frompredpatt'] = 'false'

            self.graph.add_node(node)
            self.graph.nodes[node].update({k: v
                                      for k, v in attrs.items()
                                      if k!='subargof'})

            self.graph.add_edge(*edge)
            self.graph.edges[edge].update({'semrel': 'subarg'})

            instedge = (node, node.replace('semantics-subarg', 'syntax'))
            self.graph.add_edge(*instedge)
            self.graph.edges[instedge].update({'instantiation': 'head'})

        elif 'subpredof' in attrs:
            edge = (attrs['subpredof'], node)

            print('WARNING: adding subpred edge',
                  edge, 'to', self.name)

            attrs['frompredpatt'] = 'false'

            self.graph.add_node(node)
            self.graph.nodes[node].update({k: v
                                      for k, v in attrs.items()
                                      if k!='subpredof'})

            self.graph.add_edge(*edge)
            self.graph.edges[edge].update({'semrel': 'subpred'})

            instedge = (node, node.replace('semantics-subpred', 'syntax'))
            self.graph.add_edge(*instedge)
            self.graph.edges[instedge].update({'instantiation': 'head'})

        else:
            print('WARNING: adding orphan node',
                  node, 'in', self.name)

            attrs['frompredpatt'] = 'false'

            self.graph.add_node(node)
            self.graph.nodes[node].update({k: v
                                           for k, v in attrs.items()
                                           if k!='subpredof'})

            instedge = (node, node.replace('semantics-pred', 'syntax').replace('semantics-arg', 'syntax'))
            self.graph.add_edge(*instedge)
            self.graph.edges[instedge].update({'instantiation': 'head'})

            if self.root is not None:
                self.graph.add_edge(self.root, node)

    def _add_edge_annotation(self, edge, attrs):
        if edge in self.graph.edges:
            self.graph.edges[edge].update(attrs)
        else:
            print('WARNING: adding unlabeled edge',
                  edge, 'to', self.name)
            self.graph.add_edges_from([(edge[0], edge[1], attrs)])

class UDSAnnotation(object):

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

    def items(self):
        for name, node_attrs in self.node_attributes.items():
            yield name, (node_attrs, self.edge_attributes[name])

    @classmethod
    def from_json(cls, fname):
        with open(fname) as f:
            annotation = json.load(f)

        return cls(annotation)
