# !/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python version: 3.x -*-
import os

from flask import Flask, render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'ftcls.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('generic/404.html'), 404

    @app.errorhandler(501)
    def page_not_found(e):
        return render_template('generic/501.html'), 501

    from . import db_sqlite, auth, project
    db_sqlite.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(project.bp)
    app.add_url_rule('/', endpoint='index')

    return app