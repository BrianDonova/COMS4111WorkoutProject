import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'


    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import workout
    app.register_blueprint(workout.bp)
    app.add_url_rule('/', endpoint='index')

    from . import members
    app.register_blueprint(members.bp)

    from . import progress
    app.register_blueprint(progress.bp)  

    from . import nutrition
    app.register_blueprint(nutrition.bp)

    from . import trainer
    app.register_blueprint(trainer.bp)

    from . import exercise
    app.register_blueprint(exercise.bp)

    from . import location
    app.register_blueprint(location.bp)

    from . import equipment
    app.register_blueprint(equipment.bp)
    return app