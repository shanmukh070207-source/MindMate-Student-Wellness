"""Train, evaluate and save the MindMate text classifier.

Usage (from the MindMate folder):
    python -m ml.train_model
    python -m ml.train_model --data data/my_dataset.csv

The dataset must be a CSV with 'text' and 'label' columns. An optional 'group'
column keeps near-duplicate sentences on the same side of the train/test split.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import accuracy_score, classification_report  # noqa: E402
from sklearn.model_selection import GroupShuffleSplit, train_test_split  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402

from config import BASE_DIR, Config  # noqa: E402
from ml.response_library import CATEGORIES  # noqa: E402

DEFAULT_DATA = os.path.join(BASE_DIR, "data", "demo_dataset.csv")
REQUIRED_COLUMNS = ["text", "label"]
MIN_ROWS_PER_CLASS = 5


class DatasetError(Exception):
    """Raised when the dataset is missing or not in the expected format."""


def load_dataset(path):
    """Load and validate the dataset. Returns a cleaned DataFrame."""
    if not os.path.exists(path):
        raise DatasetError(f"Dataset not found at '{path}'. See data/README.md for the expected format.")
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise DatasetError(f"Could not read the dataset as CSV: {exc}") from exc

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DatasetError(f"Dataset is missing required column(s): {', '.join(missing)}")

    before = len(df)
    df = df.dropna(subset=REQUIRED_COLUMNS).copy()
    df["text"] = df["text"].astype(str).str.strip()
    df["label"] = df["label"].astype(str).str.strip()
    df = df[df["text"] != ""]

    unknown = sorted(set(df["label"]) - set(CATEGORIES))
    if unknown:
        print(f"Warning: dropping rows with unknown labels: {unknown}")
        df = df[df["label"].isin(CATEGORIES)]

    df = df.drop_duplicates(subset=["text"])
    print(f"Rows kept: {len(df)} of {before} (removed missing, empty, unknown-label and duplicate rows)")

    counts = df["label"].value_counts()
    if counts.empty:
        raise DatasetError("No valid rows left after cleaning.")
    if len(counts) < 2:
        raise DatasetError("At least two different labels are needed to train a classifier.")
    too_small = counts[counts < MIN_ROWS_PER_CLASS]
    if not too_small.empty:
        raise DatasetError(f"Each label needs at least {MIN_ROWS_PER_CLASS} rows. Too few: {too_small.to_dict()}")
    return df.reset_index(drop=True)


def split_dataset(df, seed=42):
    """Hold out 25% for testing, grouping by sentence core when possible."""
    if "group" in df.columns and df["group"].notna().all():
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=seed)
        train_idx, test_idx = next(splitter.split(df["text"], df["label"], groups=df["group"]))
        return df.iloc[train_idx], df.iloc[test_idx]
    return train_test_split(df, test_size=0.25, random_state=seed, stratify=df["label"])


def build_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), sublinear_tf=True, min_df=1)),
        ("clf", LogisticRegression(max_iter=1000, C=2.0)),
    ])


def choose_threshold(y_true, probabilities, classes, target_precision=0.85, min_coverage=0.5):
    """Pick the lowest confidence threshold at which accepted predictions are
    at least `target_precision` correct on the held-out test set, while still
    answering at least `min_coverage` of the messages. The result is an
    estimate from a small test set, not a guarantee."""
    y_true = np.array(y_true)
    predicted = np.array(classes)[probabilities.argmax(axis=1)]
    confidence = probabilities.max(axis=1)
    best = None
    for t in np.arange(0.20, 0.91, 0.05):
        accepted = confidence >= t
        coverage = accepted.mean()
        if accepted.sum() == 0:
            continue
        precision = (predicted[accepted] == y_true[accepted]).mean()
        if precision >= target_precision and coverage >= min_coverage:
            best = (round(float(t), 2), float(precision), float(coverage))
            break
    if best is None:
        best = (0.5, None, None)  # conservative default if the target cannot be met
    return best


def train(data_path=DEFAULT_DATA, model_path=Config.MODEL_PATH, metrics_path=Config.METRICS_PATH):
    df = load_dataset(data_path)
    print("\nCategory distribution:")
    print(df["label"].value_counts().to_string())

    train_df, test_df = split_dataset(df)
    # Leakage check: no identical text on both sides.
    assert not set(train_df["text"]) & set(test_df["text"]), "Train/test leakage detected"
    print(f"\nTrain rows: {len(train_df)}  Test rows: {len(test_df)}")

    pipeline = build_pipeline()
    pipeline.fit(train_df["text"], train_df["label"])

    predictions = pipeline.predict(test_df["text"])
    probabilities = pipeline.predict_proba(test_df["text"])
    accuracy = accuracy_score(test_df["label"], predictions)
    report = classification_report(test_df["label"], predictions, output_dict=True, zero_division=0)
    print(f"\nHeld-out accuracy: {accuracy:.3f}")
    print(classification_report(test_df["label"], predictions, zero_division=0))

    threshold, precision, coverage = choose_threshold(
        test_df["label"], probabilities, pipeline.classes_
    )
    print(f"Chosen confidence threshold: {threshold} "
          f"(precision above threshold: {precision}, share of messages answered: {coverage})")

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump({"pipeline": pipeline, "threshold": threshold, "labels": list(pipeline.classes_)}, model_path)

    metrics = {
        "data_file": os.path.basename(data_path),
        "rows_total": int(len(df)),
        "rows_train": int(len(train_df)),
        "rows_test": int(len(test_df)),
        "accuracy": round(float(accuracy), 4),
        "threshold": threshold,
        "precision_above_threshold": precision,
        "coverage_above_threshold": coverage,
        "per_class": {k: {m: round(float(v), 3) for m, v in vals.items()}
                      for k, vals in report.items() if isinstance(vals, dict)},
        "note": ("Measured on a held-out split of the supplied dataset only. "
                 "If the demonstration dataset was used, these numbers are not meaningful "
                 "for real student messages."),
    }
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nModel saved to {model_path}\nMetrics saved to {metrics_path}")
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Train the MindMate classifier.")
    parser.add_argument("--data", default=DEFAULT_DATA, help="Path to the labelled CSV file")
    args = parser.parse_args()
    try:
        train(args.data)
    except DatasetError as exc:
        print(f"Training stopped: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
