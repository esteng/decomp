from os.path import basename
from warnings import warn
from networkx import DiGraph
from predpatt import load_conllu, PredPatt, PredPattOpts
from ..corpus import Corpus
from ..syntax.dependency import CoNLLDependencyTreeCorpus

default_predpatt_options =  PredPattOpts(resolve_relcl=True,
                                        borrow_arg_for_relcl=True,
                                        resolve_conj=False,
                                        cut=True) # Resolve relative clause


class PredPattCorpus(Corpus):
    """Container for predpatt graphs

    Parameters
    ----------
    treeid : str
        an identifier for the tree
    predpatt_depgraph : tuple(predpatt.PredPatt, networkx.DiGraph)
        a pairing of the predpatt for a dependency parse and the graph
        representing that dependency parse

    Attributes
    ----------
    graphs : list(networkx.DiGraph)
        trees constructed from annotated sentences
    """

    def _graphbuilder(self, treeid, predpatt_depgraph):
        predpatt, depgraph = predpatt_depgraph
        
        return PredPattGraphBuilder.from_predpatt(predpatt, depgraph, treeid)

    @classmethod
    def from_file(cls, fpath=None, f=None, options=None, name=None):
        """Load a CoNLL dependency corpus and apply predpatt

        Parameters
        ----------
        fpath : str
            the path to a .conll(u) file
        f : file-like
            a .conll(u) file opened in read mode
        options : PredPattOpts
            options for predpatt extraction
        name : str
            the name of the corpus; used in constructing treeids
        """
        try:
            assert f is None or fpath is None
        except AssertionError:
            warnmsg = 'both "f" and "fpath" passed; ignoring "fpath"'
            warn(warnmsg)

        try:
            assert f is not None or fpath is not None
        except AssertionError:
            errmsg = 'must pass either "f" or "fpath"'
            raise ValueError(errmsg)
            
        if f is None:
            name = basename(fpath) if name is None else name
            options = default_predpatt_options if options is None else options

            with open(fpath, 'r') as f:
                return cls._read_conllu(name, f, options)

        else:
            name = '' if name is None else name
            return cls._read_conllu(name, f, options)

    @classmethod
    def _read_conllu(cls, name, infile, options):
        data = infile.read()

        # load the CoNLL dependency parses as graphs
        ud = {name+'-'+str(i+1): [line.split()
                                  for line in block.split('\n')
                                  if len(line) > 0
                                  if line[0]!='#']
              for i, block in enumerate(data.split('\n\n'))}
        ud = CoNLLDependencyTreeCorpus(ud)

        # extract the predpatt for those dependency parses
        predpatt = {name+'-'+sid.split('_')[1]: PredPatt(ud_parse,
                                                         opts=options)
                    for sid, ud_parse in load_conllu(data)}

        return cls({n: (pp, ud[n])
                    for n, pp in predpatt.items()})
        
                
class PredPattGraphBuilder(object):
    """A predpatt graph builder"""
    
    @classmethod
    def from_predpatt(cls, predpatt, depgraph, treeid=''):
        """Build a DiGraph from a PredPatt object and another DiGraph

        Parameters
        ----------
        predpatt : predpatt.PredPatt
            the predpatt extraction for the dependency parse
        depgraph : networkx.DiGraph
            the dependency graph
        treeid : str
            the tree indentifier; will be a prefix of all node
            identifiers
        """
        # handle null treeids
        treeid = treeid+'-' if treeid else ''
        
        # initialize the predpatt graph
        #predpattgraph = DiGraph(predpatt=predpatt)
        predpattgraph = DiGraph()
        predpattgraph.name = treeid.strip('-')

        # include all of the syntax edges in the original dependendency graph
        predpattgraph.add_nodes_from([(n, attr)
                                      for n, attr in depgraph.nodes.items()])
        predpattgraph.add_edges_from([(n1, n2, attr)
                                      for (n1, n2), attr in depgraph.edges.items()])

        # add links between predicate nodes and syntax nodes
        predpattgraph.add_edges_from([edge
                                      for event in predpatt.events
                                      for edge in cls._instantiation_edges(treeid, event, 'pred')])

        # add links between argument nodes and syntax nodes
        predpattgraph.add_edges_from([edge
                                      for event in predpatt.events
                                      for arg in event.arguments
                                      for edge in cls._instantiation_edges(treeid, arg, 'arg')])

        # add links between predicate nodes and argument nodes        
        predpattgraph.add_edges_from([edge
                                      for event in predpatt.events
                                      for arg in event.arguments
                                      for edge in cls._predarg_edges(treeid, event, arg,
                                                                     arg.position in [e.position
                                                                                      for e in predpatt.events])])

        # mark that all the semantic nodes just added were from predpatt
        # this is done to distinguish them from nodes added through annotations
        for node in predpattgraph.nodes:
            if 'semantics' in node:
                predpattgraph.nodes[node]['frompredpatt'] = 'true'
        
        return predpattgraph

    @staticmethod
    def _instantiation_edges(treeid, node, typ):
        parent_id = treeid+'semantics-'+typ+'-'+str(node.position+1)
        child_head_token_id = treeid+'syntax-'+str(node.position+1)
        child_span_token_ids = [treeid+'syntax-'+str(tok.position+1)
                                for tok in node.tokens
                                if child_head_token_id!=treeid+'syntax-'+str(tok.position+1)]
        
        return [(parent_id, child_head_token_id, {'instantiation': 'head'})] +\
               [(parent_id, tokid, {'instantiation': 'nonhead'})
                for tokid in child_span_token_ids]

    @staticmethod
    def _predarg_edges(treeid, parent_node, child_node, pred_child):
        parent_id = treeid+'semantics-pred-'+str(parent_node.position+1)
        child_id = treeid+'semantics-arg-'+str(child_node.position+1)            
        
        if pred_child:
            child_id_pred = treeid+'semantics-pred-'+str(child_node.position+1)
            return [(parent_id, child_id, {'semrel': 'arg', 'frompredpatt': 'true'})]+\
                   [(child_id, child_id_pred, {'semrel': 'subpred', 'frompredpatt': 'true'})]
        
        else:
            return [(parent_id, child_id, {'semrel': 'arg', 'frompredpatt': 'true'})]
