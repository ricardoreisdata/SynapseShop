from typing import List, Optional

from .entity import InventoryRecord
from .models import InventoryItem
from .repository import InventoryRepository


class InventoryService:
    def __init__(self, repository: InventoryRepository) -> None:
        self.repository = repository

    def list(self) -> List[InventoryItem]:
        return [self._to_item(record) for record in self.repository.list()]

    def get(self, sku: str) -> Optional[InventoryItem]:
        record = self.repository.get(sku)
        return self._to_item(record) if record is not None else None

    def register(self, sku: str, name: str, quantity: int) -> InventoryItem:
        record = self.repository.upsert(sku, name, quantity)
        return self._to_item(record)

    def adjust(self, sku: str, delta: int) -> Optional[InventoryItem]:
        record = self.repository.adjust(sku, delta)
        return self._to_item(record) if record is not None else None

    def delete(self, sku: str) -> bool:
        return self.repository.delete(sku)

    @staticmethod
    def _to_item(record: InventoryRecord) -> InventoryItem:
        return InventoryItem(sku=record.sku, name=record.name, quantity=record.quantity)