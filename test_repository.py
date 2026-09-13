# Integration tests for db and repository
import model
from repository import AbstractRepository, SqlAlchemyRepository
from sqlalchemy.orm import Session
from sqlalchemy import text


def test_repository_can_save_a_batch(session: Session):
    batch = model.Batch("batch1", "Rusty-soapdish", 100, eta=None)
    repo: AbstractRepository = SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = list(
        session.execute(
            text('SELECT reference, sku, _purchased_quantity, eta FROM "batches"')
        )
    )


def insert_order_line(session: Session):
    session.execute(
        text(
            "INSERT INTO order_lines (orderid, sku, qty)"
            'VALUES ("order1","gereric-sofa", 12)'
        )
    )

    [[orderline_id]] = session.execute(
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid="order1", sku="generic-sofa"),
    )

    return orderline_id