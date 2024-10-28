from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

EntryIDT = TypeVar("EntryIDT")


class DataModel(BaseModel, Generic[EntryIDT]):
    """
    Abstract class for all data models
    """

    entry_id: EntryIDT
    type: str


class VectorDBDataModel(ABC, DataModel[int]):
    """
    Abstract class for all data models that need to be saved into a vector DB (e.g. Qdrant)
    """

    @abstractmethod
    def to_payload(self) -> tuple:
        pass
