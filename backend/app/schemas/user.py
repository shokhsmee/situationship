from app.core.enums import UserRole
from app.schemas.base import ORMModel


class UserRead(ORMModel):
    id: int
    telegram_id: int | None = None
    username: str | None = None
    display_name: str
    language: str
    role: UserRole
