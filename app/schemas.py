from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class PostUpdate(BaseModel):
    title: str | None = Field(
        default=None, min_length=1, max_length=255,
    )
    content: str | None = Field(
        default=None, min_length=1,
    )


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
