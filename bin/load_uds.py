from os.path import basename
from glob import glob
from decomp.semantics.uds import UDSCorpus

uds = {fname: UDSCorpus.from_file('../data/UD_English-r1.2/'+fname,
                                  ['../data/protoroles/protoroles.json',
                                   '../data/factuality/factuality.json',
                                   '../data/genericity/genericity.json',
                                   '../data/time/time.json',
                                   '../data/wordsense/wordsense.json'],
                                  name='ewt-'+basename(fname).split('.')[0].split('-')[2])
       for fname in ['en-ud-train.conllu','en-ud-dev.conllu','en-ud-test.conllu']}

for fname, corpus in uds.items():
    split = fname.strip('.conllu').split('-')[2]
    uds[fname].to_json('../data/uds-ewt-'+split+'.json')

for fname, corpus in uds.items():
    split = fname.strip('.conllu').split('-')[2]
    uds[fname].to_mrs('../data/uds-ewt-'+split+'.mrs')    

uds = {basename(fpath): UDSCorpus.from_json(fpath)
       for fpath in glob('../data/uds-ewt-*.json')}
