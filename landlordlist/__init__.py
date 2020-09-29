import os

from flask import Flask, g, json
from werkzeug.exceptions import HTTPException

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter, HEADERS

from flask_limiter.util import get_remote_address


# Global Libraries
db      = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)


# Flask App
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile(os.path.join(app.instance_path, 'config.py'), silent=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'll.sqlite')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

        # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Init Plugins
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Import blueprints
    from .api import (
        cli,
        parties,
        people,
        houses
    )

    app.register_blueprint(cli.bp)
    app.register_blueprint(parties.bp)
    app.register_blueprint(people.bp)
    app.register_blueprint(houses.bp)

    # Error handling
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    return app
