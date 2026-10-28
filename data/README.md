# Dataset format

The training script (`python -m ml.train_model`) reads a CSV file with these columns:

| column  | required | meaning |
| ------- | -------- | ------- |
| `text`  | yes | a short message written the way a student might write it |
| `label` | yes | one of the categories below (exact spelling) |
| `group` | no  | an id for sentences that are near-copies of each other (see below) |

Valid labels: `Academic Stress`, `Exam Anxiety`, `Time Management`, `Low Motivation`,
`Concentration Difficulties`, `General Emotional Stress`, `General or Unclassified Concern`.

Example:

```csv
text,label
I am worried about my upcoming exams,Exam Anxiety
I cannot manage all my assignments,Time Management
I have too much academic work,Academic Stress
```

Rows with missing text/label, unknown labels or duplicate text are dropped (the script prints how many).
Each label needs at least 5 rows.

## About `demo_dataset.csv`

`demo_dataset.csv` is **synthetic demonstration data** created by `generate_demo_dataset.py`
(hand-written sentences combined with small variations). It is **not** real student data and was **not**
reviewed by any mental-health professional. It exists so the project runs out of the box and so the
pipeline can be demonstrated. Accuracy figures measured on it say little about how the classifier would
behave on real messages, and nothing about any clinical question.

## Using a real dataset

Choose a labelled text dataset suited to this task (short messages mapped to these study-related
categories) and **check its licence and permitted uses before including or sharing it**. Survey
questionnaires with numeric answers are not message text and should not be used here. Copy your CSV into
this folder (for example `data/my_dataset.csv`) and run:

```
python -m ml.train_model --data data/my_dataset.csv
```

Private files in `data/` other than `demo_dataset.csv` are ignored by git on purpose.

## The `group` column and data leakage

If many rows are small variations of the same sentence, a random split would put near-copies in both the
training and test sets, making results look better than they are. When a `group` column exists, the split
keeps all rows with the same group on the same side. If you have no groups, leave the column out and a
normal stratified split is used (then please make sure your data has no near-duplicates).

## Privacy rule

Never add users' chat messages, mood notes or journal entries to this dataset. MindMate does not save chat
messages, and the training code does not read the application database.
