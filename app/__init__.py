from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_moment import Moment


db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
moment = Moment()
# app.config.from_object(Config)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    moment.init_app(app)

    with app.app_context():
        from . import models #import models after db in initialized

        # register Blueprints
        from .api import api as api_blueprint
        app.register_blueprint(api_blueprint)

    return app

# from . import models



