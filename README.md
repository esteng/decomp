# Overview

This package provides a toolkit for working with the Decomp graph-based semantic representation

# Installation

To install, simply use `pip`.

```bash
pip install git+git://gitlab.hltcoe.jhu.edu/aswhite/decomp.git
```

You can also clone and use the included `setup.py`.

```bash
git clone git://gitlab.hltcoe.jhu.edu/aswhite/decomp.git
cd decomp
python setup.py install
```

If you would like to install the package for the purposes of development, use:

```bash
git clone git://gitlab.hltcoe.jhu.edu/aswhite/decomp.git
cd decomp
python setup.py develop
```

# Reading UDS

The UDS corpus can be read using the `UDSCorpus` class.

```python
from os.path import basename
from glob import glob
from decomp.semantics.uds import UDSCorpus

# load UDS from JSON
uds = {basename(fpath): UDSCorpus.from_json(fpath)
       for fpath in glob('../data/uds-ewt-*.json')}
```
