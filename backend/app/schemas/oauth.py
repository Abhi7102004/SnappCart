from pydantic import BaseModel

class OAuthURLResponse(BaseModel):
    """Returned when frontend requests the OAuth redirect URL"""
    authorization_url: str