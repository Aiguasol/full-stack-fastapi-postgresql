__doc__ = """Data migration utilities for alembic"""

import logging
from typing import Any, Optional, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta

logger = logging.getLogger(__name__)

def upsert_instances(session: Session, cls: Any, instances: list[Union[BaseModel, Any]]) -> None:
    

    for instance in instances:
        if isinstance(instance, BaseModel):
            t_db = cls(**instance.dict())
        else:
            t_db = instance
        
        found_t_db = session.query(cls).filter(cls.__table__.c.name == t_db.name).one_or_none()        
        
        if found_t_db is None:
            logger.debug(f"Adding {found_t_db} to session...")
            session.add(t_db)
    session.commit()


def delete_instances(session: Session, cls: Any, instances: list[Union[BaseModel, Any]]) -> None:

    for instance in instances:
        if isinstance(instance, BaseModel):
            t_db = cls(**instance.dict())
        else:
            t_db = instance

        found_t_db = session.query(cls).filter(cls.__table__.c.name == t_db.name).one_or_none()
        if found_t_db:
            logger.debug(f"deleting {found_t_db} from session...")
            session.delete(found_t_db)
    session.commit()
