import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.parametrize("login", ["testuser", "test@example.com"])
def test_login_accepts_username_or_email(client, login):
    User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",  # noqa: S106
    )

    response = client.post(
        reverse("account_login"),
        {"login": login, "password": "testpass123"},
    )

    assert response.status_code == 302
    assert client.session["_auth_user_id"] == str(User.objects.get().pk)
