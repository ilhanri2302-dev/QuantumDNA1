"""
NOVACORE Quantum Readiness Module

Demonstration of cryptographic mechanisms selected for
post-quantum migration.
"""

key_exchange = "ML-KEM"
signature = "ML-DSA"


class QuantumReadyService:

    def establish_key(self, peer):
        # Post-quantum key establishment.
        return {
            "algorithm": key_exchange,
            "peer": peer
        }

    def sign_message(self, message):
        # Post-quantum digital signature.
        return {
            "algorithm": signature,
            "message": message
        }