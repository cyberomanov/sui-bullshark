from pydantic import BaseModel


class SignatureData(BaseModel):
    address: str
    signature: str


class SignatureResult(BaseModel):
    data: SignatureData


class SignatureResponse(BaseModel):
    result: SignatureResult
