from datetime import datetime
from pydantic import BaseModel


class SUser(BaseModel):
    user_id: int
    id: int
    username: str
    name: str
    age: int
    photo: str
    text: str
    gender: str
    interest: str
    liked: list[int]
    join_date: datetime
    active_date: datetime
    view_count: int
    claims_count: int
    claims: list[int]
    banned: bool
    noticed: list[int]
    visible: bool


class SActions(BaseModel):
    action_id: int
    from_id: int
    action_type: str
    to_id: int
    action_date: datetime
