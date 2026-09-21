import logging
import os

from flask import Flask, render_template

from config import Config
from routes.audit_routes import audit_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app.register_blueprint(audit_bp)

    @app.get("/")
    def index():
        return render_template("index.html", environments=Config.ENVIRONMENTS)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
