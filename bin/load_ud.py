from os.path import basename
from decomp.semantics.predpatt import PredPattCorpus

predpatt = {fname: PredPattCorpus.from_file('../data/UD_English-r1.2/'+fname,
                                            name='ewt-'+basename(fname).split('.')[0].split('-')[2])
            for fname in ['en-ud-train.conllu','en-ud-dev.conllu','en-ud-test.conllu']}
