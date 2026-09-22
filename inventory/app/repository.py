from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .entity import InventoryRecord


class InventoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, sku: str) -> Optional[InventoryRecord]:
        return self.session.scalar(select(InventoryRecord).where(InventoryRecord.sku == sku))

    def list(self) -> list[InventoryRecord]:
        return list(self.session.scalars(select(InventoryRecord).order_by(InventoryRecord.sku)))

    def upsert(self, sku: str, name: str, quantity: int) -> InventoryRecord:
        record = self.get(sku)
        if record is None:
            record = InventoryRecord(sku=sku, name=name, quantity=quantity)
            self.session.add(record)
        else:
            record.name = name
            record.quantity = quantity
        try:
            self.session.flush()
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(record)
        return record

    def delete(self, sku: str) -> bool:
        record = self.get(sku)
        if record is None:
            return False
        self.session.delete(record)
        self.session.commit()
        return True

    def adjust(self, sku: str, delta: int) -> Optional[InventoryRecord]:
        record = self.session.scalar(
            select(InventoryRecord)
            .where(InventoryRecord.sku == sku)
            .with_for_update()
        )
        if record is None:
            return None
        new_quantity = record.quantity + delta
        if new_quantity < 0:
            self.session.rollback()
            raise ValueError("Estoque nao pode ficar negativo")
        record.quantity = new_quantity
        self.session.commit()
        self.session.refresh(record)
        return record