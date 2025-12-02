from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Word, PracticeSession
from app.schemas import ValidateSentenceRequest, ValidateSentenceResponse
from app.utils import mock_ai_validation # นำเข้า mock utility
from datetime import datetime

router = APIRouter()


@router.post("/validate-sentence", response_model=ValidateSentenceResponse)
def validate_sentence(
    request: ValidateSentenceRequest,
    db: Session = Depends(get_db)
):
    """
    Receive user sentence, validate it (using Mock AI/n8n), and save results to database.
    """
    # 1. Get word data
    # ใช้ word_id ที่รับมาเพื่อหาข้อมูลคำศัพท์
    word_data = db.query(Word).filter(Word.id == request.word_id).first()
    
    if not word_data:
        raise HTTPException(status_code=404, detail="Word not found")

    # 2. Mock AI validation (ใน Production จะแทนที่ด้วยการเรียก n8n Webhook)
    ai_feedback = mock_ai_validation(
        sentence=request.sentence,
        target_word=word_data.word,
        difficulty=word_data.difficulty_level
    )
    
    # 3. Save to database
    session = PracticeSession(
        word_id=request.word_id,
        user_sentence=request.sentence,
        # ต้องแปลง Decimal เป็น float ก่อนนำไปใช้ใน Pydantic Schema
        score=ai_feedback['score'], 
        feedback=ai_feedback['suggestion'],
        corrected_sentence=ai_feedback['corrected_sentence'],
        practiced_at=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # 4. Return the response
    return ValidateSentenceResponse(
        score=ai_feedback['score'],
        level=ai_feedback['level'],
        suggestion=ai_feedback['suggestion'],
        corrected_sentence=ai_feedback['corrected_sentence']
    )