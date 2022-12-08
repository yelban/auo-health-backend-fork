from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginResponseToken(BaseModel):
    access_token: str
    refresh_token: str
    # csrf_access_token: str
    # csrf_refresh_token: str
    token_type: str


# class TokenPayload(BaseModel):
#     sub: Optional[str] = None
