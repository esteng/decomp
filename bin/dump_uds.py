import logging
from os.path import basename
from decomp.semantics.uds import UDSCorpus

logging.basicConfig(level=logging.INFO)


def build_name(fname):
    """Build the name of the corpus split

    This name will be used as a prefix in node ids.

    Parameters
    ----------
    fname : str
        name of the form en-ud-SPLIT.conllu
    """
    return 'ewt-'+basename(fname).split('.')[0].split('-')[2]


# load UDS
uds = {fname: UDSCorpus.from_conll('../data/UD_English-r1.2/'+fname,
                                   ['../data/protoroles/protoroles.json',
                                    '../data/factuality/factuality.json',
                                    '../data/genericity/genericity.json',
                                    '../data/time/time.json',
                                    '../data/wordsense/wordsense.json'],
                                   name=build_name(fname))
       for fname in ['en-ud-train.conllu',
                     'en-ud-dev.conllu',
                     'en-ud-test.conllu']}

# dump to JSON
for fname, corpus in uds.items():
    split = fname.strip('.conllu').split('-')[2]
    uds[fname].to_json('../data/uds-ewt-'+split+'.json')
