import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.exc import IntegrityError

from app.db import Base, engine, SessionLocal
from app.entity import InventoryRecord
from app.repository import InventoryRepository
from app.service import InventoryService


def timed(label: str, fn):
    start = time.perf_counter()
    result = fn()
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"{label:<55} {elapsed_ms:8.3f} ms")
    return result, elapsed_ms


def main() -> None:
    session = SessionLocal()
    try:
        repo = InventoryRepository(session)
        service = InventoryService(repo)

        print(f"=== Testes transacionais {datetime.now().isoformat(timespec='seconds')} ===\n")

        _, t1 = timed("upsert novo item TEST-KB-01", lambda: service.register("TEST-KB-01", "Teclado", 10))
        assert repo.get("TEST-KB-01") is not None
        print("PASS: persistencia apos commit (upsert)\n")

        _, t2 = timed("consulta por sku TEST-KB-01", lambda: service.get("TEST-KB-01"))
        assert service.get("TEST-KB-01").quantity == 10
        print("PASS: leitura consistente\n")

        _, t3 = timed("upsert item existente (update)", lambda: service.register("TEST-KB-01", "Teclado RGB", 15))
        assert service.get("TEST-KB-01").quantity == 15
        print("PASS: upsert idempotente (update)\n")

        _, t4 = timed("ajuste +5", lambda: service.adjust("TEST-KB-01", 5))
        assert service.get("TEST-KB-01").quantity == 20
        print("PASS: ajuste positivo\n")

        _, t5 = timed("ajuste -30 (rollback por negatividade)", lambda: service_rollback("TEST-KB-01", -30))
        assert service.get("TEST-KB-01").quantity == 20
        print("PASS: rollback em estoque negativo\n")

        _, t6 = timed("ajuste -10", lambda: service.adjust("TEST-KB-01", -10))
        assert service.get("TEST-KB-01").quantity == 10
        print("PASS: ajuste negativo valido\n")

        _, t7 = timed("violacao de unicidade de sku", lambda: violation_duplicate_sku())
        assert service.get("TEST-KB-01") is not None
        print("PASS: UNIQUE em sku aplicado (IntegrityError + rollback)\n")

        _, t8 = timed("listagem ordenada", lambda: service.list())
        skus = [i.sku for i in service.list()]
        assert skus == sorted(skus)
        print("PASS: listagem ordenada por sku\n")

        _, t9 = timed("delete TEST-KB-01", lambda: service.delete("TEST-KB-01"))
        assert service.get("TEST-KB-01") is None
        print("PASS: delete + persistencia\n")

        print(f"\nTotal de operacoes: 9 | Tempo medio por transacao: {(t1 + t2 + t3 + t4 + t5 + t6 + t7 + t8 + t9) / 9:.3f} ms\n")
        print("=== Checkpoint: integridade do schema ===")

        insp = __import__("sqlalchemy.inspection", fromlist=["inspect"]).inspect(engine)
        cols = {c["name"]: c for c in insp.get_columns("inventory")}
        assert "id" in cols and "sku" in cols and "quantity" in cols and "created_at" in cols
        print("PASS: colunas esperadas presentes na tabela inventory")
    finally:
        session.close()
        inspector = __import__("sqlalchemy.inspection", fromlist=["inspect"]).inspect(engine)
        if inspector.has_table("inventory"):
            cleanup = SessionLocal()
            try:
                cleanup.execute(InventoryRecord.__table__.delete().where(InventoryRecord.sku.like("TEST-%")))
                cleanup.commit()
            finally:
                cleanup.close()


def service_rollback(sku: str, delta: int):
    session = SessionLocal()
    try:
        svc = InventoryService(InventoryRepository(session))
        try:
            svc.adjust(sku, delta)
        except ValueError:
            session.rollback()
    finally:
        session.close()


def violation_duplicate_sku():
    session = SessionLocal()
    try:
        session.add(InventoryRecord(sku="TEST-KB-01", name="Duplicado", quantity=1))
        session.commit()
    except IntegrityError:
        session.rollback()
        return "IntegrityError capturado"
    finally:
        session.close()


if __name__ == "__main__":
    main()