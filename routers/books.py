from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
import sqlalchemy
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
import models
from sqlalchemy import func

router = APIRouter(tags=["books"])

def get_db():
    """
    Dependency that provides a database session.

    This function is used as a dependency in FastAPI to provide a database session
    to the request handlers. It creates a new session, yields it for use, and ensures
    that the session is closed after the request is processed.

    Yields:
        db (Session): A SQLAlchemy database session.
    """
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

@router.post("/book", status_code=status.HTTP_201_CREATED)
async def create_book(db: db_dependency, book_request: BookRequest):
    """
    This function creates a new book in the database.
    """
    book_model = models.Book(**book_request.model_dump())
    try:
        db.add(book_model)
        db.commit()
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author ID not exist.")

@router.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books(db: db_dependency, limit: int = Query(default=2, gt=0), offset: int = Query(default=0, ge=0)):
    """
    This function fetches all books from the database.
    """
    books = db.query(models.Book).offset(offset).limit(limit).all()
    return books

@router.get("/book/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(db: db_dependency, book_id: int = Path(gt=0)):
    """
    This function fetches a book by ID from the database.
    """
    book_model = db.query(models.Book).filter(models.Book.book_id == book_id).first()
    if book_model is not None:
        return book_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@router.put("/book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(db: db_dependency, 
                        book_id: int, 
                        book_request: BookRequest):
    """
    This function updates a book by ID in the database.
    """
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

@router.delete("/book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(db: db_dependency, book_id: int = Path(gt=0)):
    """
    This function deletes a book by ID from the database.
    """
    book_model = db.query(models.Book).filter(models.Book.book_id == book_id).first()
    if book_model is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.query(models.Book).filter(models.Book.book_id == book_id).delete()
    db.commit()

@router.get("/books/year/{year_published}", status_code=status.HTTP_200_OK)
async def search_books_by_year(db: db_dependency, year_published: int = Path(gt=1000), limit: int = Query(default=2, gt=0), offset: int = Query(default=0, ge=0)):
    """
    This function searches books by year in the database.
    """
    books_search = db.query(models.Book).filter(models.Book.year_published == year_published).offset(offset).limit(limit).all()
    if len(books_search) != 0:
        return books_search
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books in stock for year "+str(year_published))

@router.get("/book/{book_id}/availability", status_code=status.HTTP_200_OK)
async def check_book_availability(db: db_dependency, book_id: int = Path(gt=0)):
    """
    This function checks the availability of a book in the database.
    """
    book_model = db.query(models.Book).filter(models.Book.book_id == book_id).first()
    if book_model is not None:
        return {"in_stock": book_model.in_stock}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@router.get("/books/author_country/{country}", status_code=status.HTTP_200_OK)
async def get_books_by_author_country(db: db_dependency, country: str, limit: int = Query(default=2, gt=0), offset: int = Query(default=0, ge=0)):
    """
    This function fetches books by country of author from the database
    """
    books_search = db.query(models.Book).join(models.Author).filter(func.lower(models.Author.country) == country.lower()).offset(offset).limit(limit).all()
    if len(books_search) != 0:
        return books_search
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books found for authors from "+country)