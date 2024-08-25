from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
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

class AuthorRequest(BaseModel):
    author_id: int = Field(gt=0)
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    country: str = Field(min_length=3, max_length=50)

# Add new author
@router.post("/author", status_code=status.HTTP_201_CREATED)
async def create_author(db: db_dependency, author_request: AuthorRequest):
    author_model = models.Author(**author_request.model_dump())
    db.add(author_model)
    db.commit()

# Fetch all authors
@router.get("/authors", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(models.Author).all()

# Fetch author by ID
@router.get("/author/{author_id}", status_code=status.HTTP_200_OK)
async def read_author(db: db_dependency, author_id: int = Path(gt=0)):
    author_model = db.query(models.Author).filter(models.Author.author_id == author_id).first()
    if author_model is not None:
        return author_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")