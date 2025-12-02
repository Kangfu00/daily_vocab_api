from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, cast, String
from typing import List
import math # เพิ่มการนำเข้า math เพื่อใช้ในการปัดเศษ

from app.database import get_db
from app.models import Word, PracticeSession
from app.schemas import SummaryResponse, HistoryItem

router = APIRouter()


@router.get("/summary", response_model=SummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    """Get overall practice statistics"""
    
    total_practices = db.query(PracticeSession).count()
    
    average_score_raw = db.query(func.avg(PracticeSession.score)).scalar()
    # ปัดเศษคะแนนเฉลี่ยเป็นทศนิยม 1 ตำแหน่ง หรือเป็น 0.0 ถ้าไม่มีข้อมูล
    average_score = round(float(average_score_raw), 1) if average_score_raw is not None else 0.0
    
    total_words_practiced = db.query(func.count(distinct(PracticeSession.word_id))).scalar()
    
    # Distribution by level
    level_distribution_query = db.query(
        Word.difficulty_level,
        func.count(PracticeSession.id).label('count')
    ).join(PracticeSession, PracticeSession.word_id == Word.id).group_by(Word.difficulty_level).all()
    
    # กำหนดค่าเริ่มต้นเพื่อให้แน่ใจว่ามี key ครบ
    level_distribution = {
        'Beginner': 0,
        'Intermediate': 0,
        'Advanced': 0
    }
    
    for level, count in level_distribution_query:
        level_distribution[level] = count
    
    return SummaryResponse(
        total_practices=total_practices,
        average_score=average_score,
        total_words_practiced=total_words_practiced,
        level_distribution=level_distribution
    )


@router.get("/history", response_model=List[HistoryItem])
def get_history(limit: int = 10, db: Session = Depends(get_db)):
    """Get last N practice sessions"""
    
    # Query ข้อมูลพร้อม join word table เพื่อดึงคำศัพท์
    history_records = db.query(
        PracticeSession.id,
        Word.word,
        PracticeSession.user_sentence,
        PracticeSession.score,
        PracticeSession.feedback,
        PracticeSession.practiced_at
    ).join(Word, PracticeSession.word_id == Word.id).order_by(PracticeSession.practiced_at.desc()).limit(limit).all()
    
    # Map ผลลัพธ์เข้า Pydantic Schema
    history_items = []
    for id, word, user_sentence, score, feedback, practiced_at in history_records:
        history_items.append(HistoryItem(
            id=id,
            word=word,
            user_sentence=user_sentence,
            score=round(float(score), 1),
            feedback=feedback,
            practiced_at=practiced_at.isoformat() # แปลง datetime เป็น string
        ))# api/app/routers/stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List
import math

from app.database import get_db
from app.models import Word, PracticeSession
from app.schemas import SummaryResponse, HistoryItem

router = APIRouter()

@router.get("/summary", response_model=SummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    # นับจำนวนครั้งที่ฝึก
    total_practices = db.query(PracticeSession).count()
    
    # หาคะแนนเฉลี่ย
    average_score_raw = db.query(func.avg(PracticeSession.score)).scalar()
    average_score = round(float(average_score_raw), 1) if average_score_raw else 0.0
    
    # นับจำนวนคำศัพท์ที่ไม่ซ้ำกัน
    total_words_practiced = db.query(func.count(distinct(PracticeSession.word_id))).scalar()
    
    # นับจำนวนตามระดับความยาก (Join ตาราง Word)
    level_counts = db.query(
        Word.difficulty_level,
        func.count(PracticeSession.id)
    ).join(PracticeSession, PracticeSession.word_id == Word.id)\
     .group_by(Word.difficulty_level).all()
    
    # เตรียมข้อมูลส่งกลับ (Default เป็น 0)
    level_distribution = {'Beginner': 0, 'Intermediate': 0, 'Advanced': 0}
    for level, count in level_counts:
        if level in level_distribution:
            level_distribution[level] = count
    
    return SummaryResponse(
        total_practices=total_practices,
        average_score=average_score,
        total_words_practiced=total_words_practiced,
        level_distribution=level_distribution
    )

@router.get("/history", response_model=List[HistoryItem])
def get_history(limit: int = 10, db: Session = Depends(get_db)):
    # ดึงข้อมูลประวัติล่าสุด
    history_records = db.query(
        PracticeSession.id,
        Word.word,
        PracticeSession.user_sentence,
        PracticeSession.score,
        PracticeSession.feedback,
        PracticeSession.practiced_at
    ).join(Word, PracticeSession.word_id == Word.id)\
     .order_by(PracticeSession.practiced_at.desc())\
     .limit(limit).all()
    
    # แปลงข้อมูลให้ตรงกับ Schema
    results = []
    for record in history_records:
        results.append(HistoryItem(
            id=record.id,
            word=record.word,
            user_sentence=record.user_sentence,
            score=float(record.score) if record.score else 0.0,
            feedback=record.feedback,
            practiced_at=record.practiced_at
        ))
        
    return results
        
    return history_items