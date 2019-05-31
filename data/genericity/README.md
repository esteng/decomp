# Genericity (v1.0)

This archive contains data collected from the protocols described in the following paper.

V. S. Govindarajan, B. Van Durme, & White, A. S. 2019. [Decomposing Generalization: Models of Generic, Habitual, and Episodic Statements](https://arxiv.org/abs/1901.11429).

If you make use of this data set in a presentation or publication, we ask that you please cite this paper.

There are four files: `arg_long_data.tsv`, `arg_norm_data.tsv`, `pred_long_data.tsv`, and `pred_norm_data.tsv`. The first two contain annotations for arguments in sentences from the [Universal Dependencies v1.2 dataset](https://github.com/UniversalDependencies/UD_English-EWT/releases/tag/r1.2), and the latter two contain annotations for predicates. The `long` datasets contain raw annotations with the annotation confidence measures, while the `norm` datasets contain the data after normalisation (which is described in the paper).

The column descriptions and values for `arg_long_data.tsv` can be found below.

| Column            | Description       | Values            |
|-------------------|-------------------|-------------------|
| Split | The dataset split to which annotation belongs | `train`, `dev`, `test` |
| Annotator.ID | The annotator that provided the response | `1`,.....,`100` |
| Sentence.ID | The file and sentence number of the sentence in the English Universal Dependencies v1.2 treebank with the format `LANGUAGE-CORPUS-SPLIT.ANNOTATION SENTNUM` |  |
| Arg.Token | The root argument index in the sentence | `1`,.....,`157` |
| Arg.Span | The indices of all tokens in the argument span (comma separated) | see data |
| Pred.Token | The index of the root of the governing predicate | `1`,.....,`155` |
| Pred.Span | The indices of all tokens in the governing predicate span (comma separated) | see data |
| Arg.Word | The argument token | see data |
| Arg.Lemma | The argument lemma | see data |
| Is.Particular | The particular property annotation | `True, False` |
| Part.Confidence | The 5-point Likert scale annotation confidence of the property | `0, 1, 2, 3, 4` |
| Is.Kind | The kind property annotation | `True, False` |
| Kind.Confidence | The 5-point Likert scale annotation confidence of the property | `0, 1, 2, 3, 4` |
| Is.Abstract | The abstract property annotation | `True, False` |
| Abs.Confidence | The 5-point Likert scale annotation confidence of the property | `0, 1, 2, 3, 4` |


The column descriptions and values for `arg_norm_data.tsv` can be found below.

| Column            | Description       | Values            |
|-------------------|-------------------|-------------------|
| Split | The dataset split to which annotation belongs | `train`, `dev`, `test` |
| Annotator.ID | The annotator that provided the response | `1`,.....,`100` |
| Sentence.ID | The file and sentence number of the sentence in the English Universal Dependencies v1.2 treebank with the format `LANGUAGE-CORPUS-SPLIT.ANNOTATION SENTNUM` |  |
| Arg.Token | The root argument index in the sentence | `1`,.....,`157` |
| Arg.Span | The indices of all tokens in the argument (comma separated) | see data |
| Is.Particular.Norm | The normalised particular score | `[-3.77, 3.79]` |
| Is.Kind.Norm | The normalised kind score | `[-4.25, 3.66]` |
| Is.Abstract.Norm | The normalised abstract score | `[--5.46, 3.83]` |

The column descriptions and values for `pred_long_data.tsv` can be found below.

| Column            | Description       | Values            |
|-------------------|-------------------|-------------------|
| Split | The dataset split to which annotation belongs | `train`, `dev`, `test` |
| Annotator.ID | The annotator that provided the response | `1`,.....,`437` |
| Sentence.ID | The file and sentence number of the sentence in the English Universal Dependencies v1.2 treebank with the format `LANGUAGE-CORPUS-SPLIT.ANNOTATION SENTNUM` |  |
| Pred.Token | The root predicate index | `1`,.....,`155` |
| Ann.Token | The index of the tokens highlighted to annotators (subset of Pred.Span) | see data |
| Pred.Span | The indices of all tokens in the predicate (comma separated) | see data |
| Arg.Token | The index of the root in all dependent arguments (comma separated) | see data |
| Arg.Span | The indices of all tokens in the dependent arguments (semicolon separated for each dependent and comma separated within a dependent)| see data |
| Pred.Word | The predicate token | see data |
| Pred.Lemma | The predicate lemma | see data |
| Is.Particular | The particular property annotation | `True, False` |
| Part.Confidence | The 5-point Likert scale annotation confidence of the property | `0, 1, 2, 3, 4` |
| Is.Dynamic | The dynamic property annotation | `True, False` |
| Dyn.Confidence | The 5-point Likert scale annotation confidence of the property | `0, 1, 2, 3, 4` |
| Is.Hypothetical | The hypothetical property annotation | `True, False` |
| Hyp.Confidence | The 5-point Likert scale annotation confidence of the property | `0, 1, 2, 3, 4` |

The column descriptions and values for `pred_norm_data.tsv` can be found below.

| Column            | Description       | Values            |
|-------------------|-------------------|-------------------|
| Split | The dataset split to which annotation belongs | `train`, `dev`, `test` |
| Annotator.ID | The annotator that provided the response | `1`,.....,`437` |
| Sentence.ID | The file and sentence number of the sentence in the English Universal Dependencies v1.2 treebank with the format `LANGUAGE-CORPUS-SPLIT.ANNOTATION SENTNUM` |  |
| Pred.Token | The index of the root of the governing predicate | `1`,.....,`155` |
| Pred.Span | The indices of all tokens in the governing predicate | see data |
| Is.Particular.Norm | The normalised particular score | `[-3.22, 4.56]` |
| Is.Dynamic.Norm | The normalised dynamic score | `[-4.11, 3.95]` |
| Is.Hypothetical.Norm | The normalised hypothetical score | `[-3.98, 3.83]` |

NOTE: The `pred_norm_data.tsv` file contains 3 fewer annotations than the `pred_long_data.tsv` file, since one of the predicates in the validation set (each of which is annotated by 3 predicates) had NULL values in the Arg.Token and Arg.Span columns (as identified by [PredPatt](https://github.com/hltcoe/PredPatt)). These annotations were dropped for the purposes of training models.