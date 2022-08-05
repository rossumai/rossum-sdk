from rossum_ng.models.base import Base


class UserRole(Base):
    id: int
    name: str
    url: str
