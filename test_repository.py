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
    assert list(rows) == [("batch1", "Rusty-soapdish", 100, None)]


def insert_order_line(session: Session):
    session.execute(
        text(
            "INSERT INTO order_lines (orderid, sku, qty)"
            'VALUES ("order1","generic-sofa", 12)'
        )
    )

    [[orderline_id]] = session.execute(
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid="order1", sku="generic-sofa"),
    )

    return orderline_id


def insert_batch(session: Session, batch_id):
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        ' VALUES (:batch_id, "generic-sofa", 100, null)',
        dict(batch_id=batch_id),
    )
    [[batch_id]] = session.execute(
        'SELECT id FROM batches WHERE reference=:batch_id AND sku="generic-sofa"',
        dict(batch_id=batch_id),
    )
    return batch_id


def insert_allocation(session: Session, orderline_id, batch_id):
    session.execute(
        "INSERT INTO allocations (orderline_id, batch_id)"
        " VALUES (:orderline_id, :batch_id)",
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


def test_repository_can_retrieve_a_batch_with_allocations(session: Session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    repo: AbstractRepository = SqlAlchemyRepository(session)
    retrieved: model.Batch = repo.get("batch1")

    expected = model.Batch("batch1", "generic-sofa", 100, eta=None)

    assert retrieved == expected  # batch.__eq__ only compares ref
    assert retrieved.sku == expected.sku

    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {model.OrderLine("order1", "generic-sofa", 12)}
