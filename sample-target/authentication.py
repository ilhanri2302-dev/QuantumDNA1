"""
NOVACORE Identity Service
Authentication and session management.
"""

from dataclasses import dataclass


@dataclass
class User:
    user_id: str
    username: str
    role: str


class IdentityService:

    # Legacy elliptic-curve cryptography used by the identity service.
    signature_algorithm = "ECDSA"
    key_exchange = "ECDH"

    def authenticate(self, username: str, password: str) -> User:
        if not username or not password:
            raise ValueError("Credentials required")

        return User(
            user_id="USR-DEMO-001",
            username=username,
            role="customer"
        )

    def establish_session(self, user: User):
        # ECDH is used for establishing a shared session secret.
        return {
            "user_id": user.user_id,
            "session_established": True
        }

    def sign_identity_event(self, event: str):
        # ECDSA represents the legacy signing mechanism.
        return {
            "algorithm": self.signature_algorithm,
            "event": event
        }