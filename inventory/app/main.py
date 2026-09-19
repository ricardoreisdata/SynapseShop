from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import Response

from .models import AdjustRequest, InventoryItem, MessageResponse
from .store import get_store, seed_store


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    seed_store(get_store())
    yield


app = FastAPI(
    title="SynapseShop Inventory Service",
    description="Microsservico de estoque do SynapseShop (FastAPI). Sem banco de dados nesta aula (SpecDD - Aula 5).",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=MessageResponse, tags=["sistema"])
def health() -> MessageResponse:
    return MessageResponse(status="ok", message="inventory disponivel")


@app.get("/inventory", response_model=list[InventoryItem], tags=["inventory"])
def list_items(store: Dict[str, InventoryItem] = Depends(get_store)) -> list[InventoryItem]:
    return sorted(store.values(), key=lambda item: item.sku)


@app.get("/inventory/{sku}", response_model=InventoryItem, tags=["inventory"])
def get_item(sku: str, store: Dict[str, InventoryItem] = Depends(get_store)) -> InventoryItem:
    item = store.get(sku)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item nao encontrado no estoque")
    return item


@app.put("/inventory/{sku}", response_model=InventoryItem, status_code=status.HTTP_200_OK, tags=["inventory"])
def register_item(sku: str, payload: InventoryItem, store: Dict[str, InventoryItem] = Depends(get_store)) -> InventoryItem:
    item = payload.model_copy(update={"sku": sku})
    store[sku] = item
    return item


@app.post("/inventory/{sku}/adjust", response_model=InventoryItem, tags=["inventory"])
def adjust_stock(sku: str, payload: AdjustRequest, store: Dict[str, InventoryItem] = Depends(get_store)) -> InventoryItem:
    item = store.get(sku)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item nao encontrado no estoque")
    if payload.delta == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="delta deve ser diferente de zero")
    new_quantity = item.quantity + payload.delta
    if new_quantity < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estoque nao pode ficar negativo")
    updated = item.model_copy(update={"quantity": new_quantity})
    store[sku] = updated
    return updated


@app.delete("/inventory/{sku}", status_code=status.HTTP_204_NO_CONTENT, tags=["inventory"])
def delete_item(sku: str, store: Dict[str, InventoryItem] = Depends(get_store)) -> Response:
    if sku not in store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item nao encontrado no estoque")
    del store[sku]
    return Response(status_code=status.HTTP_204_NO_CONTENT)