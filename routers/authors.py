from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
import models
from sqlalchemy import func

router = APIRouter(tags=["authors"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class AuthorRequest(BaseModel):
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    country: str = Field(min_length=3, max_length=50)

# Add new author
@router.post("/author", status_code=status.HTTP_201_CREATED)
async def create_author(db: db_dependency, author_request: AuthorRequest):
    author_model = models.Author(
        first_name=author_request.first_name,
        last_name=author_request.last_name,
        country=author_request.country
    )
    db.add(author_model)
    db.commit()

# Fetch all authors
@router.get("/authors", status_code=status.HTTP_200_OK)
async def read_all_authors(db: db_dependency):
    return db.query(models.Author).all()

# Fetch author by ID
@router.get("/author/{author_id}", status_code=status.HTTP_200_OK)
async def read_author(db: db_dependency, author_id: int = Path(gt=0)):
    author_model = db.query(models.Author).filter(models.Author.author_id == author_id).first()
    if author_model is not None:
        return author_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

# Update author by ID
@router.put("/author/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_author(db: db_dependency, 
                        author_id: int, 
                        author_request: AuthorRequest):
    author_model = db.query(models.Author).filter(models.Author.author_id == author_id).first()
    if author_model is None:
        raise HTTPException(status_code=404, detail="Author not found")
    author_model.first_name = author_request.first_name
    author_model.last_name = author_request.last_name
    author_model.country = author_request.country
    db.add(author_model)
    db.commit()

# Delete author by ID
@router.delete("/author/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(db: db_dependency, author_id: int = Path(gt=0)):
    author_model = db.query(models.Author).filter(models.Author.author_id == author_id).first()
    if author_model is None:
        raise HTTPException(status_code=404, detail="Author not found")
    db.query(models.Author).filter(models.Author.author_id == author_id).delete()
    db.commit()

# Search authors by first name or last name
@router.get("/authors/search", status_code=status.HTTP_200_OK)
async def search_authors(db: db_dependency, first_name: str = None, last_name: str = None):
    if first_name is None and last_name is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either first_name or last_name must be provided")
    query = db.query(models.Author)
    if first_name is not None and last_name is not None:
        query = query.filter(func.lower(models.Author.first_name) == first_name.lower(), func.lower(models.Author.last_name) == last_name.lower())
    elif first_name is not None:
        query = query.filter(models.Author.first_name == first_name)
    else:
        query = query.filter(models.Author.last_name == last_name)
    if len(query.all()) != 0:
        return query.all()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No authors found with given search criteria")