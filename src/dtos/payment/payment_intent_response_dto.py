from pydantic import BaseModel


class PaymentIntentResponseDTO(BaseModel):
    payment_id: int
    client_secret: str
