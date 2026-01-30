from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
cache = Cache()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Cache config
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    login_manager.login_view = 'login'

    from app import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app
