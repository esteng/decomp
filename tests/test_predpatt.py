from io import StringIO
from networkx import DiGraph
from predpatt import load_conllu, PredPatt, PredPattOpts
from decomp.syntax.dependency import DependencyGraphBuilder
from decomp.semantics.predpatt import PredPattCorpus, PredPattGraphBuilder

rawtree = '''1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	police	police	NOUN	NN	Number=Sing	3	compound	_	_
3	commander	commander	NOUN	NN	Number=Sing	7	nsubj	_	_
4	of	of	ADP	IN	_	6	case	_	_
5	Ninevah	Ninevah	PROPN	NNP	Number=Sing	6	compound	_	_
6	Province	Province	PROPN	NNP	Number=Sing	3	nmod	_	_
7	announced	announce	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
8	that	that	SCONJ	IN	_	11	mark	_	_
9	bombings	bombing	NOUN	NNS	Number=Plur	11	nsubj	_	_
10	had	have	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	11	aux	_	_
11	declined	decline	VERB	VBN	Tense=Past|VerbForm=Part	7	ccomp	_	_
12	80	80	NUM	CD	NumType=Card	13	nummod	_	_
13	percent	percent	NOUN	NN	Number=Sing	11	dobj	_	_
14	in	in	ADP	IN	_	15	case	_	_
15	Mosul	Mosul	PROPN	NNP	Number=Sing	11	nmod	_	SpaceAfter=No
16	,	,	PUNCT	,	_	11	punct	_	_
17	whereas	whereas	SCONJ	IN	_	20	mark	_	_
18	there	there	PRON	EX	_	20	expl	_	_
19	had	have	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	20	aux	_	_
20	been	be	VERB	VBN	Tense=Past|VerbForm=Part	11	advcl	_	_
21	a	a	DET	DT	Definite=Ind|PronType=Art	23	det	_	_
22	big	big	ADJ	JJ	Degree=Pos	23	amod	_	_
23	jump	jump	NOUN	NN	Number=Sing	20	nsubj	_	_
24	in	in	ADP	IN	_	26	case	_	_
25	the	the	DET	DT	Definite=Def|PronType=Art	26	det	_	_
26	number	number	NOUN	NN	Number=Sing	23	nmod	_	_
27	of	of	ADP	IN	_	28	case	_	_
28	kidnappings	kidnapping	NOUN	NNS	Number=Plur	26	nmod	_	SpaceAfter=No
29	.	.	PUNCT	.	_	7	punct	_	_'''

listtree = [l.split() for l in rawtree.split('\n')]

def setup_graph():
    ud = DependencyGraphBuilder.from_conll(listtree, 'tree1')
    
    pp = PredPatt(next(load_conllu(rawtree))[1],
                  opts=PredPattOpts(resolve_relcl=True,
                                    borrow_arg_for_relcl=True,
                                    resolve_conj=False,
                                    cut=True))

    graph = PredPattGraphBuilder.from_predpatt(pp, ud, 'tree1')
    
    return pp, graph

def setup_corpus():
    rawfile = StringIO(rawtree)
    return PredPattCorpus.from_file(f=rawfile)

## could use @nose.with_setup
def test_predpatt_graph_builder():
    pp, pp_graph = setup_graph()

    assert pp_graph.name == 'tree1'
    assert all(['tree1' in nodeid
                for nodeid in pp_graph.nodes])
    
    # test syntax nodes
    assert pp_graph.nodes['tree1-syntax-0'] == {}
    
    for idx, node in pp_graph.nodes.items():
        if 'syntax' in idx:
            idx = idx.split('-')[-1]
            for row in listtree:
                if int(row[0]) == idx:
                    assert node['form'] == row[1]
                    assert node['lemma'] == row[2]
                    assert node['upos'] == row[3]
                    assert node['xpos'] == row[4]        

    for (idx1, idx2), edge in pp_graph.edges.items():
        if 'syntax' in idx1 and 'syntax' in idx2:
            idx1, idx2 = idx1.split('-')[-1], idx2.split('-')[-1]
            for row in listtree:
                if int(row[0]) == idx2:
                    assert int(row[6]) == idx1
                    assert row[7] == edge['deprel']
        
    # test semantics nodes
    assert 'tree1-semantics-pred-0' not in pp_graph.nodes
    assert 'tree1-semantics-arg-0' not in pp_graph.nodes    

    assert all(['arg' in nodeid or 'pred' in nodeid
                for nodeid in pp_graph.nodes
                if 'semantics' in nodeid])

    assert all(['arg' not in nodeid and 'pred' not in nodeid
                for nodeid in pp_graph.nodes
                if 'syntax' in nodeid])

    # test argument edges
    assert all([pp_graph.edges[(nodeid2, nodeid1)]['semrel'] == 'arg'
                for nodeid1, node1 in pp_graph.nodes.items()
                for nodeid2 in pp_graph.nodes
                if 'semantics-arg' in nodeid1
                if 'semantics-pred' in nodeid2
                if (nodeid2, nodeid1) in pp_graph.edges])    
    
    # tests subpredicate edges
    subprededge = ('tree1-semantics-arg-11', 'tree1-semantics-pred-11')
    assert pp_graph.edges[subprededge]['semrel'] == 'subpred'
    
    assert all([(nodeid2, nodeid1) in pp_graph.edges and
                pp_graph.edges[(nodeid2, nodeid1)]['semrel'] == 'subpred'
                for nodeid1, node1 in pp_graph.nodes.items()
                for nodeid2 in pp_graph.nodes
                if 'semantics-pred' in nodeid1
                if 'semantics-arg' in nodeid2
                if nodeid1.split('-')[-1] == nodeid2.split('-')[-1]])
    
def test_predpatt_corpus():
    corpus = setup_corpus()
    
    assert all([isinstance(t, DiGraph) for _, t in corpus.graphs.items()])
    assert all([isinstance(t, DiGraph) for _, t in corpus]) # tests iterator
    assert list(corpus) # tests iterator reset
