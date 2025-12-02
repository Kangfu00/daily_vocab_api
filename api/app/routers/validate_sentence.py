from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Word, PracticeSubmission
from app.schemas import SentenceRequest
from app.utils import mock_ai_validation

router = APIRouter()

@router.post("/validate-sentence")
def validate_sentence(request: SentenceRequest, db: Session = Depends(get_db)):

    # 1) ดึงข้อมูลคำศัพท์จาก Database
    word = db.query(Word).filter(Word.id == request.word_id).first()

    if not word:
        return {"error": "Word not found"}

    # 2) เรียก mock AI validation
    result = mock_ai_validation(
        request.sentence,
        word.word,
        word.difficulty_level
    )

    # 3) บันทึกข้อมูลลง Database
    submission = PracticeSubmission(
        user_id=1,
        word_id=request.word_id,
        submitted_sentence=request.sentence,
        score=result["score"]
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    # 4) ส่งผลลัพธ์กลับ
    return result
