import datetime as dt
import logging
import random
import uuid

from faker import Faker
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api.api_v1.api import api_router
from app.api.deps import get_db
from app.core.config import settings, SettingsModeEnum
from app.core.security import get_password_hash
from app.db import base
from app.db.base_class import Base
from app.models import (
    Item,
    Role,
    User,
)

logger = logging.getLogger(__name__)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# for fake data generation
fake = Faker()
Faker.seed(0)


# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def create_default_types(session: Session) -> None:

    Role.insert_or_update_roles(session)


def create_superusers(session: Session) -> None:

    admin_role = Role.get_superuser_role(session)

    user = crud.user.get_by_email(session, email=settings.FIRST_SUPERUSER_EMAIL)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            uuid=uuid.uuid4(),
            password=settings.FIRST_SUPERUSER_PASSWORD,
            first_name=settings.FIRST_SUPERUSER_NAME,
            last_name=settings.FIRST_SUPERUSER_LAST_NAME,
            is_superuser=True,
            role_id=admin_role.id,
        )
        
        crud.user.create(session, obj_in=user_in)  # noqa: F841


# TODO: refactor this method
def seed_fake_data(session: Session) -> None:

    # ------------------------------- default types ------------------------------ #

    create_default_types(session)

    # ----------------------------- create superusers ---------------------------- #

    create_superusers(session)

    # --------------------------- insert default roles --------------------------- #

    default_role = Role.get_default_role(session)
    superuser_role = Role.get_superuser_role(session)

    # ------------------------------- default users ------------------------------ #

    for ix in range(1, 3):

        u = User(
            first_name=f"user{ix}",
            uuid=uuid.uuid4(),
            last_name=f"user{ix}_last",
            email=f"user{ix}@test.db",
            hashed_password=get_password_hash(f"test{ix}"),
            role_id=default_role.id,
        )
        logger.debug(f"inserting user {u}")

    session.commit()


    # add one superuser
    su = User(
        first_name=f"superuser1",
        uuid=uuid.uuid4(),
        last_name=f"superuser1_last",
        email=f"superuser1@test.db",
        hashed_password=get_password_hash(f"supertest1"),
        role_id=superuser_role.id,
    )

    create_superusers(session)

    logger.debug(f"inserting user {su}")
    session.add(su)


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    seed_fake_data(db)


def refresh_db(db: Session) -> None:
    assert settings.FASTAPI_MODE != SettingsModeEnum.PROD, "Refresh DB is not allowed in production mode"
    Base.metadata.drop_all(bind=db.bind)
    Base.metadata.create_all(bind=db.bind)
    seed_fake_data(db)
