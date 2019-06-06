# pylint: disable=W0221
# pylint: disable=R0903
# pylint: disable=R1704
"""Module for converting PredPatt objects to networkx digraphs"""

from os.path import basename
from warnings import warn
from networkx import DiGraph
from predpatt import load_conllu, PredPatt, PredPattOpts
from ..corpus import Corpus
from ..syntax.dependency import CoNLLDependencyTreeCorpus

DEFAULT_PREDPATT_OPTIONS = PredPattOpts(resolve_relcl=True,
                                        borrow_arg_for_relcl=True,
                                        resolve_conj=False,
                                        cut=True)  # Resolve relative clause


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

    def _graphbuilder(self, graphid, predpatt_depgraph):
        predpatt, depgraph = predpatt_depgraph

        return PredPattGraphBuilder.from_predpatt(predpatt, depgraph, graphid)

    @classmethod
    def from_file(cls, fpath=None, file=None, options=None, name=None):
        """Load a CoNLL dependency corpus and apply predpatt

        Parameters
        ----------
        fpath : str
            the path to a .conll(u) file
        file : file-like
            a .conll(u) file opened in read mode
        options : PredPattOpts
            options for predpatt extraction
        name : str
            the name of the corpus; used in constructing treeids
        """
        try:
            assert file is None or fpath is None
        except AssertionError:
            warnmsg = 'both "file" and "fpath" passed; ignoring "fpath"'
            warn(warnmsg)

        try:
            assert file is not None or fpath is not None
        except AssertionError:
            errmsg = 'must pass either "file" or "fpath"'
            raise ValueError(errmsg)

        if file is None:
            name = basename(fpath) if name is None else name
            options = DEFAULT_PREDPATT_OPTIONS if options is None else options

            with open(fpath, 'r') as file:
                return cls._read_conllu(name, file, options)

        else:
            name = '' if name is None else name
            return cls._read_conllu(name, file, options)

    @classmethod
    def _read_conllu(cls, name, infile, options):
        data = infile.read()

        # load the CoNLL dependency parses as graphs
        ud_corp = {name+'-'+str(i+1): [line.split()
                                       for line in block.split('\n')
                                       if len(line) > 0
                                       if line[0] != '#']
                   for i, block in enumerate(data.split('\n\n'))}
        ud_corp = CoNLLDependencyTreeCorpus(ud_corp)

        # extract the predpatt for those dependency parses
        predpatt = {name+'-'+sid.split('_')[1]: PredPatt(ud_parse,
                                                         opts=options)
                    for sid, ud_parse in load_conllu(data)}

        return cls({n: (pp, ud_corp[n])
                    for n, pp in predpatt.items()})


class PredPattGraphBuilder:
    """A predpatt graph builder"""

    @classmethod
    def from_predpatt(cls, predpatt, depgraph, graphid=''):
        """Build a DiGraph from a PredPatt object and another DiGraph

        Parameters
        ----------
        predpatt : predpatt.PredPatt
            the predpatt extraction for the dependency parse
        depgraph : networkx.DiGraph
            the dependency graph
        graphid : str
            the tree indentifier; will be a prefix of all node
            identifiers
        """
        # handle null graphids
        graphid = graphid+'-' if graphid else ''

        # initialize the predpatt graph
        # predpattgraph = DiGraph(predpatt=predpatt)
        predpattgraph = DiGraph()
        predpattgraph.name = graphid.strip('-')

        # include all of the syntax edges in the original dependendency graph
        predpattgraph.add_nodes_from([(n, attr)
                                      for n, attr in depgraph.nodes.items()])
        predpattgraph.add_edges_from([(n1, n2, attr)
                                      for (n1, n2), attr
                                      in depgraph.edges.items()])

        # add links between predicate nodes and syntax nodes
        predpattgraph.add_edges_from([edge
                                      for event in predpatt.events
                                      for edge
                                      in cls._instantiation_edges(graphid,
                                                                  event,
                                                                  'pred')])

        # add links between argument nodes and syntax nodes
        edges = [edge
                 for event in predpatt.events
                 for arg in event.arguments
                 for edge
                 in cls._instantiation_edges(graphid, arg, 'arg')]

        predpattgraph.add_edges_from(edges)

        # add links between predicate nodes and argument nodes
        edges = [edge
                 for event in predpatt.events
                 for arg in event.arguments
                 for edge in cls._predarg_edges(graphid, event, arg,
                                                arg.position
                                                in [e.position
                                                    for e
                                                    in predpatt.events])]

        predpattgraph.add_edges_from(edges)

        # mark that all the semantic nodes just added were from predpatt
        # this is done to distinguish them from nodes added through annotations
        for node in predpattgraph.nodes:
            if 'semantics' in node:
                predpattgraph.nodes[node]['frompredpatt'] = 'true'

        return predpattgraph

    @staticmethod
    def _instantiation_edges(graphid, node, typ):
        parent_id = graphid+'semantics-'+typ+'-'+str(node.position+1)
        child_head_token_id = graphid+'syntax-'+str(node.position+1)
        child_span_token_ids = [graphid+'syntax-'+str(tok.position+1)
                                for tok in node.tokens
                                if child_head_token_id !=
                                graphid+'syntax-'+str(tok.position+1)]

        return [(parent_id, child_head_token_id, {'instantiation': 'head'})] +\
               [(parent_id, tokid, {'instantiation': 'nonhead'})
                for tokid in child_span_token_ids]

    @staticmethod
    def _predarg_edges(graphid, parent_node, child_node, pred_child):
        parent_id = graphid+'semantics-pred-'+str(parent_node.position+1)
        child_id = graphid+'semantics-arg-'+str(child_node.position+1)

        if pred_child:
            child_id_pred = graphid+'semantics-pred-'+str(child_node.position+1)
            return [(parent_id,
                     child_id,
                     {'semrel': 'arg', 'frompredpatt': 'true'})] +\
                   [(child_id,
                     child_id_pred,
                     {'semrel': 'subpred', 'frompredpatt': 'true'})]

        return [(parent_id,
                 child_id,
                 {'semrel': 'arg', 'frompredpatt': 'true'})]
