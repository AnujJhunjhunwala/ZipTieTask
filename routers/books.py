from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
import sqlalchemy
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
import models
from sqlalchemy import func

router = APIRouter(tags=["books"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class BookRequest(BaseModel):
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

# Fetch book by ID
@router.get("/book/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(db: db_dependency, book_id: int = Path(gt=0)):
    book_model = db.query(models.Book).filter(models.Book.book_id == book_id).first()
    if book_model is not None:
        return book_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

# Update book 
@router.put("/book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(db: db_dependency, 
                        book_id: int, 
                        book_request: BookRequest):
    book_model = db.query(models.Book).filter(models.Book.book_id == book_id).first()
    if book_model is None:
        raise HTTPException(status_code=404, detail="Book not found")
    book_model.title = book_request.title
    book_model.genre = book_request.genre
    book_model.year_published = book_request.year_published
    book_model.author_id = book_request.author_id
    book_model.in_stock = book_request.in_stock
    db.add(book_model)
    db.commit()

# Delete book
@router.delete("/book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(db: db_dependency, book_id: int = Path(gt=0)):
    book_model = db.query(models.Book).filter(models.Book.book_id == book_id).first()
    if book_model is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.query(models.Book).filter(models.Book.book_id == book_id).delete()
    db.commit()

# Search books by published year
@router.get("/books/year/{year_published}", status_code=status.HTTP_200_OK)
async def search_books_by_year(db: db_dependency, year_published: int = Path(gt=1000)):
    books_search = db.query(models.Book).filter(models.Book.year_published == year_published).all()
    if len(books_search) != 0:
        return books_search
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books in stock for year "+str(year_published))

# Check availability of book
@router.get("/book/{book_id}/availability", status_code=status.HTTP_200_OK)
async def check_book_availability(db: db_dependency, book_id: int = Path(gt=0)):
    book_model = db.query(models.Book).filter(models.Book.book_id == book_id).first()
    if book_model is not None:
        return {"in_stock": book_model.in_stock}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

# Get books by country of author
@router.get("/books/author_country/{country}", status_code=status.HTTP_200_OK)
async def get_books_by_author_country(db: db_dependency, country: str):
    books_search = db.query(models.Book).join(models.Author).filter(func.lower(models.Author.country) == country.lower()).all()
    if len(books_search) != 0:
        return books_search
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books found for authors from "+country)