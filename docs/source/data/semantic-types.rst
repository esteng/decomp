`Universal Decompositional Semantic`_ Types
===========================================

.. _Universal Decompositional Semantic: http://decomp.io/

PredPatt makes very coarse-grained typing distinctions—between predicate and argument nodes, on the one hand, and between dependency and head edges, on the other. UDS provides ultra fine-grained typing distinctions, represented as collections of real-valued attributes. The union of all node and edge attributes defined in UDS determines the *UDS type space*; any proper subset determines a *UDS type subspace*. 

UDS attributes are derived from crowd-sourced annotations of the heads or spans corresponding to predicates and/or arguments and are represented in the dataset as node and/or edge attributes. It is important to note that, though all nodes and edges in the semantics domain have a ``type`` attribute, UDS does not afford any special status to these types. That is, the only thing that UDS "sees" are the nodes and edges in the semantics domain. The set of nodes and edges visible to UDS is a superset of those associated with PredPatt predicates and their arguments.

There are currently four node type subspaces.

  - `Factuality`_
  - `Genericity`_
  - `Time`_
  - `Entity type`_

There is currently one edge type subspace.

  - `Semantic Proto-Roles`_

Factuality
----------

**Project page**

`<http://decomp.io/projects/factuality/>`_

**Attributes**

``factuality-factual``

**References**

White, A.S., D. Reisinger, K. Sakaguchi, T. Vieira, S. Zhang, R. Rudinger, K. Rawlins, & B. Van Durme. 2016. Universal Decompositional Semantics on Universal Dependencies. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, pages 1713–1723, Austin, Texas, November 1-5, 2016.

Rudinger, R., White, A.S., & B. Van Durme. 2018. Neural models of factuality. Proceedings of NAACL-HLT 2018, pages 731–744. New Orleans, Louisiana, June 1-6, 2018.

Genericity
----------

**Project page**

`<http://decomp.io/projects/genericity/>`_

**Attributes**

``genericity-arg-particular``, ``genericity-arg-kind``, ``genericity-arg-abstract``, ``genericity-pred-particular``, ``genericity-pred-dynamic``, ``genericity-pred-hypothetical``

**References**

Govindarajan, V.S., B. Van Durme, & A.S. White. 2019. Decomposing Generalization: Models of Generic, Habitual, and Episodic Statements. To appear in Transactions of the Association for Computational Linguistics.

Time
----

**Project page**

`<http://decomp.io/projects/time/>`_

**Attributes**

``time-dur-hours``, ``time-dur-instant``, ``time-dur-forever``, ``time-dur-weeks``, ``time-dur-days``, ``wordsense-supersense-noun.time``, ``time-dur-months``, ``time-dur-years``, ``time-dur-centuries``, ``time-dur-seconds``, ``time-dur-minutes``, ``time-dur-decades``

**References**

Vashishtha, S., B. Van Durme, & A.S. White. 2019. Fine-Grained Temporal Relation Extraction. To appear in Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics (ACL 2019), Florence, Italy, July 29-31, 2019.

Entity type
-----------

**Project page**

`<http://decomp.io/projects/word-sense/>`_

**Attributes**

``wordsense-supersense-noun.shape``, ``wordsense-supersense-noun.process``, ``wordsense-supersense-noun.relation``, ``wordsense-supersense-noun.communication``, ``wordsense-supersense-noun.time``, ``wordsense-supersense-noun.plant``, ``wordsense-supersense-noun.phenomenon``, ``wordsense-supersense-noun.animal``, ``wordsense-supersense-noun.state``, ``wordsense-supersense-noun.substance``, ``wordsense-supersense-noun.person``, ``wordsense-supersense-noun.possession``, ``wordsense-supersense-noun.Tops``, ``wordsense-supersense-noun.object``, ``wordsense-supersense-noun.event``, ``wordsense-supersense-noun.artifact``, ``wordsense-supersense-noun.act``, ``wordsense-supersense-noun.body``, ``wordsense-supersense-noun.attribute``, ``wordsense-supersense-noun.quantity``, ``wordsense-supersense-noun.motive``, ``wordsense-supersense-noun.location``, ``wordsense-supersense-noun.cognition``, ``wordsense-supersense-noun.group``, ``wordsense-supersense-noun.food``, ``wordsense-supersense-noun.feeling``

**References**

White, A.S., D. Reisinger, K. Sakaguchi, T. Vieira, S. Zhang, R. Rudinger, K. Rawlins, & B. Van Durme. 2016. Universal Decompositional Semantics on Universal Dependencies. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, pages 1713–1723, Austin, Texas, November 1-5, 2016.

Semantic Proto-Roles
--------------------

**Project page**

`<http://decomp.io/projects/semantic-proto-roles/>`_

**Attributes**

``protoroles-was_used``, ``protoroles-purpose``, ``protoroles-partitive``, ``protoroles-location``, ``protoroles-instigation``, ``protoroles-existed_after``, ``protoroles-time``, ``protoroles-awareness``, ``protoroles-change_of_location``, ``protoroles-manner``, ``protoroles-sentient``, ``protoroles-was_for_benefit``, ``protoroles-change_of_state_continuous``, ``protoroles-existed_during``, ``protoroles-change_of_possession``, ``protoroles-existed_before``, ``protoroles-volition``, ``protoroles-change_of_state``

**References**

White, A.S., D. Reisinger, K. Sakaguchi, T. Vieira, S. Zhang, R. Rudinger, K. Rawlins, & B. Van Durme. 2016. Universal Decompositional Semantics on Universal Dependencies. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, pages 1713–1723, Austin, Texas, November 1-5, 2016.

