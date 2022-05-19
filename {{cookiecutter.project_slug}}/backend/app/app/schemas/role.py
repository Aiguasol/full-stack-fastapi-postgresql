from typing import Optional

from pydantic import BaseModel, Field


class Permissions:
    VIEW_RECORD: int = 1
    VIEW_ROUTE: int = 2
    UPDATE_ROUTE: int = 4
    UPDATE_RECORD: int = 8
    CREATE_RECORD: int = 16
    CREATE_ROUTE: int = 32
    ADMIN_RECORD: int = 64
    ADMIN_ROUTE: int = 128
    ADMIN_USERS: int = 256

    ADMIN_PERMISSIONS: list[int] = [ADMIN_RECORD, ADMIN_ROUTE, ADMIN_USERS]


class BaseUserRole(BaseModel):
    name: Optional[str] = Field(None, description="Name of the role")
    description: Optional[str] = Field(None, description="Description of the role")
    default: Optional[bool] = Field(None, description="Is this the default role")
    permissions: Optional[list[int]] = Field(None, description="Permissions for this role")

    @property
    def permissions_total(self) -> int:
        return sum(self.permissions)


normal_user_role = BaseUserRole(
    name="User",
    description="A normal user with default permissions",
    default=True,
    permissions=[Permissions.VIEW_RECORD, Permissions.VIEW_ROUTE],
)


super_user_role = BaseUserRole(
    name="Administrator",
    description="An administrator with full permissions",
    default=False,
    permissions=[
        Permissions.VIEW_RECORD,
        Permissions.VIEW_ROUTE,
        Permissions.UPDATE_ROUTE,
        Permissions.UPDATE_RECORD,
        Permissions.CREATE_RECORD,
        Permissions.CREATE_ROUTE,
        Permissions.ADMIN_RECORD,
        Permissions.ADMIN_ROUTE,
        Permissions.ADMIN_USERS,
    ],
)

default_user_roles = [normal_user_role, super_user_role]
