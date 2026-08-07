from datetime import date, timedelta
import pytest

from model import Batch, OrderLine, allocate, OutOfStock

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_allocating_to_a_batch_reduces_the_available_quantity():
    BATCH_COUNT = 20
    ORDER_COUNT = 2

    batch = Batch("batch-001", "SMALL-TABLE", qty=BATCH_COUNT, eta=today)
    line = OrderLine("order-ref", "SMALL-TABLE", qty=ORDER_COUNT)

    batch.allocate(line)

    assert batch.available_quantity == BATCH_COUNT - ORDER_COUNT


def test_can_allocate_if_available_greater_than_required():
    batch = Batch("batch-002", "CHAIR", qty=30, eta=today)
    line = OrderLine("order-ref-2", "CHAIR", qty=29)

    assert batch.allocate(line) == True and batch.available_quantity == 1


def test_cannot_allocate_if_available_smaller_than_required():
    batch = Batch("batch-003", "DESK-LAMP", qty=10, eta=today)
    line = OrderLine("order-ref-3", "DESK-LAMP", qty=11)

    assert batch.allocate(line) == False and batch.available_quantity == 10


def test_can_allocate_if_available_equal_to_required():
    batch = Batch("batch-004", "ORGANIZER", qty=10, eta=today)
    line = OrderLine("order-ref-4", "ORGANIZER", qty=10)

    assert batch.allocate(line) == True


def test_cannot_allocate_if_sku_dont_match():
    batch = Batch("batch-005", "DESK-LAMP", qty=20, eta=today)
    line = OrderLine("order-ref-5", "ORGANIZER", qty=10)

    assert batch.allocate(line) == False


def test_can_deallocate_allocated_lines():
    line1 = OrderLine("order-1", "CHAIR", 10)
    batch = Batch("batch-1", "CHAIR", 30, eta=today)
    batch.allocate(line1)
    assert batch.deallocate(line1) is True and batch.available_quantity == 30


def test_can_only_deallocate_allocated_lines():
    line1 = OrderLine("order-1", "CHAIR", 10)
    line2 = OrderLine("order-2", "CHAIR", 10)
    batch = Batch("batch-1", "CHAIR", 30, eta=today)
    batch.allocate(line1)
    assert batch.deallocate(line2) is False and batch.available_quantity == 20


def test_allocation_is_indempotent():
    line1 = OrderLine("order-2", "CHAIR", 10)
    batch = Batch("batch-1", "CHAIR", 30, eta=today)

    batch.allocate(line1)
    assert batch.allocate(line1) == False
    assert batch.available_quantity == 20


def test_prefers_warehouse_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "DESKLAMP", qty=100, eta=None)
    shipment_batch = Batch("Shipment-batch", "DESKLAMP", qty=100, eta=tomorrow)
    line = OrderLine("Oref", "DESKLAMP", qty=50)

    allocate(line, [shipment_batch, in_stock_batch])

    assert in_stock_batch.available_quantity == 50
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("earliest_batch", "ITEM", 100, eta=today)
    medium = Batch("normal_batch", "ITEM", 100, eta=tomorrow)
    last = Batch("slowest_batch", "ITEM", 100, eta=later)

    line = OrderLine("Oref", "ITEM", qty=50)

    allocate(line, [medium, last, earliest])

    assert earliest.available_quantity == 50
    assert medium.available_quantity == 100
    assert last.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch", "DESKLAMP", qty=100, eta=None)
    shipment_batch = Batch("Shipment-batch", "DESKLAMP", qty=100, eta=tomorrow)
    line = OrderLine("Oref", "DESKLAMP", qty=50)

    allocation = allocate(line, [shipment_batch, in_stock_batch])

    assert allocation == in_stock_batch.batchid


def test_raises_out_of_stock_exception_if_cannot_allocate():
    shipment_batch = Batch("Shipment-batch", "DESKLAMP", qty=49, eta=tomorrow)
    line = OrderLine("Oref", "DESKLAMP", qty=50)

    with pytest.raises(OutOfStock, match="DESKLAMP"):
        allocate(line, [shipment_batch])
