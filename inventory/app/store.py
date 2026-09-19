from typing import Dict

from .models import InventoryItem

_store: Dict[str, InventoryItem] = {}


def get_store() -> Dict[str, InventoryItem]:
    return _store


def seed_store(store: Dict[str, InventoryItem]) -> None:
    store["NB-01"] = InventoryItem(sku="NB-01", name="Notebook Ultra", quantity=50)
    store["MOUSE-RGB-01"] = InventoryItem(sku="MOUSE-RGB-01", name="Mouse Gamer RGB", quantity=120)