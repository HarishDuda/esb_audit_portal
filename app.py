import logging
import os

from flask import Flask, render_template

from config import Config
from routes.audit_routes import audit_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app.register_blueprint(audit_bp)

    @app.get("/")
    def index():
        response = app.make_response(render_template("index.html", environments=Config.ENVIRONMENTS))
        response.headers["Cache-Control"] = "no-store"
        return response

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)
