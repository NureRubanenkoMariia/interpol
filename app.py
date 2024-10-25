from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config


db = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder='templates')

    app.config.from_object(Config)

    db.init_app(app)

    from routes import init_routes
    init_routes(app, db)

    return app



