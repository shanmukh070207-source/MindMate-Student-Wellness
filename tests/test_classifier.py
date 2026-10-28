import json
import os

import pytest

from ml import train_model
from ml.predict import Classifier, InvalidMessageError, ModelNotAvailableError, clean_message
from ml.response_library import CATEGORIES, NEUTRAL_CATEGORY, RESPONSES, get_response, has_response
from ml.safety import check_safety


@pytest.fixture(scope="module")
def classifier(trained_paths):
    return Classifier.load(trained_paths[0])


def test_model_loads_and_has_threshold(classifier):
    assert 0.2 <= classifier.threshold <= 0.95


def test_valid_text_gives_supported_category(classifier):
    category, confidence = classifier.predict("I am so nervous about my exam tomorrow")
    assert category in CATEGORIES and 0 < confidence <= 1


def test_clear_messages_get_matching_categories(classifier):
    assert classifier.respond("I'm scared I will fail the physics exam")["category"] == "Exam Anxiety"
    assert classifier.respond("I can't concentrate on my books, my mind keeps wandering")["category"] == "Concentration Difficulties"


def test_respond_returns_message_and_actions(classifier):
    result = classifier.respond("I have too many assignments and don't know where to start")
    assert result["message"] and result["actions"] and result["safety"] is False


def test_empty_and_whitespace_rejected(classifier):
    for bad in ["", "   ", "\n\t"]:
        with pytest.raises(InvalidMessageError):
            classifier.respond(bad)


def test_unexpected_input_rejected(classifier):
    for bad in [None, 123, ["a"], {"x": 1}]:
        with pytest.raises(InvalidMessageError):
            classifier.respond(bad)
    with pytest.raises(InvalidMessageError):
        clean_message("a" * 5000)


def test_gibberish_and_symbols_do_not_crash(classifier):
    for text in ["asdkjh qweoiu zxcmn", "!!!???", "😀😀😀", "x" * 900]:
        result = classifier.respond(text)
        assert result["message"]


def test_uncertain_prediction_gets_neutral_response(classifier):
    classifier.threshold, original = 1.01, classifier.threshold   # nothing can reach this
    try:
        result = classifier.respond("I am worried about my upcoming exams")
    finally:
        classifier.threshold = original
    assert result["category"] == NEUTRAL_CATEGORY and result["reliable"] is False
    assert result["message"] in RESPONSES[NEUTRAL_CATEGORY]["messages"]


def test_missing_model_file_gives_clear_error(tmp_path):
    with pytest.raises(ModelNotAvailableError) as info:
        Classifier.load(str(tmp_path / "nope.joblib"))
    assert "train" in str(info.value).lower()


def test_corrupt_model_file_gives_clear_error(tmp_path):
    bad = tmp_path / "bad.joblib"
    bad.write_text("not a model")
    with pytest.raises(ModelNotAvailableError):
        Classifier.load(str(bad))


def test_category_without_response_falls_back_to_neutral():
    assert not has_response("Made Up Category")
    assert get_response("Made Up Category")["category"] == NEUTRAL_CATEGORY


def test_every_category_has_several_responses():
    for category in CATEGORIES:
        assert has_response(category) and len(RESPONSES[category]["messages"]) >= 3


def test_labels_in_model_match_category_list(classifier):
    assert set(classifier.pipeline.classes_) <= set(CATEGORIES)


# ---- dataset and training checks ----
def test_missing_dataset(tmp_path):
    with pytest.raises(train_model.DatasetError):
        train_model.load_dataset(str(tmp_path / "missing.csv"))


def test_dataset_missing_columns(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("sentence,category\nhello,Academic Stress\n")
    with pytest.raises(train_model.DatasetError) as info:
        train_model.load_dataset(str(p))
    assert "text" in str(info.value)


def test_dataset_cleaning_drops_bad_rows(tmp_path):
    lines = ["text,label"]
    for i in range(6):
        lines += [f"exam worry {i},Exam Anxiety", f"no motivation {i},Low Motivation"]
    lines += [",Exam Anxiety", "blank label,", "weird label,Not A Category", "exam worry 0,Exam Anxiety"]
    p = tmp_path / "d.csv"
    p.write_text("\n".join(lines) + "\n")
    df = train_model.load_dataset(str(p))
    assert len(df) == 12 and set(df["label"]) == {"Exam Anxiety", "Low Motivation"}


def test_dataset_with_one_label_rejected(tmp_path):
    p = tmp_path / "one.csv"
    p.write_text("text,label\n" + "\n".join(f"worried {i},Exam Anxiety" for i in range(10)) + "\n")
    with pytest.raises(train_model.DatasetError):
        train_model.load_dataset(str(p))


def test_not_a_csv_rejected(tmp_path):
    p = tmp_path / "x.csv"
    p.write_bytes(b"\x00\x01\x02")
    with pytest.raises(train_model.DatasetError):
        train_model.load_dataset(str(p))


def test_no_leakage_between_train_and_test():
    df = train_model.load_dataset(train_model.DEFAULT_DATA)
    train_df, test_df = train_model.split_dataset(df)
    assert not set(train_df["text"]) & set(test_df["text"])
    assert not set(train_df["group"]) & set(test_df["group"])


def test_metrics_file_written(trained_paths):
    metrics = json.load(open(trained_paths[1]))
    assert 0 <= metrics["accuracy"] <= 1 and metrics["rows_test"] > 0


# ---- safety ----
@pytest.mark.parametrize("text", [
    "I want to kill myself", "i don't want to be alive anymore", "thinking about suicide",
    "I wish I was dead", "I keep hurting myself",
])
def test_safety_phrases_detected(text):
    assert check_safety(text)


@pytest.mark.parametrize("text", ["I'm dying to finish this assignment", "this exam will kill me lol", "I am stressed", ""])
def test_ordinary_text_not_flagged(text):
    assert not check_safety(text)


def test_safety_response_bypasses_classifier(classifier):
    class Boom:
        def predict_proba(self, _):
            raise AssertionError("classifier must not be used for safety messages")
        classes_ = []
    broken = Classifier(Boom(), 0.5)
    result = broken.respond("I want to end my life")
    assert result["safety"] is True and "14416" in result["message"]


def test_chat_endpoint_flow(auth_client):
    ok = auth_client.post("/chat/message", json={"message": "I'm so nervous about my exams"})
    assert ok.status_code == 200 and ok.get_json()["message"]
    assert auth_client.post("/chat/message", json={"message": "   "}).status_code == 400
    assert auth_client.post("/chat/message", data="not json", content_type="text/plain").status_code == 400
    crisis = auth_client.post("/chat/message", json={"message": "I want to die"}).get_json()
    assert crisis["safety"] is True and crisis["contacts"]


def test_chat_requires_login(client):
    assert client.post("/chat/message", json={"message": "hi"}).status_code == 302


def test_chat_page_shows_setup_error_when_model_missing(tmp_path):
    from app import create_app
    app = create_app({"TESTING": True, "TESTING_SKIP_CSRF": True, "DATABASE": str(tmp_path / "m.sqlite3"),
                      "MODEL_PATH": str(tmp_path / "missing.joblib")})
    c = app.test_client()
    c.post("/register", data={"username": "gina_g", "password": "password123", "confirm": "password123"})
    c.post("/login", data={"username": "gina_g", "password": "password123"})
    page = c.get("/chat").data
    assert b"Chat is not available yet" in page and b"ml.train_model" in page
    assert c.post("/chat/message", json={"message": "hello"}).status_code == 503
