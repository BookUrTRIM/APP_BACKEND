from enum import Enum


class PaymentType(str, Enum):
    DEPOSIT = 'deposit'
    BALANCE = 'balance'


class PaymentStatus(str, Enum):
    PENDING   = 'pending'
    VALIDATED = 'validated'
    FAILED    = 'failed'
    REFUNDED  = 'refunded'
