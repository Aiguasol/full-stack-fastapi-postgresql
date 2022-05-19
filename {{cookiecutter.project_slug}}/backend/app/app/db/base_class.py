from typing import Any, Optional

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.utils import delete_instances, upsert_instances


@as_declarative()
class Base:
    id: Any
    __name__: str
    __default_instances__: Optional[list[BaseModel]] = None

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def insert_table_defaults(cls, session: Session, instances: Optional[list[BaseModel]] = None) -> None:
        instances = instances or cls.__default_instances__
        if instances is not None:
            upsert_instances(session, cls, instances)

    @classmethod
    def delete_table_defaults(cls, session: Session, instances: Optional[list[BaseModel]] = None) -> None:
        instances = instances or cls.__default_instances__
        if instances is not None:
            delete_instances(session, cls, instances)
