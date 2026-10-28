"""Load the trained pipeline once and classify chat messages.

Keeping this separate from Flask means the classifier can be reused and tested
without starting the web app.
"""
import logging
import os

import joblib

from ml.response_library import CATEGORIES, NEUTRAL_CATEGORY, get_response, has_response
from ml.safety import check_safety, safety_response

log = logging.getLogger(__name__)

MAX_LENGTH = 1000


class ModelNotAvailableError(Exception):
    """Raised when the trained model file is missing or unreadable."""


class InvalidMessageError(ValueError):
    """Raised when a chat message is empty or not usable text."""


def clean_message(text, max_length=MAX_LENGTH):
    """Validate a message and return it with tidy whitespace."""
    if not isinstance(text, str):
        raise InvalidMessageError("Please type a message.")
    text = " ".join(text.split())
    if not text:
        raise InvalidMessageError("Please type a message before sending.")
    if len(text) > max_length:
        raise InvalidMessageError(f"Please keep your message under {max_length} characters.")
    return text


class Classifier:
    """Wraps the saved scikit-learn pipeline (TF-IDF + Logistic Regression)."""

    def __init__(self, pipeline, threshold, categories=None):
        self.pipeline = pipeline
        self.threshold = float(threshold)
        self.categories = list(categories or CATEGORIES)

    @classmethod
    def load(cls, model_path):
        if not model_path or not os.path.exists(model_path):
            raise ModelNotAvailableError(
                "The chat model has not been trained yet. Run 'python -m ml.train_model' "
                "from the project folder, then restart the app."
            )
        try:
            bundle = joblib.load(model_path)  # only load files you trained yourself
            return cls(bundle["pipeline"], bundle["threshold"], bundle.get("labels"))
        except Exception as exc:
            log.exception("Could not read model file")
            raise ModelNotAvailableError(
                "The chat model file could not be read. Please retrain it with 'python -m ml.train_model'."
            ) from exc

    def predict(self, text):
        """Return (category, confidence) for a cleaned message."""
        probabilities = self.pipeline.predict_proba([text])[0]
        classes = list(self.pipeline.classes_)
        best = int(probabilities.argmax())
        category = classes[best]
        confidence = float(probabilities[best])
        if category not in self.categories:
            raise ValueError("Unexpected category from the model.")
        return category, confidence

    def respond(self, text, rng=None):
        """Full chat workflow for one message. Returns a dict for the chat page."""
        text = clean_message(text)

        # Safety check first. It never depends on the classifier.
        if check_safety(text):
            return safety_response()

        category, confidence = self.predict(text)
        reliable = confidence >= self.threshold and category != NEUTRAL_CATEGORY

        # Uncertain, or a category with no configured reply -> neutral reply.
        if not reliable or not has_response(category):
            result = get_response(NEUTRAL_CATEGORY, rng) if rng else get_response(NEUTRAL_CATEGORY)
            result["reliable"] = False
        else:
            result = get_response(category, rng) if rng else get_response(category)
            result["reliable"] = True

        result["confidence"] = round(confidence, 2)
        result["safety"] = False
        return result
