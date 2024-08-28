from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
import models
from sqlalchemy import func, or_

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
async def read_all_authors(db: db_dependency, limit: int = Query(default=2, gt=0), offset: int = Query(default=0, ge=0)):
    authors = db.query(models.Author).offset(offset).limit(limit).all()
    return authors

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
async def search_authors(db: db_dependency, name: str = None, limit: int = Query(default=2, gt=0), offset: int = Query(default=0, ge=0)):
    if name is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter a name to search")
    query = db.query(models.Author).filter(
        or_(
            func.lower(models.Author.first_name).like(f"%{name.lower()}%"),
            func.lower(models.Author.last_name).like(f"%{name.lower()}%"),
            func.lower(func.concat(models.Author.first_name, ' ', models.Author.last_name)).like(f"%{name.lower()}%")
        )
    ).offset(offset).limit(limit).all()
    if len(query) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No authors found with given search criteria")
    return query
    