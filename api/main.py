from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
# นำเข้า router ทั้งหมดที่ต้องใช้
from app.routers import words, practice, stats

# สร้างตารางฐานข้อมูลเมื่อเริ่มแอป (ย้ายมาใส่ใน event ตามที่เคยคุยกัน)
# เพื่อป้องกันปัญหา MySQL connection error ตอนเริ่ม
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

app = FastAPI(
    title="Vocabulary Practice API",
    version="1.0.0",
    description="API for vocabulary practice and learning"
)

# เรียกใช้ฟังก์ชันสร้างตารางตอน Startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# ตั้งค่า CORS (เพื่อให้ Frontend เชื่อมต่อได้)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # หรือระบุ ["http://localhost:3000"] เพื่อความปลอดภัย
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- รวม Router ทั้งหมดที่นี่ ---
app.include_router(words.router, prefix='/api', tags=['Words'])
app.include_router(practice.router, prefix='/api', tags=['Practice'])
app.include_router(stats.router, prefix='/api', tags=['Stats']) # เพิ่มบรรทัดนี้ Dashboard ถึงจะทำงาน!

@app.get("/")
def read_root():
    return {
        "message": "Vocabulary Practice API is running!",
        "version": "1.0.0",
        "endpoints": {
            "random_word": "/api/word",
            "validate": "/api/validate-sentence",
            "summary": "/api/summary",
            "history": "/api/history"
        }
    }