import json
from io import StringIO
from predpatt import PredPatt, PredPattOpts, load_conllu
from decomp.syntax.dependency import DependencyGraphBuilder
from decomp.semantics.predpatt import PredPattGraphBuilder
from decomp.semantics.uds import UDSAnnotation, UDSGraph, UDSCorpus

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

annotation1 = '{"tree1": {"tree1-semantics-pred-7": {"factuality-factual": 1.114193081855774}, "tree1-semantics-pred-11": {"factuality-factual": 1.1141914129257202}}}'

annotation2 = '{"tree1": {"tree1-semantics-pred-7_tree1-semantics-arg-3": {"protoroles-awareness": -0.0, "protoroles-change_of_location": -0.4137, "protoroles-change_of_possession": -0.4137, "protoroles-change_of_state": -1.3143, "protoroles-change_of_state_continuous": -0.0, "protoroles-existed_after": 0.0347, "protoroles-existed_before": -0.5095, "protoroles-existed_during": 0.0347, "protoroles-instigation": -0.1604, "protoroles-partitive": -1.7254, "protoroles-sentient": -2.0457, "protoroles-volition": -0.0, "protoroles-was_for_benefit": -1.3143, "protoroles-was_used": -0.3109}}}'

mrs_str = '''1	The	the	DT	-	-	_	_	_	_
2	police	police	NN	-	-	_	_	_	_
3	commander	commander	NN	-	-	{"type": "semantics", "subtype": "arg"}	{"semrel": "arg", "protoroles-awareness": -0.0, "protoroles-change_of_location": -0.4137, "protoroles-change_of_possession": -0.4137, "protoroles-change_of_state": -1.3143, "protoroles-change_of_state_continuous": -0.0, "protoroles-existed_after": 0.0347, "protoroles-existed_before": -0.5095, "protoroles-existed_during": 0.0347, "protoroles-instigation": -0.1604, "protoroles-partitive": -1.7254, "protoroles-sentient": -2.0457, "protoroles-volition": -0.0, "protoroles-was_for_benefit": -1.3143, "protoroles-was_used": -0.3109}	_	_
4	of	of	IN	-	-	_	_	_	_
5	Ninevah	Ninevah	NNP	-	-	_	_	_	_
6	Province	Province	NNP	-	-	_	_	_	_
7	announced	announce	VBD	+	+	{"type": "semantics", "subtype": "pred", "factuality-factual": 1.114193081855774}	{"semrel": "parallel"}	_	_
8	that	that	IN	-	-	_	_	_	_
9	bombings	bombing	NNS	-	-	{"type": "semantics", "subtype": "arg"}	_	{"semrel": "arg"}	_
10	had	have	VBD	-	-	_	_	_	_
11	declined	decline	VBN	-	+	{"type": "semantics", "subtype": "pred", "factuality-factual": 1.1141914129257202}	{"semrel": "arg"}	_	_
12	80	80	CD	-	-	_	_	_	_
13	percent	percent	NN	-	-	{"type": "semantics", "subtype": "arg"}	_	{"semrel": "arg"}	_
14	in	in	IN	-	-	_	_	_	_
15	Mosul	Mosul	NNP	-	-	{"type": "semantics", "subtype": "arg"}	_	{"semrel": "arg"}	_
16	,	,	,	-	-	_	_	_	_
17	whereas	whereas	IN	-	-	_	_	_	_
18	there	there	EX	-	-	_	_	_	_
19	had	have	VBD	-	-	_	_	_	_
20	been	be	VBN	-	+	{"type": "semantics", "subtype": "pred"}	{"semrel": "parallel"}	_	_
21	a	a	DT	-	-	_	_	_	_
22	big	big	JJ	-	-	_	_	_	_
23	jump	jump	NN	-	-	{"type": "semantics", "subtype": "arg"}	_	_	{"semrel": "arg"}
24	in	in	IN	-	-	_	_	_	_
25	the	the	DT	-	-	_	_	_	_
26	number	number	NN	-	-	_	_	_	_
27	of	of	IN	-	-	_	_	_	_
28	kidnappings	kidnapping	NNS	-	-	_	_	_	_
29	.	.	.	-	-	_	_	_	_'''

def setup_annotations():
    ann1 = UDSAnnotation(json.loads(annotation1))
    ann2 = UDSAnnotation(json.loads(annotation2))

    return ann1, ann2

def setup_graph():
    ann1, ann2 = setup_annotations()
    
    ud = DependencyGraphBuilder.from_conll(listtree, 'tree1')
    
    pp = PredPatt(next(load_conllu(rawtree))[1],
                  opts=PredPattOpts(resolve_relcl=True,
                                    borrow_arg_for_relcl=True,
                                    resolve_conj=False,
                                    cut=True))

    pp_graph = PredPattGraphBuilder.from_predpatt(pp, ud, 'tree1')

    graph = UDSGraph(pp_graph, 'tree1')
    graph.add_annotation(*ann1['tree1'])
    graph.add_annotation(*ann2['tree1'])
    
    return graph

# def setup_corpus():
#     rawfile = StringIO(rawtree)
#     return UDSCorpus.from_file(infile=rawfile)


def test_uds_annotation():
    ann1, ann2 = setup_annotations()
    ann1_direct = json.loads(annotation1)['tree1']
    ann2_direct = json.loads(annotation2)['tree1']

    assert all([not edge_attrs
                for n, (node_attrs, edge_attrs) in ann1.items()])

    assert all([ann1_direct[k] == v
                for n, (node_attrs, edge_attrs) in ann1.items()
                for k, v in node_attrs.items()])

    assert all([not node_attrs
                for n, (node_attrs, edge_attrs) in ann2.items()])

    assert all([ann2_direct['_'.join(k)] == v
                for n, (node_attrs, edge_attrs) in ann2.items()
                for k, v in edge_attrs.items()])


def test_uds_graph():
    graph = setup_graph()

    assert graph.sentence == 'The police commander of Ninevah Province announced that bombings had declined 80 percent in Mosul , whereas there had been a big jump in the number of kidnappings .'

    assert graph.to_mrs() == mrs_str

    assert graph.to_dict() == graph.from_dict(graph.to_dict(), 'tree1').to_dict()

# def test_uds_corpus():
#     corpus = setup_corpus()
    
#     assert all([isinstance(t, DiGraph) for _, t in corpus.graphs.items()])
#     assert all([isinstance(t, DiGraph) for _, t in corpus]) # tests iterator
#     assert list(corpus) # tests iterator reset
