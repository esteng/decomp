Reading the UDS dataset
=======================

The most straightforward way to read the Universal Decompositional
Semantics (UDS) dataset is to import it.

.. code-block:: python

   from decomp import uds

This imports a `UDSCorpus`_ object ``uds``, which contains all
graphs across all splits in the data.

.. _UDSCorpus: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSCorpus

As noted in :doc:`quick-start`, the first time you do this import, it
will take several minutes to complete while the dataset is built from
the `Universal Dependencies English Web Treebank`_ (UD-EWT), which is not
shipped with the package (but is downloaded automatically on import in
the background), and the `UDS annotations`_, which are shipped with
the package as package data. Subsequent uses will be faster, since the
built dataset is cached.

.. _Universal Dependencies English Web Treebank: https://github.com/UniversalDependencies/UD_English-EWT
.. _UDS annotations: http://decomp.io/data/

If you would rather read only the graphs in the training, development,
or test split, you can do that by specifying the ``split`` parameter
of ``UDSCorpus``.

.. code-block:: python

   from decomp import UDSCorpus

   # read the train split of the UDS corpus
   uds_train = UDSCorpus(split='train')

Additional annotations beyond the standard UDS annotations can be
added using this method by passing a list of `UDSAnnotation`_
objects. ``UDSAnnotation`` objects are loaded from JSON-formatted
files that represent a dictionary mapping node identifiers or pairs of
node identifiers separated by a ``_`` to a dictionary of
attribute-value pairs. For example, if you have some additional
annotations in a file ``new_annotations.json``, those can be added to
the existing UDS annotations using:

.. _UDSAnnotation: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSAnnotation

.. code-block:: python

   # read annotations
   new_annotations = [UDSAnnotation.from_json("new_annotations.json")]

   # read the train split of the UDS corpus and append new annotations
   uds_train_plus = UDSCorpus(split='train', annotations=new_annotations)

Importantly, these annotations are added *in addition* to the existing
UDS annotations that ship with the toolkit. You do not need to add
these manually.

If you would like to read the dataset from an alternative
location—e.g. if you have serialized the dataset to JSON, using the
`to_json`_ instance method—this can be accomplished using
``UDSCorpus`` class methods. For example, if you serialize
``uds_train`` to a file ``uds-ewt-train.json``, you can read it back
into memory using:

.. _to_json: ../package/decomp.semantics.uds.html#decomp.semantics.uds.UDSCorpus.to_json

.. code-block:: python

   # serialize uds_train to JSON
   uds_train.to_json("uds-ewt-train.json")

   # read JSON serialized uds_train
   uds_train = UDSCorpus.from_json("uds-ewt-train.json")   

If you would like to rebuild the corpus from the UD-EWT CoNLL files
and some set of JSON-formatted annotation files, you can use the
analogous ``from_conll`` class method. Importantly, unlike the
standard instance initialization described above, the UDS annotations
are *not* automatically added. For example, if ``en-ud-train.conllu``
is in the current working directory and you have already loaded
``new_annotations`` as above, a corpus containing only those
annotations (without the UDS annotations) can be loaded using:

.. code-block:: python

   # read the train split of the UD corpus and append new annotations
   ud_train_annotated = UDSCorpus.from_conll("en-ud-train.conllu", new_annotations)   

This also means that if you only want the semantic graphs as implied
by PredPatt (without annotations), you can use the ``from_conll``
class method to load them.

.. code-block:: python

   # read the train split of the UD corpus
   ud_train = UDSCorpus.from_conll("en-ud-train.conllu")   
