"""Wellness resources page."""
from flask import Blueprint, render_template

from ml.safety import SUPPORT_CONTACTS

bp = Blueprint("resources", __name__)


@bp.route("/resources")
def resources():
    # Public on purpose: support information should be easy to reach.
    return render_template("resources.html", contacts=SUPPORT_CONTACTS)
