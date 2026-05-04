import logging

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http(e: HTTPException):
        return jsonify({"error": e.description}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e: Exception):
        logger.exception("Erreur inattendue : %s", e)
        return jsonify({"error": "Une erreur interne s'est produite."}), 500
