"""Post-related Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class PostBase(BaseModel):
    """Base post schema with common fields."""
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=10000)


class PostCreate(PostBase):
    """Schema for creating a new post."""
    author_id: int


class PostUpdate(BaseModel):
    """Schema for updating a post."""
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1, max_length=10000)


class PostResponse(PostBase):
    """Schema for post response."""
    id: int
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PostWithAuthor(PostResponse):
    """Schema for post with author information."""
    author_username: str
