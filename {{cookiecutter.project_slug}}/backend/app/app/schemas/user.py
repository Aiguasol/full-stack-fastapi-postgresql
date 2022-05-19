import uuid
from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, validator

from app.schemas.role import BaseUserRole
from app.schemas.type import TypeBase, TypeInDBBase


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    uuid: Optional[UUID4] = uuid.uuid4()
    is_active: Optional[bool] = True
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_superuser: bool = False
    


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    uuid: UUID4 = uuid.uuid4()
    first_name: str
    last_name: str
    password: str
    

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


class UserType(TypeBase):
    pass


class UserTypeInDB(TypeInDBBase):
    pass


boscat_user = UserType(
    name="Boscat User",
    description="A user from BOSCAT",
)

external_user = UserType(
    name="External User",
    description="A user from an external company",
)

_types_collection = [boscat_user, external_user]
