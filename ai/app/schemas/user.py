from sqlmodel import Field, SQLModel


class Book(SQLModel, table=True):
    """Book model for database storage."""
    __tablename__ = "books"
    
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    author: str
    pages: int | None = Field(default=None)