"""
Tests unitaires — AuthService
"""
from unittest.mock import MagicMock, patch

import pytest

from exceptions.auth_exceptions import InvalidCredentials
from exceptions.user_account_exceptions import EmailAlreadyExists, UserAccountDeactivated


def _make_account(id=1, email="user@test.fr", role="client", is_active=True):
    acc = MagicMock()
    acc.id = id
    acc.email = email
    acc.role = MagicMock(value=role)
    acc.is_active = is_active
    # bcrypt hash of "motdepasse123"
    import bcrypt
    acc.password_hash = bcrypt.hashpw(b"motdepasse123", bcrypt.gensalt()).decode()
    return acc


class TestSignup:
    def test_should_raise_when_email_already_exists(self):
        # Arrange
        from services.auth_service import AuthService
        from dtos.auth.signup_dto import SignupDTO

        dto = SignupDTO(email="dup@test.fr", password="motdepasse123", role="client",
                        first_name="Marie", last_name="Dupont")
        with patch("services.auth_service.UserAccountRepository") as mock_repo:
            mock_repo.get_by_email.return_value = MagicMock()

            # Act / Assert
            with pytest.raises(EmailAlreadyExists):
                AuthService.signup(dto)

    def test_should_create_account_and_profile_when_valid(self):
        # Arrange
        from services.auth_service import AuthService
        from dtos.auth.signup_dto import SignupDTO

        dto = SignupDTO(email="new@test.fr", password="motdepasse123", role="client",
                        first_name="Marie", last_name="Dupont")
        account = _make_account(email="new@test.fr")

        with patch("services.auth_service.UserAccountRepository") as mock_user_repo, \
             patch("services.auth_service.ClientRepository") as mock_client_repo, \
             patch("services.auth_service.UserAccountMapper") as mock_mapper:
            mock_user_repo.get_by_email.return_value = None
            mock_user_repo.create.return_value = account
            mock_mapper.model_to_dto.return_value = MagicMock(email="new@test.fr")

            # Act
            result = AuthService.signup(dto)

            # Assert
            mock_user_repo.create.assert_called_once()
            mock_client_repo.create.assert_called_once()
            assert result.email == "new@test.fr"


class TestLogin:
    def test_should_raise_when_account_not_found(self):
        # Arrange
        from services.auth_service import AuthService
        from dtos.auth.login_dto import LoginDTO

        dto = LoginDTO(email="unknown@test.fr", password="motdepasse123")
        with patch("services.auth_service.UserAccountRepository") as mock_repo:
            mock_repo.get_by_email.return_value = None

            # Act / Assert
            with pytest.raises(InvalidCredentials):
                AuthService.login(dto)

    def test_should_raise_when_wrong_password(self):
        # Arrange
        from services.auth_service import AuthService
        from dtos.auth.login_dto import LoginDTO

        dto = LoginDTO(email="user@test.fr", password="mauvaismdp")
        with patch("services.auth_service.UserAccountRepository") as mock_repo:
            mock_repo.get_by_email.return_value = _make_account()

            # Act / Assert
            with pytest.raises(InvalidCredentials):
                AuthService.login(dto)

    def test_should_raise_when_account_deactivated(self):
        # Arrange
        from services.auth_service import AuthService
        from dtos.auth.login_dto import LoginDTO

        dto = LoginDTO(email="user@test.fr", password="motdepasse123")
        with patch("services.auth_service.UserAccountRepository") as mock_repo:
            mock_repo.get_by_email.return_value = _make_account(is_active=False)

            # Act / Assert
            with pytest.raises(UserAccountDeactivated):
                AuthService.login(dto)

    def test_should_return_token_when_credentials_valid(self):
        # Arrange
        from services.auth_service import AuthService
        from dtos.auth.login_dto import LoginDTO

        dto = LoginDTO(email="user@test.fr", password="motdepasse123")
        with patch("services.auth_service.UserAccountRepository") as mock_repo:
            mock_repo.get_by_email.return_value = _make_account()

            # Act
            result = AuthService.login(dto)

            # Assert
            assert "access_token" in result
            assert result["token_type"] == "bearer"

    def test_token_contains_email_and_role(self):
        # Arrange
        from services.auth_service import AuthService
        from dtos.auth.login_dto import LoginDTO
        import jwt
        import config

        dto = LoginDTO(email="user@test.fr", password="motdepasse123")
        with patch("services.auth_service.UserAccountRepository") as mock_repo:
            mock_repo.get_by_email.return_value = _make_account()

            # Act
            result = AuthService.login(dto)

            # Assert
            payload = jwt.decode(result["access_token"], config.JWT_SECRET_KEY, algorithms=["HS256"])
            assert payload["email"] == "user@test.fr"
            assert "role" in payload
            assert "sub" in payload
