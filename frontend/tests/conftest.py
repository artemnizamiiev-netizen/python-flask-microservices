import os
import sys
from pathlib import Path

import pytest


SERVICE_DIR = Path(__file__).resolve().parents[1]
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))


@pytest.fixture(scope="session")
def app():

    os.environ["CONFIGURATION_SETUP"] = "config.DevelopmentConfig"
    os.environ["SECRET_KEY"] = "test_key"
    os.environ["WTF_CSRF_SECRET_KEY"] = "test_key"
    os.environ["USER_SERVICE_URL"] = "http://mock"
    os.environ["PRODUCT_SERVICE_URL"] = "http://mock"
    os.environ["ORDER_SERVICE_URL"] = "http://mock"

    from application import create_app

    app = create_app()
    app.config["TESTING"] = True

    yield app


@pytest.fixture
def client(app):
    return app.test_client()
