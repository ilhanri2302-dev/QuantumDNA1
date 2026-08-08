"""
NOVACORE Financial Services
Payment processing service.
"""

from dataclasses import dataclass
from typing import Dict

PAYMENT_CURRENCY = "USD"
PAYMENT_TIMEOUT_SECONDS = 30


@dataclass
class Payment:
    payment_id: str
    customer_id: str
    amount: float
    currency: str = PAYMENT_CURRENCY


class PaymentService:
    """
    Handles payment authorization and transaction signing.

    The cryptographic configuration below represents a legacy
    enterprise deployment that QuantumDNA is analyzing.
    """

    algorithm = "RSA-2048"

    def __init__(self):
        self.transactions: Dict[str, Payment] = {}

    def create_payment(
        self,
        payment_id: str,
        customer_id: str,
        amount: float
    ) -> Payment:

        payment = Payment(
            payment_id=payment_id,
            customer_id=customer_id,
            amount=amount
        )

        self.transactions[payment_id] = payment
        return payment

    def authorize_payment(self, payment: Payment) -> bool:
        if payment.amount <= 0:
            return False

        # In the legacy system, RSA-2048 is used for
        # payment-related cryptographic operations.
        return True

    def get_payment(self, payment_id: str):
        return self.transactions.get(payment_id)