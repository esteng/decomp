# Time (v1.0)

This archive contains data collected from the protocols described in the following paper.

Siddharth Vashishtha, Benjamin Van Durme, and Aaron Steven White. 2019. [Fine-Grained Temporal Relation Extraction](https://arxiv.org/pdf/1902.01390.pdf). [arXiv preprint 1902.01390](https://arxiv.org/abs/1902.01390). 

If you make use of this dataset in a presentation or publication, we ask that you please cite this paper.

## Contents

The file `time_eng_ud_v1.2_2015_10_30.tsv` corresponds to the data reported in Vashishtha et al. 2019. The file contains temporal relation annotations developed from the the [Universal Dependencies v1.2 dataset](https://github.com/UniversalDependencies/UD_English-EWT/releases/tag/r1.2). The document ids of the UDv1.2 sentences can be found in a [later version](https://github.com/UniversalDependencies/UD_English-EWT/blob/master/en_ewt-ud-train.conllu). 


The column descriptions and values for `time_eng_ud_v1.2_2015_10_30.tsv` can be found below.


| Column            | Description       | Values            |
|-------------------|-------------------|-------------------|
| Split | The dataset split to which annotation belongs | `train`, `dev`, `test` |
| Annotator.ID | The annotator that provided the response | `0`,.....,`764` |
| Sentence1.ID | The file and sentence number of the sentence corresponding to the first predicate (in linear order) in the English Universal Dependencies v1.2 treebank with the format `LANGUAGE-CORPUS-SPLIT.ANNOTATION SENTNUM` |  |
| Pred1.Span | The indices of all tokens of the first predicate	(in linear order)  (separated by '_') | see data |
| Pred1.Token | The index of the root of the first predicate (in linear order)  | `1`,.....,`155` |
| Event1.ID | The ID corresponding to the first event in the concatenated sentence. Equivalent to `Sentence1.ID_Pred1.Token` | see data |
| Sentence2.ID | The file and sentence number of the sentence corresponding to the second predicate (in linear order) in the English Universal Dependencies v1.2 treebank with the format `LANGUAGE-CORPUS-SPLIT.ANNOTATION SENTNUM` |  |
| Pred2.Span | The indices of all tokens of the second predicate (in linear order)  (separated by '_') | see data |
| Pred2.Token | The index of the root of the second predicate (in linear order)  | `1`,.....,`155` |
| Event2.ID | The ID corresponding to the second event in the concatenated sentence. Equivalent to `Sentence2.ID_Pred2.Token` | see data |
| Pred1.Text | The text of the predicate span of the first predicate. | see data |
| Pred1.Lemma | The lemma of the root of the first predicate. | see data |
| Pred2.Text | The text of the predicate span of the second predicate. | see data |
| Pred2.Lemma | The lemma of the root of the second predicate. | see data |
| Pred1.Duration | The duration label annotated for the first predicate. | see data |
| Pred2.Duration | The duration label annotated for the second predicate. | see data |
| Pred1.Beg | The annotated beginning point of the first predicate (in linear order). A value between 0 and 100| see data |
| Pred1.End | The annotated end point of the first predicate (in linear order). A value between 0 and 100 | see data |
| Pred2.Beg | The annotated beginning point of the second predicate (in linear order). A value between 0 and 100| see data |
| Pred2.End | The annotated end point of the second predicate (in linear order). A value between 0 and 100 | see data |
| Pred1.Duration.Confidence | How confident was the annotator in labelling the duration annotation for the first predicate | `0`, `1`, `2`, `3`, `4` |
| Pred2.Duration.Confidence | How confident was the annotator in labelling the duration annotation for the second predicate | `0`, `1`, `2`, `3`, `4` |
| Relation.Confidence | How confident was the annotator in labelling the beginning and end points of the first and the second predicate | `0`, `1`, `2`, `3`, `4` |
| Document.ID | The document ID corresponding to the current Split, containing both Sentence1 and Sentence2 | see data |

## Notes

As mentioned in the paper, we refer to the situation referred to by the predicate that comes first in linear order as e1 and the situation referred to by the predicate that comes second in linear order as e2. 
`Sentence1.ID` correponds to the file and sentence number of the situation e1, and `Sentence2.ID` correponds to the file and sentence number of the situation e2. 

Note that `Sentence1.ID` and `Sentence2.ID` are either going to be equal to each other or `Sentence2.ID` will be the next sentence after `Sentence1.ID` in a document. This is because we concatenate every two consecutive sentences in a document to capture inter-sentential temporal relations. See paper for more details.