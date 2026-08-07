"""Model for OrderLIne allocation to batches"""

from datetime import date
from dataclasses import dataclass
from typing import NewType, Set, List


Quantity = NewType("Quantity", float)
Sku = NewType("Sku", str)
Ref = NewType("Ref", str)


@dataclass(frozen=True)
class OrderLine:
    orderid: Ref
    sku: Sku
    qty: Quantity


class OutOfStock(Exception):
    pass


class Batch:
    def __init__(self, batch_nr: Ref, sku: Sku, qty: Quantity, eta: date):
        self._purchased_quantity: Quantity = qty
        self.sku: Sku = sku
        self.eta: date = eta
        self.batchid: Ref = batch_nr
        self._allocations: Set[OrderLine] = set()

    def __gt__(self, other):
        if self.eta == None:
            return False
        if other.eta == None:
            return True
        return self.eta > other.eta

    @property
    def available_quantity(self) -> float:
        return self._purchased_quantity - self.allocated_quantity

    @property
    def allocated_quantity(self) -> float:
        return sum(line.qty for line in self._allocations)

    def allocate(self, order: OrderLine) -> bool:
        if self.can_allocate(order):
            self._allocations.add(order)
            return True
        return False

    def can_allocate(self, order: OrderLine) -> bool:
        return (
            self.available_quantity >= order.qty
            and self.sku == order.sku
            and not order in self._allocations
        )

    def deallocate(self, order: OrderLine) -> bool:
        if order in self._allocations:
            self._allocations.remove(order)
            return True
        return False


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    "allocates and OrderLine to the right batch and returns its reference"
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.batchid
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
