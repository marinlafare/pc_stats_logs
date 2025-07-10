import os
from typing import Any, List, Dict, TypeVar, Type
from sqlalchemy import select, insert, Integer, func, update, bindparam
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from database.models import Base, to_dict
from database.engine import AsyncDBSession


_ModelType = TypeVar("_ModelType", bound=Base)

DataObject = Dict[str, Any]
ListOfDataObjects = List[DataObject]

class DBInterface:
    """
    A generic database interface for SQLAlchemy models, supporting create and read operations.
    """
    def __init__(self, db_class: Type[_ModelType]):
        """
        Initializes the DBInterface with a specific SQLAlchemy model class.

        Args:
            db_class (Type[_ModelType]): The SQLAlchemy model class (e.g., PcStats, GpuStats).
        """
        self.db_class = db_class

    async def create(self, data: DataObject) -> DataObject:
        """
        Creates a single new record in the database.

        Args:
            data (DataObject): A dictionary containing the data for the new record.
                               This dictionary should correspond to the SQLAlchemy model's fields.

        Returns:
            DataObject: A dictionary representation of the newly created record,
                        including any auto-generated fields like the timestamp ID.

        Raises:
            Exception: If an error occurs during the database operation.
        """
        async with AsyncDBSession() as session:
            try:
                # Instantiate the SQLAlchemy model with the provided data
                item: _ModelType = self.db_class(**data)
                session.add(item)
                await session.commit()
                await session.refresh(item) # Refresh to get the auto-generated ID (timestamp)
                result = to_dict(item)
                return result
            except Exception as e:
                await session.rollback()
                print(f"Error creating record for {self.db_class.__name__}: {e}")
                raise
