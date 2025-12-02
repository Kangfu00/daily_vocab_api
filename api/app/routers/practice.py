# api/app/routers/practice.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Word, PracticeSession
from app.schemas import ValidateSentenceRequest, ValidateSentenceResponse
from app.utils import mock_ai_validation
from datetime import datetime

router = APIRouter()

@router.post("/validate-sentence", response_model=ValidateSentenceResponse)
def validate_sentence(
    request: ValidateSentenceRequest,
    db: Session = Depends(get_db)
):
    # 1. หาคำศัพท์จาก ID
    word_data = db.query(Word).filter(Word.id == request.word_id).first()
    if not word_data:
        raise HTTPException(status_code=404, detail="Word not found")

    # 2. ตรวจสอบประโยค (ใช้ Mock AI)
    ai_feedback = mock_ai_validation(
        sentence=request.sentence,
        target_word=word_data.word,
        difficulty=word_data.difficulty_level
    )
    
    # 3. *** บันทึกลงฐานข้อมูล (สำคัญมาก) ***
    new_session = PracticeSession(
        word_id=request.word_id,
        user_sentence=request.sentence,
        score=ai_feedback['score'], 
        feedback=ai_feedback['suggestion'],
        corrected_sentence=ai_feedback['corrected_sentence'],
        practiced_at=datetime.utcnow()
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return ValidateSentenceResponse(
        score=ai_feedback['score'],
        level=ai_feedback['level'],
        suggestion=ai_feedback['suggestion'],
        corrected_sentence=ai_feedback['corrected_sentence']
    )