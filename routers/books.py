from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import sqlalchemy
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class BookRequest(BaseModel):
    book_id : int = Field(gt=0)
    title: str = Field(min_length=3, max_length=100)
    genre: str = Field(min_length=3, max_length=50)
    year_published: int = Field(gt=1000)
    author_id: int = Field(gt=0)
    in_stock: bool = Field(default=True)

# Add new book
@router.post("/book", status_code=status.HTTP_201_CREATED)
async def create_book(db: db_dependency, book_request: BookRequest):
    book_model = models.Book(**book_request.model_dump())
    try:
        db.add(book_model)
        db.commit()
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author ID not exist.")

# Fetch all books
@router.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books(db: db_dependency):
    return db.query(models.Book).all()