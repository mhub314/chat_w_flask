from flask import Flask, jsonify, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_moment import Moment
import logging

db = SQLAlchemy()
migrate = Migrate()
# cors = CORS()
moment = Moment()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app, resources={r"/*": {"origins": [
        "https://watch-buddy.vercel.app/",
        "http://localhost:3000",    
    ]}})

    moment.init_app(app)

    with app.app_context():
        from . import models
        from .api import api as api_blueprint
        app.register_blueprint(api_blueprint, url_prefix='/api')

        # Define the root route for form.html
        @app.route('/')
        def home():
            logging.debug("Accessed home route")
            return render_template('form.html')
        
        @app.route('/test')
        def test():
            logging.debug("Accessed test route")
            return jsonify({"message": "Test route working"})

        for rule in app.url_map.iter_rules():
            logging.debug(f'Route: {rule} -> {rule.endpoint}')
            print(f'Route: {rule} -> {rule.endpoint}')

    return app
