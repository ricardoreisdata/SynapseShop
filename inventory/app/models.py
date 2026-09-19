from pydantic import BaseModel, Field


class InventoryItem(BaseModel):
    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    quantity: int = Field(ge=0)


class AdjustRequest(BaseModel):
    delta: int = Field(description="Variacao de estoque (positivo para entrada, negativo para saida)")


class MessageResponse(BaseModel):
    status: str = "ok"
    message: str