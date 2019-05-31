from abc import ABCMeta, abstractmethod, abstractproperty, abstractstaticmethod

from random import choices
from warnings import warn

class Corpus(metaclass=ABCMeta):
    """Samples trees given distributional data

    Parameters
    ----------
    parses : iterable
        list of parsed sentences

    Attributes
    ----------
    trees : list(Tree)
        list of graphs constructed from data
    """
    
    def __init__(self, parses):
        self._parses = parses
        
        self._graphs = {}
        
        self._build_graphs()
        self._initialize_graphs_iterator()
        
    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self._graphs_iter)
        except StopIteration:
            self._initialize_graphs_iterator()
            raise StopIteration

    def items(self):
        return self._graphs.items()
        
    def __getitem__(self, k):
        return self._graphs[k]

    def __contains__(self, k):
        return k in self._graphs
    
    def __len__(self):
        return len(self._graphs)
    
    def _initialize_graphs_iterator(self):
        self._graphs_iter = (el for el in self._graphs.items())

    def _build_graphs(self):
        for graphid, rawgraph in self._parses.items():
            try:
                self._graphs[graphid] = self._graphbuilder(graphid, rawgraph)
            except ValueError:
                warn(graphid+' has no or multiple root nodes')
            except RecursionError:
                warn(graphid+' has loops')

        self._graphids = list(self._graphs)

    @abstractstaticmethod
    def _graphbuilder(self):
        raise NotImplementedError

    @property
    def graphs(self):
        return self._graphs

    @property
    def graphids(self):
        return self._graphids
    
    @property
    def ngraphs(self):
        return len(self._graphs)
    
    def flatten(self, attr='data'):
        return [el for t in self._graphs.values() for el in t.flatten(attr)]
    
    def unique(self, attr='data'):
        return set(el for t in self._graphs.values() for el in t.unique(attr))

    def sample(self, k):
        graphids = choices(self._graphids, k=k)

        return {tid: self._graphs[tid] for tid in graphids}
