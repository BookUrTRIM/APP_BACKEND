from daos.review_dao import ReviewDAO
from models.review_model import ReviewModel
from dtos.review.review_response_dto import ReviewResponseDTO


class ReviewMapper:
    @staticmethod
    def dao_to_model(dao: ReviewDAO) -> ReviewModel:
        return ReviewModel(
            id=dao.id,
            appointment_id=dao.appointment_id,
            rating=dao.rating,
            comment=dao.comment,
            reviewed_at=dao.reviewed_at,
        )

    @staticmethod
    def model_to_dto(model: ReviewModel) -> ReviewResponseDTO:
        return ReviewResponseDTO(
            id=model.id,
            appointment_id=model.appointment_id,
            rating=model.rating,
            comment=model.comment,
            reviewed_at=model.reviewed_at,
        )
