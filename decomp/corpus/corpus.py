"""Module for defining abstract graph corpus readers"""

from abc import ABCMeta, abstractmethod

from random import choices
from warnings import warn

class Corpus(metaclass=ABCMeta):
    """Container for graphs

    Parameters
    ----------
    parses : iterable
        list of parsed sentences

    Attributes
    ----------
    graphs : list(networkx.graph)
        list of graphs constructed from data
    graphids : list(str)
        list of ids for graphs constructed from data
    ngraphs : int
        number of graphs in corpus
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
        """Dictionary-like iterator for (graphid, graph) pairs"""
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

    @abstractmethod
    def _graphbuilder(self, graphid, rawgraph):
        raise NotImplementedError

    @property
    def graphs(self):
        """Read-only collection of graphs in corpus"""
        return self._graphs

    @property
    def graphids(self):
        """Read-only collection of graph ids in corpus"""
        return self._graphids

    @property
    def ngraphs(self):
        """Number of graphs in corpus"""
        return len(self._graphs)

    def sample(self, k):
        """Sample k graphs from the corpus"""
        graphids = choices(self._graphids, k=k)

        return {tid: self._graphs[tid] for tid in graphids}
