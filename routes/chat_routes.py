"""Supportive chat. Messages are classified and answered but NEVER stored."""
import logging

from flask import Blueprint, current_app, jsonify, render_template, request, url_for

from ml.predict import InvalidMessageError
from ml.response_library import DISCLAIMER
from ml.safety import SUPPORT_CONTACTS
from routes.auth_routes import login_required

bp = Blueprint("chat", __name__)
log = logging.getLogger(__name__)


@bp.route("/chat")
@login_required
def chat():
    return render_template(
        "chat.html",
        model_error=current_app.extensions.get("classifier_error"),
        disclaimer=DISCLAIMER,
    )


@bp.route("/safety")
def safety_info():
    return render_template("safety.html", contacts=SUPPORT_CONTACTS)


@bp.route("/chat/message", methods=["POST"])
@login_required
def chat_message():
    classifier = current_app.extensions.get("classifier")
    if classifier is None:
        return jsonify({"error": current_app.extensions.get("classifier_error")
                        or "The chat model is not available."}), 503

    data = request.get_json(silent=True)
    text = data.get("message") if isinstance(data, dict) else None
    try:
        # Not logged, not saved: the text only lives in memory for this request.
        result = classifier.respond(text)
    except InvalidMessageError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        log.exception("Chat processing failed")  # note: the message text is not logged
        return jsonify({"error": "Sorry, something went wrong while reading your message."}), 500

    # Turn endpoint names into real links for the buttons
    result["actions"] = [{"label": a["label"], "url": url_for(a["endpoint"])} for a in result.get("actions", [])]
    return jsonify(result)
