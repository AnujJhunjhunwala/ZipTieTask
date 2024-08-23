from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean

class Author(Base):
    __tablename__ = "authors"

    author_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), index=True)
    last_name = Column(String(50), index=True)
    country = Column(String)

class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    genre = Column(String(50), index=True)
    year_published = Column(Integer)
    author_id = Column(Integer, ForeignKey("authors.author_id"))
    in_stock = Column(Boolean, default=True)