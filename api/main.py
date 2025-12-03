from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
# import routers ทั้งหมด (รวม stats ด้วย)
from app.routers import words, practice, stats

# สร้าง FastAPI App
app = FastAPI(
    title="Vocabulary Practice API",
    version="1.0.0",
    description="API for vocabulary practice and learning"
)

# 1. แก้ปัญหา Database Connection Error ตอนเริ่ม
@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables check completed.")
    except Exception as e:
        print(f"⚠️ Warning: Could not connect to database immediately: {e}")

# 2. ตั้งค่า CORS ให้ Frontend (localhost:3000) เรียกมาหาได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # หรือ ["*"] เพื่อเปิดกว้าง
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. รวม Router ทั้งหมด (จุดสำคัญที่ทำให้ API ทำงานครบ)
# /api/word
app.include_router(words.router, prefix='/api', tags=['Words'])
# /api/validate-sentence
app.include_router(practice.router, prefix='/api', tags=['Practice'])
# /api/summary และ /api/history (Dashboard ใช้ตัวนี้!)
app.include_router(stats.router, prefix='/api', tags=['Stats'])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Vocabulary Practice API is ready!",
        "docs_url": "http://localhost:8000/docs"
    }