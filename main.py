from fastapi import APIRouter, FastAPI
import models
from database import engine
import models

from routers import authors, books

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(authors.router)
app.include_router(books.router)