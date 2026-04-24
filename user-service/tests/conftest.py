import os
import sys
from pathlib import Path

import pytest


SERVICE_DIR = Path(__file__).resolve().parents[1]
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("data")
    db_path = db_dir / "test.db"

    os.environ["CONFIGURATION_SETUP"] = "config.DevelopmentConfig"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["SECRET_KEY"] = "test-secret"

    from application import create_app, db

    app = create_app()
    app.config["TESTING"] = True

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()



@pytest.fixture(autouse=True)
def reset_db(app):
    from application import db

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

    yield

    with app.app_context():
        db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    from application import db as _db
    return _db
