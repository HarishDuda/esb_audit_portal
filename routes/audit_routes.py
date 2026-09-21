import logging

import oracledb
from flask import Blueprint, jsonify, request

from services.audit_service import InputError, search

audit_bp = Blueprint("audit", __name__)
logger = logging.getLogger(__name__)


@audit_bp.post("/api/audit/search")
def audit_search():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(success=False, message="A JSON request body is required."), 400
    try:
        return jsonify(search(data))
    except InputError as exc:
        return jsonify(success=False, message=str(exc)), 400
    except ValueError as exc:
        logger.warning("Audit search configuration error: %s", exc)
        return jsonify(success=False, message="Unable to retrieve ESB audit information. Please contact the application support team."), 503
    except oracledb.Error:
        logger.exception("Oracle audit search failed")
        return jsonify(success=False, message="Unable to retrieve ESB audit information. Please contact the application support team."), 503
    except Exception:
        logger.exception("Unexpected audit search failure")
        return jsonify(success=False, message="Database query failed. Please contact the application support team."), 500
