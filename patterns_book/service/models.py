from datetime import date

from pydantic import BaseModel, Field


class OrderLine(BaseModel):
    orderid: str
    sku: str
    qty: int = Field(gt=0)


class Batch(BaseModel):
    reference: str
    sku: str
    qty: int = Field(gt=0)
    eta: date | None
