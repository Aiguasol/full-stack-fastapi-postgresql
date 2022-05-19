import logging
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session, relationship

from app.db.base_class import Base
from app.db.time import utcnow
from app.schemas.role import (
    BaseUserRole,
    Permissions,
    normal_user_role,
    super_user_role,
)

if TYPE_CHECKING:
    from .item import Item  # noqa: F401

logger = logging.getLogger(__name__)


class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    
    time_created_utc = Column(DateTime, server_default=utcnow())
    time_updated_utc = Column(DateTime, onupdate=utcnow())
    last_seen_utc = Column(DateTime, onupdate=utcnow())

    # ------------------------------- relationships ------------------------------ #

    items = relationship("Item", back_populates="owner")

    role_id = Column(Integer, ForeignKey("role.id"))
    role = relationship("Role", back_populates="users")

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    @property
    def is_superuser(self):
        admin_permissions = Permissions.ADMIN_PERMISSIONS
        return all([self.can(p) for p in admin_permissions])


# Defining the Role data-model based on
# [1]M. Grinberg, “Flask Web Development 2ed,” p. 314.
# An association table can be used instead.


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer(), primary_key=True)
    name = Column(String(64), unique=True)
    default = Column(Boolean, default=False, index=True)
    permissions = Column(Integer)

    users = relationship("User", back_populates="role")

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    __default_roles__ = [normal_user_role, super_user_role]
    __superuser_role__ = super_user_role
    __base_role__ = normal_user_role

    @staticmethod
    def insert_or_update_roles(session: Session, roles: Optional[list[BaseUserRole]] = None):
        """helper method for inserting default roles in the db"""

        roles = roles or Role.__default_roles__

        for r in roles:
            role = session.query(Role).filter_by(name=r.name).one_or_none()

            # create role if it doesn't exist
            if role is None:
                role = Role(name=r.name, default=r.default)

            # update role permissions
            role.reset_permissions()
            for perm in r.permissions:
                logger.debug("adding permission %s to role %s", perm, r.name)
                role.add_permission(perm)
            logger.debug("adding role %s", r.name)
            session.add(role)
        session.commit()

    @staticmethod
    def delete_roles(session: Session, roles: Optional[list[BaseUserRole]] = None):
        """helper method for inserting default roles in the db"""

        roles = roles or Role.__default_roles__

        for r in roles:
            role = session.query(Role).filter_by(name=r.name).one_or_none()

            # create role if it doesn't exist
            if role is not None:
                session.delete(role)
        session.commit()

    @staticmethod
    def get_default_role(session: Session):
        """helper method for getting the default role"""
        role = session.query(Role).filter_by(default=True).one_or_none()
        return role

    @staticmethod
    def get_superuser_role(session: Session):
        """helper method for getting the default role"""
        role = session.query(Role).filter_by(name=Role.__superuser_role__.name).one_or_none()
        return role

    def __repr__(self) -> str:
        return f"<Role(name={self.name}, default={self.default}, permissions={self.permissions})>"
