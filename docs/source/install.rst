.. _install:

============
Installation
============

Decomp can be installed using ``pip``.

.. code-block:: bash

   pip install git+git://github.com/decompositional-semantics-initiative/decomp.git


You can also clone and use the included ``setup.py`` with the ``install`` flag.

.. code-block:: bash

   git clone https://github.com/decompositional-semantics-initiative/decomp.git
   cd decomp
   python setup.py install


If you would like to install the package for the purposes of development, you can use the included ``setup.py`` with the ``develop`` flag.

.. code-block:: bash

   git clone https://github.com/decompositional-semantics-initiative/decomp.git
   cd decomp
   python setup.py develop


If anyone has trouble with installing via setup.py or pip on OsX Mojave, adding the following environment variables  may help:

.. code-block:: bash 

    CXXFLAGS=-stdlib=libc++ CFLAGS=-stdlib=libc++ python setup.py install



