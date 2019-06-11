from os.path import basename
from glob import glob
from decomp.semantics.uds import UDSCorpus

# load UDS from JSON
uds = {basename(fpath): UDSCorpus.from_json(fpath)
       for fpath in glob('../data/uds-ewt-*.json')}
