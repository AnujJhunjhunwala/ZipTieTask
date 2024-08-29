from fastapi import FastAPI, responses
import models
from database import engine
from routers import authors, books

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(authors.router)
app.include_router(books.router)

@app.get("/")
def redirect_to_docs():
    return responses.RedirectResponse(url="/docs")