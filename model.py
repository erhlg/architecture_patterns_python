"""Model for OrderLIne allocation to batches"""

from datetime import date
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: float


class Batch:
    def __init__(self, batch_nr: str, sku: str, qty: float, eta: date):
        self._purchased_quantity: float = qty
        self.sku: str = sku
        self.eta: date = eta
        self.batchid: str = batch_nr
        self._allocations: set[OrderLine] = set()

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
