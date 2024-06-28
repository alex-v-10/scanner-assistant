from flask import Flask

def create_flask_app():
    app = Flask(__name__)
    app.config.from_object('modules.flask_app.config.Config')

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app