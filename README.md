# Overview

This package provides a toolkit for working with the Decomp graph-based semantic representation

# Installation

We recommend building the decomp Docker image from the included
Dockerfile, which uses `jupyter/scipy-notebook` as its base image.

```bash
git clone git://gitlab.hltcoe.jhu.edu/aswhite/decomp.git
cd decomp
docker build -t decomp .
docker run -p 8888:8888 decomp start-notebook.sh
```

A jupyter notebook can then be opened in the standard way.

If you prefer to install directly to your local environment, simply
use `pip`.

```bash
pip install git+git://gitlab.hltcoe.jhu.edu/aswhite/decomp.git --process-dependency-links
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

The UDS corpus can be read by directly importing it.

```python
from decomp import uds
```
