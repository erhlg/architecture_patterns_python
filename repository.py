import abc
import model
from sqlalchemy.orm import Session


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, batch: model.Batch):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session:Session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def remove(self, batch):
        self.session.delete(batch)

    def list(self):
        return self.session.query(model.Batch).all()
