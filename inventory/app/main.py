from contextlib import asynccontextmanager
from typing import AsyncIterator, Iterator

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import Response

from .db import SessionLocal
from .models import AdjustRequest, InventoryItem, MessageResponse
from .repository import InventoryRepository
from .service import InventoryService


def get_service() -> Iterator[InventoryService]:
    session = SessionLocal()
    try:
        yield InventoryService(InventoryRepository(session))
    finally:
        session.close()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    session = SessionLocal()
    try:
        service = InventoryService(InventoryRepository(session))
        service.register("NB-01", "Notebook Ultra", 50)
        service.register("MOUSE-RGB-01", "Mouse Gamer RGB", 120)
    finally:
        session.close()
    yield


app = FastAPI(
    title="SynapseShop Inventory Service",
    description="Microsservico de estoque do SynapseShop (FastAPI). Persistencia relacional em PostgreSQL com SQLAlchemy + Alembic (SpecDD - Aula 6).",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=MessageResponse, tags=["sistema"])
def health() -> MessageResponse:
    return MessageResponse(status="ok", message="inventory disponivel")


@app.get("/inventory", response_model=list[InventoryItem], tags=["inventory"])
def list_items(service: InventoryService = Depends(get_service)) -> list[InventoryItem]:
    return service.list()


@app.get("/inventory/{sku}", response_model=InventoryItem, tags=["inventory"])
def get_item(sku: str, service: InventoryService = Depends(get_service)) -> InventoryItem:
    item = service.get(sku)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item nao encontrado no estoque")
    return item


@app.put("/inventory/{sku}", response_model=InventoryItem, status_code=status.HTTP_200_OK, tags=["inventory"])
def register_item(sku: str, payload: InventoryItem, service: InventoryService = Depends(get_service)) -> InventoryItem:
    return service.register(sku, payload.name, payload.quantity)


@app.post("/inventory/{sku}/adjust", response_model=InventoryItem, tags=["inventory"])
def adjust_stock(sku: str, payload: AdjustRequest, service: InventoryService = Depends(get_service)) -> InventoryItem:
    if payload.delta == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="delta deve ser diferente de zero")
    try:
        item = service.adjust(sku, payload.delta)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item nao encontrado no estoque")
    return item


@app.delete("/inventory/{sku}", status_code=status.HTTP_204_NO_CONTENT, tags=["inventory"])
def delete_item(sku: str, service: InventoryService = Depends(get_service)) -> Response:
    if not service.delete(sku):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item nao encontrado no estoque")
    return Response(status_code=status.HTTP_204_NO_CONTENT)