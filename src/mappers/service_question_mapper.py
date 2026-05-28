from daos.service_question_dao import ServiceQuestionDAO
from dtos.service.service_question_response_dto import ServiceQuestionResponseDTO
from models.service_question_model import ServiceQuestionModel


class ServiceQuestionMapper:
    @staticmethod
    def dao_to_model(dao: ServiceQuestionDAO) -> ServiceQuestionModel:
        return ServiceQuestionModel(
            id=dao.id,
            service_id=dao.service_id,
            question=dao.question,
            options=dao.options or [],
            order=dao.order,
        )

    @staticmethod
    def model_to_dto(model: ServiceQuestionModel) -> ServiceQuestionResponseDTO:
        return ServiceQuestionResponseDTO(
            id=model.id,
            service_id=model.service_id,
            question=model.question,
            options=model.options,
            order=model.order,
        )
