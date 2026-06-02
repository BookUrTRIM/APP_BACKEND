"""
Tests unitaires — ServiceQuestionService
"""
from unittest.mock import MagicMock, patch

import pytest

from exceptions.service_exceptions import ServiceAccessDenied, ServiceNotFound
from exceptions.service_question_exceptions import ServiceQuestionIndexError, ServiceQuestionNotFound


def _make_service(id=1, provider_id=2, default_duration=60):
    s = MagicMock()
    s.id = id
    s.provider_id = provider_id
    s.default_duration = default_duration
    return s


def _make_question(id=1, service_id=1):
    q = MagicMock()
    q.id = id
    q.service_id = service_id
    q.question = "Type de cheveux ?"
    q.options = [
        {"label": "Lisse", "extra_minutes": 0},
        {"label": "Bouclé", "extra_minutes": 15},
        {"label": "Crépu", "extra_minutes": 30},
    ]
    q.order = 1
    return q


def _make_provider(id=2, user_account_id=200):
    p = MagicMock()
    p.id = id
    p.user_account_id = user_account_id
    return p


class TestList:
    def test_should_return_questions_for_service(self):
        # Arrange
        from services.service_question_service import ServiceQuestionService

        q1 = _make_question(id=1)
        q2 = _make_question(id=2)

        with patch("services.service_question_service.ServiceRepository") as mock_service, \
             patch("services.service_question_service.ServiceQuestionRepository") as mock_repo, \
             patch("services.service_question_service.ServiceQuestionMapper") as mock_mapper:
            mock_service.get_by_id.return_value = _make_service()
            mock_repo.list_by_service.return_value = [q1, q2]
            mock_mapper.model_to_dto.side_effect = lambda q: MagicMock(id=q.id)

            # Act
            result = ServiceQuestionService.list(service_id=1)

            # Assert
            assert len(result) == 2
            mock_repo.list_by_service.assert_called_once_with(1)


class TestCreate:
    def test_should_raise_when_service_not_found(self):
        from services.service_question_service import ServiceQuestionService
        from dtos.service.service_question_create_dto import ServiceQuestionCreateDTO

        dto = ServiceQuestionCreateDTO(question="Test ?", options=[])
        with patch("services.service_question_service.ServiceRepository") as mock_repo:
            mock_repo.get_by_id.return_value = None

            with pytest.raises(ServiceNotFound):
                ServiceQuestionService.create(service_id=99, user_account_id=200, dto=dto)

    def test_should_raise_when_not_owner(self):
        from services.service_question_service import ServiceQuestionService
        from dtos.service.service_question_create_dto import ServiceQuestionCreateDTO

        dto = ServiceQuestionCreateDTO(question="Test ?", options=[])
        with patch("services.service_question_service.ServiceRepository") as mock_service, \
             patch("services.service_question_service.ProviderRepository") as mock_provider:
            mock_service.get_by_id.return_value = _make_service(provider_id=2)
            mock_provider.get_by_user_account_id.return_value = _make_provider(id=99)

            with pytest.raises(ServiceAccessDenied):
                ServiceQuestionService.create(service_id=1, user_account_id=999, dto=dto)

    def test_should_create_when_valid(self):
        from services.service_question_service import ServiceQuestionService
        from dtos.service.service_question_create_dto import ServiceQuestionCreateDTO, QuestionOption

        dto = ServiceQuestionCreateDTO(
            question="Type de cheveux ?",
            options=[QuestionOption(label="Lisse", extra_minutes=0)],
        )
        question = _make_question()
        with patch("services.service_question_service.ServiceRepository") as mock_service, \
             patch("services.service_question_service.ProviderRepository") as mock_provider, \
             patch("services.service_question_service.ServiceQuestionRepository") as mock_repo, \
             patch("services.service_question_service.ServiceQuestionMapper") as mock_mapper:
            mock_service.get_by_id.return_value = _make_service(provider_id=2)
            mock_provider.get_by_user_account_id.return_value = _make_provider(id=2)
            mock_repo.create.return_value = question
            mock_mapper.model_to_dto.return_value = MagicMock(id=1)

            result = ServiceQuestionService.create(service_id=1, user_account_id=200, dto=dto)

            mock_repo.create.assert_called_once_with(1, dto)
            assert result.id == 1


class TestUpdate:
    def test_should_raise_when_question_not_found(self):
        from services.service_question_service import ServiceQuestionService
        from dtos.service.service_question_update_dto import ServiceQuestionUpdateDTO

        dto = ServiceQuestionUpdateDTO(question="Modifié ?")
        with patch("services.service_question_service.ServiceQuestionRepository") as mock_repo:
            mock_repo.get_by_id.return_value = None

            with pytest.raises(ServiceQuestionNotFound):
                ServiceQuestionService.update(question_id=99, user_account_id=200, dto=dto)

    def test_should_raise_when_not_owner(self):
        from services.service_question_service import ServiceQuestionService
        from dtos.service.service_question_update_dto import ServiceQuestionUpdateDTO

        dto = ServiceQuestionUpdateDTO(question="Hack")
        with patch("services.service_question_service.ServiceQuestionRepository") as mock_q, \
             patch("services.service_question_service.ServiceRepository") as mock_service, \
             patch("services.service_question_service.ProviderRepository") as mock_provider:
            mock_q.get_by_id.return_value = _make_question(service_id=1)
            mock_service.get_by_id.return_value = _make_service(provider_id=2)
            mock_provider.get_by_user_account_id.return_value = _make_provider(id=99)

            with pytest.raises(ServiceAccessDenied):
                ServiceQuestionService.update(question_id=1, user_account_id=999, dto=dto)


class TestCalculateDuration:
    def test_should_return_base_duration_when_no_answers(self):
        from services.service_question_service import ServiceQuestionService
        from dtos.service.duration_calculate_dto import DurationCalculateDTO

        dto = DurationCalculateDTO(answers=[])
        with patch("services.service_question_service.ServiceRepository") as mock_repo:
            mock_repo.get_by_id.return_value = _make_service(default_duration=60)

            result = ServiceQuestionService.calculate_duration(service_id=1, dto=dto)

            assert result.duration == 60

    def test_should_add_extra_minutes_from_answers(self):
        from services.service_question_service import ServiceQuestionService
        from dtos.service.duration_calculate_dto import DurationCalculateDTO, AnswerItem

        dto = DurationCalculateDTO(answers=[
            AnswerItem(question_id=1, option_index=1),  # +15 min
            AnswerItem(question_id=2, option_index=0),  # +0 min
        ])
        q2 = _make_question(id=2)
        q2.options = [{"label": "Court", "extra_minutes": 0}]

        with patch("services.service_question_service.ServiceRepository") as mock_service, \
             patch("services.service_question_service.ServiceQuestionRepository") as mock_q:
            mock_service.get_by_id.return_value = _make_service(default_duration=45)
            mock_q.get_by_id.side_effect = lambda qid: _make_question(id=qid) if qid == 1 else q2

            result = ServiceQuestionService.calculate_duration(service_id=1, dto=dto)

            assert result.duration == 45 + 15 + 0

    def test_should_raise_when_service_not_found(self):
        from services.service_question_service import ServiceQuestionService
        from dtos.service.duration_calculate_dto import DurationCalculateDTO

        dto = DurationCalculateDTO(answers=[])
        with patch("services.service_question_service.ServiceRepository") as mock_repo:
            mock_repo.get_by_id.return_value = None

            with pytest.raises(ServiceNotFound):
                ServiceQuestionService.calculate_duration(service_id=99, dto=dto)

    def test_should_raise_when_option_index_out_of_range(self):
        from services.service_question_service import ServiceQuestionService
        from dtos.service.duration_calculate_dto import DurationCalculateDTO, AnswerItem

        dto = DurationCalculateDTO(answers=[AnswerItem(question_id=1, option_index=99)])
        with patch("services.service_question_service.ServiceRepository") as mock_service, \
             patch("services.service_question_service.ServiceQuestionRepository") as mock_q:
            mock_service.get_by_id.return_value = _make_service(default_duration=60)
            mock_q.get_by_id.return_value = _make_question()

            with pytest.raises(ServiceQuestionIndexError):
                ServiceQuestionService.calculate_duration(service_id=1, dto=dto)
