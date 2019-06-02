from numpy import array
from ..corpus import Corpus
from networkx import DiGraph

CONLL_HEAD = {'u': ['id', 'form', 'lemma', 'upos', 'xpos',
                    'feats', 'head', 'deprel', 'deps', 'misc'],
              'x': ['id', 'form', 'lemma', 'cpostag', 'postag',
                    'feats', 'head', 'deprel', 'phead', 'pdeprel']}

CONLL_NODE_ATTRS = {'u': {k: CONLL_HEAD['u'].index(k)
                          for k in ['form', 'lemma', 'upos', 'xpos', 'feats']},
                    'x': {k: CONLL_HEAD['x'].index(k)
                          for k in ['form', 'lemma', 'cpostag', 'postag', 'feats']}}

CONLL_EDGE_ATTRS = {'u': {k: CONLL_HEAD['u'].index(k)
                          for k in ['deprel']},
                    'x': {k: CONLL_HEAD['x'].index(k)
                          for k in ['deprel']}}


class CoNLLDependencyTreeCorpus(Corpus):
    """Class for building and containing dependency trees from CoNLL-U annotated sentences

    Attributes
    ----------
    trees : list(Tree)
        trees constructed from annotated sentences
    """

    def _graphbuilder(self, graphid, rawgraph):
        return DependencyGraphBuilder.from_conll(rawgraph, graphid)
    
class DependencyGraphBuilder(object):
    """a dependency graph builder"""
    
    @classmethod
    def from_conll(cls, conll, treeid='', spec='u'):
        """build DiGraph from a CoNLL representation

        Parameters
        ----------
        conll : list(list)
            conll representation
        treeid : str
            a unique identifier for the tree
        spec  : str (default="u")
            the specification to assume of the conll representation
        """

        # handle null treeids
        treeid = treeid+'-' if treeid else ''
        
        # initialize the dependency graph
        depgraph = DiGraph(conll=array(conll))
        depgraph.name = treeid.strip('-')
        
        depgraph.add_nodes_from([cls._conll_node_attrs(treeid, row, spec)
                                 for row in conll])
        depgraph.add_edges_from([cls._conll_edge_attrs(treeid, row, spec)
                                 for row in conll])

        return depgraph

    @staticmethod
    def _conll_node_attrs(treeid, row, spec):
        node_id = row[0]
        
        node_attrs = {}
        other_attrs = {}
        
        for attr, idx in CONLL_NODE_ATTRS[spec].items():
            # convert features into a dictionary
            if attr == 'feats':
                if row[idx] != '_':
                    feat_split = row[idx].split('|')
                    other_attrs = dict([kv.split('=')
                                        for kv in feat_split])

            else:
                node_attrs[attr] = row[idx]

        node_attrs = dict(node_attrs, **other_attrs)
                
        return (treeid+'syntax-'+node_id, node_attrs)

    @staticmethod
    def _conll_edge_attrs(treeid, row, spec):
        child_id = treeid+'syntax-'+row[0]
        parent_id = treeid+'syntax-'+row[CONLL_HEAD[spec].index('head')]
        edge_attrs = {attr: row[idx] for attr, idx in CONLL_EDGE_ATTRS[spec].items()}
        
        return (parent_id, child_id, edge_attrs)
    
