import os
from flask import Flask, request, redirect, url_for, render_template
from flask_graphql import GraphQLView
import secrets


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY=secrets.token_urlsafe(),
        DATABASE=os.path.join(app.instance_path, 'webapp.sqlite')
    )
    # if test_config is None:
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     assert hasattr(test_config, 'SECRET_KEY') and len(test_config['SECRET_KEY']) > 8
    #     app.config.from_mapping(test_config)
    
    if not hasattr(app.config, 'SECRET_KEY') or app.config['SECRET_KEY'] is None:
        app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
    elif len(app.config['SECRET_KEY']) <= 8:
        raise RuntimeError('The session was unavailable because the SECRET_KEY set is unacceptable.') 
        
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .graph import schema
    app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
        )
    )

    from . import __main as main
    app.register_blueprint(main.bp)
    
    return app