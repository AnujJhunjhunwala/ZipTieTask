from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path
import models
from database import SessionLocal, engine
from typing import Annotated
from sqlalchemy.orm import Session
import models
from pydantic import BaseModel, Field
from starlette import status

from routers import authors, books

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(authors.router)
app.include_router(books.router)

router = APIRouter()