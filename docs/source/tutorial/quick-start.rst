Quick Start
===========

To read the Universal Decompositional Semantics (UDS) dataset, use:

.. code-block:: python

   from decomp import uds

This imports a `UDSCorpus`_ object ``uds``, which contains all
graphs across all splits in the data. If you would like a corpus,
e.g., containing only a particular split, see other loading options in
:doc:`reading`.

.. _UDSCorpus: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSCorpus

The first time you do this import, it will take several minutes to
complete while the dataset is built from the `Universal Dependencies
English Web Treebank`_, which is not shipped with the package (but is
downloaded automatically on import in the background), and the `UDS
annotations`_, which are shipped with the package. Subsequent uses
will be faster, since the built dataset is cached.

.. _Universal Dependencies English Web Treebank: https://github.com/UniversalDependencies/UD_English-EWT
.. _UDS annotations: http://decomp.io/data/

`UDSGraph`_ objects in the corpus can be accessed using standard
dictionary getters or iteration.

.. _UDSGraph: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSGraph

.. code-block:: python

   # the UDS graph corresponding to the 12th sentence in
   # en-ud-train.conllu
   uds["ewt-train-12"]

   # prints all the graph identifiers in the corpus
   # (e.g. "ewt-train-12")
   for graphid in uds:
       print(graphid)

   # prints all the graph identifiers in the corpus
   # (e.g. "ewt-train-12") along with the corresponding sentence
   for graphid, graph in uds.items():
       print(graphid)
       print(graph.sentence)
       
A list of graph identifiers can be accessed via the ``graphids``
attribute of the UDSCorpus. A mapping from these identifiers and the
corresponding graph can be accessed via the ``graphs`` attribute.

.. code-block:: python

   # a list of the graph identifiers in the corpus
   uds.graphids

   # a dictionary mapping the graph identifiers to the
   # corresponding graph
   uds.graphs

There are various instance attributes and methods for accessing nodes, edges, and their attributes in the UDS graphs.

.. code-block:: python

   # the UDS graph corresponding to the 12th sentence in
   # en-ud-train.conllu
   graph = uds["ewt-train-12"]

   # a dictionary mapping identifiers for syntax nodes in the UDS
   # graph to their attributes
   graph.syntax_nodes

   # a dictionary mapping identifiers for semantics nodes in the UDS
   # graph to their attributes
   graph.semantics_nodes   

   # a dictionary mapping identifiers for semantics edges (tuples of
   # node identifiers) in the UDS graph to their attributes
   graph.semantics_edges()

   # a dictionary mapping identifiers for semantics edges (tuples of
   # node identifiers) in the UDS graph involving the predicate headed
   # by the 7th token to their attributes
   graph.semantics_edges('ewt-train-12-semantics-pred-7')

   # a dictionary mapping identifiers for syntax edges (tuples of
   # node identifiers) in the UDS graph to their attributes
   graph.syntax_edges()

   # a dictionary mapping identifiers for syntax edges (tuples of
   # node identifiers) in the UDS graph involving the node for
   # the 7th token to their attributes
   graph.syntax_edges('ewt-train-12-syntax-7')
		

There are also methods for accessing relationships between semantics and syntax nodes.

.. code-block:: python

   # a tuple of ordinal position for the head syntax node in the UDS
   # graph that make of the predicate headed by the 7th token in the
   # corresponding sentence to a list of the form and lemma attributes
   # for that token
   graph.head('ewt-train-12-semantics-pred-7', ['form', 'lemma'])

   # a dictionary mapping ordinal position for syntax nodes in the UDS
   # graph that make of the predicate headed by the 7th token in the
   # corresponding sentence to a list of the form and lemma attributes
   # for the corresponding tokens
   graph.span('ewt-train-12-semantics-pred-7', ['form', 'lemma'])
		
All of these methods are built on top of the ``query`` method, which accepts arbitrary SPARQL 1.1 queries. See :doc:`querying` for details.  
