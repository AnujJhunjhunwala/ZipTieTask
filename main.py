from fastapi import FastAPI
import models
from database import engine
from routers import authors, books

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(authors.router)
app.include_router(books.router)