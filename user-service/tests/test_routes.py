from passlib.hash import sha256_crypt


def test_healthz_returns_ok(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_create_user_returns_created_user(client, app):
    response = client.post(
        "/api/user/create",
        data={
            "first_name": "Pupa",
            "last_name": "Lupa",
            "email": "pupalupa@example.com",
            "username": "pupalupa",
            "password": "salary",
        },
    )

    assert response.status_code == 200

    payload = response.get_json()
    assert payload["message"] == "User added"
    assert payload["result"]["username"] == "pupalupa"
    assert payload["result"]["email"] == "pupalupa@example.com"

    from application.models import User

    with app.app_context():
        user = User.query.filter_by(username="pupalupa").first()
        assert user is not None
        assert user.email == "pupalupa@example.com"


def test_login_returns_401_for_invalid_password(client, app):
    from application.models import User

    with app.app_context():
        user = User(
            username="testuser",
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password=sha256_crypt.hash("correct-password"),
            authenticated=True,
        )
        from application import db
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/api/user/login",
        data={
            "username": "testuser",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == "Not logged in"


def test_login_returns_api_key_for_valid_credentials(client, app):
    from application.models import User
    
    with app.app_context():
        user = User(
            username="bibaboba",
            email="bibaboba@example.com",
            first_name="biba",
            last_name="boba",
            password=sha256_crypt.hash("correct-password"),
            authenticated=True,
        )
        from application import db
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/api/user/login",
        data={
            "username": "bibaboba",
            "password": "correct-password",
        },
    )

    assert response.status_code == 200

    payload = response.get_json()
    assert payload["message"] == "Logged in"
    assert payload["api_key"]

    with app.app_context():
        user = User.query.filter_by(username="bibaboba").first()
        assert user.api_key is not None
