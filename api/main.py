from fastapi import FastAPI
from app.routers import words
from app.database import Base, engine
from app.routers import validate_sentence

Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Vocabulary Practice API",
    version="1.0.0",
    description="API for vocabulary practice and learning"
)

app.include_router(words.router, prefix='/api', tags='words')

@app.get("/")
def read_root():
    return {
        "message": "Vocabulary Practice API",
        "version": "1.0.0",
        "endpoints": {
            "random_word": "/api/word",
            "validate": "/api/validate-sentence",
            "summary": "/api/summary",
            "history": "/api/history"
        }
    }
    
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(words.router, prefix='/api', tags=['words'])
from app.routers import words, practice
app.include_router(practice.router, prefix='/api', tags=["practice"])

from fastapi import FastAPI
from app.routers import validate_sentence

app = FastAPI()

app.include_router(validate_sentence.router, prefix="/api")