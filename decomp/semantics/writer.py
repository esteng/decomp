class MRSWriter(object):

    def __init__(self, graph):
        self.graph = graph
    
    @classmethod
    def to_string(self):
        mrs = {}

        sem_head_nums = sorted([int(nodeid.split('-')[-1])
                                for nodeid in self.semantics_nodes])
        pred_head_nums = sorted([int(nodeid.split('-')[-1])
                                 for nodeid in self.predicate_nodes])
        arg_head_nums = sorted([int(nodeid.split('-')[-1])
                                for nodeid in self.argument_nodes])

        if not pred_head_nums:
            return []
        
        maxnodenum = 0

        for synnodeid in self.syntax_nodes:
            nodenum = int(synnodeid.split('-')[-1])

            maxnodenum = max(nodenum, maxnodenum)
            
            ispredhead = nodenum in pred_head_nums
            isarghead = nodenum in arg_head_nums
            
            semnodeid_pred = self.name+'-semantics-pred-'+synnodeid.split('-')[-1]
            semnodeid_arg = self.name+'-semantics-arg-'+synnodeid.split('-')[-1]
                
            if nodenum > 0:
                synnode = self.graph.nodes[synnodeid]
                mrs[nodenum] = [synnode[k]
                                for k in ['form', 'lemma', 'xpos']]

                # add root indicator
                if (self.synroot, synnodeid) in self.graph.edges:
                    mrs[nodenum].append('+')
                else:
                    mrs[nodenum].append('-')

                # add pred indicator
                if ispredhead:
                    mrs[nodenum].append('+')
                else:
                    mrs[nodenum].append('-')

                # add node info where frame info would be
                nodeinfo = {}
                
                if ispredhead and isarghead:
                    semnode_arg = self.graph.nodes[semnodeid_arg]
                    semnode_pred = self.graph.nodes[semnodeid_pred]

                    nodeinfo = dict({k: v
                                     for k, v in semnode_arg.items()
                                     if k not in ['frompredpatt', 'id']},
                                    **{k: v
                                       for k, v in semnode_pred.items()
                                       if k not in ['frompredpatt', 'id']})
                    
                elif ispredhead:
                    semnode_pred = self.graph.nodes[semnodeid_pred]

                    nodeinfo = {k: v
                                for k, v in semnode_pred.items()
                                if k not in ['frompredpatt', 'id']}

                elif isarghead:
                    semnode_arg = self.graph.nodes[semnodeid_arg]
                    
                    nodeinfo = {k: v
                                for k, v in semnode_arg.items()
                                if k not in ['frompredpatt', 'id']}

                if nodeinfo:
                    mrs[nodenum].append(json.dumps(nodeinfo))
                else:
                    mrs[nodenum].append('_')

                # add edge attributes                
                for prednum in pred_head_nums:
                    edgeinfo = {}                    
                    semparentid = self.name+'-semantics-pred-'+str(prednum)                        

                    if (semparentid, semnodeid_arg) in self.graph.edges:
                        semedge = self.graph.edges[(semparentid, semnodeid_arg)]

                        edgeinfo = {k: v
                                    for k, v in semedge.items()
                                    if k not in ['frompredpatt', 'id']}
                        
                    if edgeinfo:
                        edgeinfo = json.dumps(edgeinfo)

                        mrs[nodenum].append(edgeinfo)
                    else:
                        mrs[nodenum].append('_')

        # attach nodes to root if they don't already have a parent
        isroot = {i: l[4]=='+' for i, l in mrs.items()}
        
        try:
            assert sum(isroot.values())==1
        except AssertionError:
            errmsg = uds_graph.name+' has multiple roots'
            ValueError(errmsg)
                        
        rootrelnum = [pred_head_nums.index(i) for i, v in isroot.items() if v][0]

        for i, line in mrs.items():
            # if this is a predicate and there are no other relations
            if line[4]=='+' and all([elem=='_' for elem in line[6:]]):
                # add a "parallel" (nonsubordinating) relation to the root
                mrs[i][6+rootrelnum] = json.dumps({'semrel': 'parallel'})
        
        return [[str(i)]+mrs[i] for i in range(1, maxnodenum+1)]
