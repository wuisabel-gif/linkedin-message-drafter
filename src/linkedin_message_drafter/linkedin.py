"""Boundary for a future, user-configured official LinkedIn integration.

This module intentionally does not contain endpoints, scraping, browser automation,
or token handling. LinkedIn products and permissions vary by app and approval.
"""


class LinkedInClient:
    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("An access token is required")
        self.access_token = access_token

    def send_message(self, recipient_id: str, text: str) -> None:
        raise NotImplementedError(
            "Implement only with LinkedIn-approved messaging permissions and endpoints. "
            "The default application is draft-only."
        )
