from daos.invoice_dao import InvoiceDAO
from models.invoice_model import InvoiceModel
from dtos.invoice.invoice_response_dto import InvoiceResponseDTO


class InvoiceMapper:
    @staticmethod
    def dao_to_model(dao: InvoiceDAO) -> InvoiceModel:
        return InvoiceModel(
            id=dao.id,
            appointment_id=dao.appointment_id,
            issued_at=dao.issued_at,
            total_amount=dao.total_amount,
            pdf_url=dao.pdf_url,
        )

    @staticmethod
    def model_to_dto(model: InvoiceModel) -> InvoiceResponseDTO:
        return InvoiceResponseDTO(
            id=model.id,
            appointment_id=model.appointment_id,
            issued_at=model.issued_at,
            total_amount=model.total_amount,
            pdf_url=model.pdf_url,
        )
