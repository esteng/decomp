"""Module for serializing UDS graphs"""
from warnings import warn
import json


class MRSWriter:
    """Class for serializing UDS graphs to CoNLL-like MRS

    Because the MRS format cannot natively handle anything beyond
    simple predicate-argument relations, this class filters any nodes
    not returned from PredPatt--e.g. subpredicate and subargument
    relations.

    Parameters
    ----------
    graph : decomp.semantics.UDSGraph
        UDS graph to serialize to MRS

    Attributes
    ----------
    graph : decomp.semantics.UDSGraph

    Methods
    -------
    to_list
    to_string

    Raises
    ------
    ValueError
    """

    def __init__(self, graph):
        self.graph = graph

        self._build_mrs()

    def _build_mrs(self):
        self.mrs = {}

        self.pred_head_nums = sorted([int(nodeid.split('-')[-1])
                                      for nodeid
                                      in self.graph.predicate_nodes])
        self.arg_head_nums = sorted([int(nodeid.split('-')[-1])
                                     for nodeid
                                     in self.graph.argument_nodes])

        if not self.pred_head_nums:
            warn(self.graph.name + ' has no predicates')

        maxnodenum = 0

        for synid in self.graph.syntax_nodes:
            nodenum = int(synid.split('-')[-1])
            maxnodenum = max(nodenum, maxnodenum)

            if nodenum > 0:
                self._add_syntax(synid, nodenum)
                self._add_root_indicator(synid, nodenum)
                ispredhead, isarghead = self._add_pred_indicator(nodenum)
                semid_arg = self._add_node_semantics(synid,
                                                     nodenum,
                                                     ispredhead,
                                                     isarghead)
                self._add_edge_semantics(semid_arg, nodenum)

        self._attach_orphans_to_root()

        self.maxnodenum = maxnodenum

    def _add_syntax(self, synid, nodenum):
        synnode = self.graph.nodes[synid]
        self.mrs[nodenum] = [synnode[k]
                             for k
                             in ['form', 'lemma', 'xpos']]

    def _add_root_indicator(self, synid, nodenum):
        if (self.graph.synroot, synid) in self.graph.edges:
            self.mrs[nodenum].append('+')
        else:
            self.mrs[nodenum].append('-')

    def _add_pred_indicator(self, nodenum):
        ispredhead = nodenum in self.pred_head_nums
        isarghead = nodenum in self.arg_head_nums

        if ispredhead:
            self.mrs[nodenum].append('+')
        else:
            self.mrs[nodenum].append('-')

        return ispredhead, isarghead

    def _add_node_semantics(self, synid, nodenum, ispredhead, isarghead):
        nodeinfo = {}

        semid_pred = self.graph.name +\
                     '-semantics-pred-' +\
                     synid.split('-')[-1]
        semid_arg = self.graph.name +\
                    '-semantics-arg-' +\
                    synid.split('-')[-1]

        if ispredhead and isarghead:
            semnode_arg = self.graph.nodes[semid_arg]
            semnode_pred = self.graph.nodes[semid_pred]

            nodeinfo = dict({k: v
                             for k, v in semnode_arg.items()
                             if k not in ['frompredpatt', 'id']},
                            **{k: v
                               for k, v in semnode_pred.items()
                               if k not in ['frompredpatt', 'id']})

        elif ispredhead:
            semnode_pred = self.graph.nodes[semid_pred]

            nodeinfo = {k: v
                        for k, v in semnode_pred.items()
                        if k not in ['frompredpatt', 'id']}

        elif isarghead:
            semnode_arg = self.graph.nodes[semid_arg]

            nodeinfo = {k: v
                        for k, v in semnode_arg.items()
                        if k not in ['frompredpatt', 'id']}

        if nodeinfo:
            self.mrs[nodenum].append(json.dumps(nodeinfo))
        else:
            self.mrs[nodenum].append('_')

        return semid_arg

    def _add_edge_semantics(self, semid_arg, nodenum):
        for prednum in self.pred_head_nums:
            edgeinfo = {}
            semparentid = self.graph.name +\
                          '-semantics-pred-' +\
                          str(prednum)

            if (semparentid, semid_arg) in self.graph.edges:
                semedge = self.graph.edges[(semparentid, semid_arg)]

                edgeinfo = {k: v
                            for k, v in semedge.items()
                            if k not in ['frompredpatt', 'id']}

            if edgeinfo:
                edgeinfo = json.dumps(edgeinfo)

                self.mrs[nodenum].append(edgeinfo)
            else:
                self.mrs[nodenum].append('_')

    def _attach_orphans_to_root(self):
        isroot = {i: l[3] == '+' for i, l in self.mrs.items()}

        try:
            assert sum(isroot.values()) == 1
        except AssertionError:
            errmsg = self.graph.name + ' has multiple roots'
            raise ValueError(errmsg)

        rootrelnum = [self.pred_head_nums.index(i)
                      for i, v in isroot.items() if v][0]

        for i, line in self.mrs.items():
            # if this is a predicate and there are no other relations
            if line[4] == '+' and all([elem == '_' for elem in line[6:]]):
                # add a "parallel" (nonsubordinating) relation to the root
                self.mrs[i][6+rootrelnum] = json.dumps({'semrel': 'parallel'})

    def to_list(self):
        """Convert UDS graph to CoNLL-like MRS list"""

        return [[str(i)]+self.mrs[i] for i in range(1, self.maxnodenum+1)]

    def to_string(self):
        """Convert UDS graph to CoNLL-like MRS string"""

        return '\n'.join(['\t'.join(line) for line in self.to_list()])
