import os

from flask import Flask


def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        SECRET_KEY = "dev",
    )

    if test_config == None:
        app.config.from_pyfile('config.py', silent = True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'


    from . import cut
    cut.init_cutter()

    from . import search
    
    from . import pg
    app.register_blueprint(pg.bp)

    return app
