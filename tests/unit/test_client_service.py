"""
Tests unitaires — ClientService (profil + hair profile)
"""
from unittest.mock import MagicMock, patch

import pytest

from exceptions.client_exceptions import ClientAlreadyExists, ClientNotFound


def _make_client(id=1, user_account_id=100):
    c = MagicMock()
    c.id = id
    c.user_account_id = user_account_id
    return c


class TestCreate:
    def test_should_raise_when_profile_already_exists(self):
        from services.client_service import ClientService
        from dtos.client.client_create_dto import ClientCreateDTO

        dto = ClientCreateDTO(first_name="Marie", last_name="Dupont")
        with patch("services.client_service.ClientRepository") as mock_repo:
            mock_repo.get_by_user_account_id.return_value = MagicMock()

            with pytest.raises(ClientAlreadyExists):
                ClientService.create(user_account_id=100, dto=dto)

    def test_should_create_when_valid(self):
        from services.client_service import ClientService
        from dtos.client.client_create_dto import ClientCreateDTO

        dto = ClientCreateDTO(first_name="Marie", last_name="Dupont")
        client = _make_client()
        with patch("services.client_service.ClientRepository") as mock_repo, \
             patch("services.client_service.ClientMapper") as mock_mapper:
            mock_repo.get_by_user_account_id.return_value = None
            mock_repo.create.return_value = client
            mock_mapper.model_to_dto.return_value = MagicMock(id=1, first_name="Marie")

            result = ClientService.create(user_account_id=100, dto=dto)

            mock_repo.create.assert_called_once()
            assert result.first_name == "Marie"


class TestGetMe:
    def test_should_raise_when_client_not_found(self):
        from services.client_service import ClientService

        with patch("services.client_service.ClientRepository") as mock_repo:
            mock_repo.get_by_user_account_id.return_value = None

            with pytest.raises(ClientNotFound):
                ClientService.get_me(user_account_id=99)


class TestGetHairProfile:
    def test_should_raise_when_client_not_found(self):
        from services.client_service import ClientService

        with patch("services.client_service.ClientRepository") as mock_repo:
            mock_repo.get_by_user_account_id.return_value = None

            with pytest.raises(ClientNotFound):
                ClientService.get_hair_profile(user_account_id=99)

    def test_should_return_none_when_no_profile(self):
        from services.client_service import ClientService

        with patch("services.client_service.ClientRepository") as mock_repo, \
             patch("services.client_service.ClientHairProfileRepository") as mock_hair:
            mock_repo.get_by_user_account_id.return_value = _make_client()
            mock_hair.get_by_client.return_value = None

            result = ClientService.get_hair_profile(user_account_id=100)

            assert result is None

    def test_should_return_profile_when_exists(self):
        from services.client_service import ClientService

        profile = MagicMock()
        with patch("services.client_service.ClientRepository") as mock_repo, \
             patch("services.client_service.ClientHairProfileRepository") as mock_hair, \
             patch("services.client_service.ClientHairProfileMapper") as mock_mapper:
            mock_repo.get_by_user_account_id.return_value = _make_client()
            mock_hair.get_by_client.return_value = profile
            mock_mapper.model_to_dto.return_value = MagicMock(hair_type="bouclé")

            result = ClientService.get_hair_profile(user_account_id=100)

            assert result.hair_type == "bouclé"


class TestUpsertHairProfile:
    def test_should_raise_when_client_not_found(self):
        from services.client_service import ClientService
        from dtos.client.hair_profile_upsert_dto import HairProfileUpsertDTO
        from enums.hair_enum import HairType, HairLength

        dto = HairProfileUpsertDTO(hair_type=HairType.BOUCLE, hair_length=HairLength.LONG)
        with patch("services.client_service.ClientRepository") as mock_repo:
            mock_repo.get_by_user_account_id.return_value = None

            with pytest.raises(ClientNotFound):
                ClientService.upsert_hair_profile(user_account_id=99, dto=dto)

    def test_should_upsert_profile_when_valid(self):
        from services.client_service import ClientService
        from dtos.client.hair_profile_upsert_dto import HairProfileUpsertDTO
        from enums.hair_enum import HairType, HairLength

        dto = HairProfileUpsertDTO(hair_type=HairType.BOUCLE, hair_length=HairLength.LONG)
        profile = MagicMock()
        with patch("services.client_service.ClientRepository") as mock_repo, \
             patch("services.client_service.ClientHairProfileRepository") as mock_hair, \
             patch("services.client_service.ClientHairProfileMapper") as mock_mapper:
            mock_repo.get_by_user_account_id.return_value = _make_client()
            mock_hair.upsert.return_value = profile
            mock_mapper.model_to_dto.return_value = MagicMock(hair_type="bouclé")

            result = ClientService.upsert_hair_profile(user_account_id=100, dto=dto)

            mock_hair.upsert.assert_called_once_with(1, dto)
            assert result.hair_type == "bouclé"
