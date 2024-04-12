from flask import Flask
from os import environ
from flask_caching import Cache

cache = Cache(
    config={"CACHE_TYPE": "simple", "CACHE_DEFAULT_TIMEOUT": 300}
)  # Set cache timeout to 5 minutes = 300secs


def create_app(config_overrides=None):
    app = Flask(__name__)

    # This enables the postgres database if an environmental variable is declared, which it will be if we are using docker-compose.yml
    # if it is not specified by docker-compose i.e if we just run docker build, the default value of "sqlite:///db.sqlite" will be used
    app.config["SQLALCHEMY_DATABASE_URI"] = environ.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///db.sqlite"
    )
    if config_overrides:
        app.config.update(config_overrides)

    # Load the models
    from spamoverflow.models import db

    db.init_app(app)

    # Initialize the caching
    cache.init_app(app)

    # Create the database tables
    with app.app_context():
        db.create_all()

    # Register the blueprints
    from spamoverflow.views.routes import api

    app.register_blueprint(api)

    return app
