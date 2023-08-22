from pydantic import BaseModel


class USD(BaseModel):
    usd: float


class SuiPrice(BaseModel):
    sui: USD
