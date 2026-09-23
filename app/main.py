from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from uuid import uuid4
from io import BytesIO
from app import schemas
from app.database import engine, Base, get_db
from app import models

from app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,

    SubjectCreate,
    SubjectResponse,

    LessonCreate,
    LessonResponse,

    ProgressCreate,
    ProgressResponse,

    TranslationRequest,
    TranslationResponse,

    QuizQuestionCreate,
    QuizQuestionResponse,

    QuizAnswerCreate,
    QuizAnswerResponse,

    QuizAttemptCreate,
    QuizAttemptResponse,

    QuizSubmission,
)

from app.auth import (
    hash_password,
    verify_password,
    create_access_token
)

from app.dependencies import get_current_user

from app.services.translation import (
    translate_text,
    SUPPORTED_LANGUAGES
)

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI-Powered Vernacular Education API",
    description="Backend for SIH26042",
    version="1.0.0"
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Vernacular Education Backend is running!"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "Backend is working properly"
    }


# ============================================================
# DATABASE TEST
# ============================================================

@app.get("/database-test")
def database_test(
    db: Session = Depends(get_db)
):
    try:
        users = db.query(models.User).count()

        return {
            "database": "Connected",
            "users_count": users
        }

    except Exception as e:
        return {
            "database": "Connection Failed",
            "error": str(e)
        }


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================

@app.get("/languages")
def get_languages():
    return {
        "languages": [
            {"name": "Hindi", "code": "hi-IN"},
            {"name": "English", "code": "en-IN"},
            {"name": "Bengali", "code": "bn-IN"},
            {"name": "Tamil", "code": "ta-IN"},
            {"name": "Telugu", "code": "te-IN"},
            {"name": "Marathi", "code": "mr-IN"},
            {"name": "Gujarati", "code": "gu-IN"},
            {"name": "Kannada", "code": "kn-IN"},
            {"name": "Malayalam", "code": "ml-IN"},
            {"name": "Punjabi", "code": "pa-IN"},
            {"name": "Odia", "code": "or-IN"},
            {"name": "Assamese", "code": "as-IN"},
            {"name": "Urdu", "code": "ur-IN"}
        ]
    }


# ============================================================
# REGISTER
# ============================================================

@app.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role,
        language=user.language
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role,
        "language": new_user.language
    }


# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(models.User)
        .filter(models.User.email == form_data.username)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": str(db_user.id),
            "email": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "role": db_user.role,
        "language": db_user.language
    }


# ============================================================
# MY PROFILE
# ============================================================

@app.get("/profile/me")
def get_my_profile(
    current_user: models.User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "language": current_user.language,
        "is_active": current_user.is_active
    }


# ============================================================
# CREATE SUBJECT
# ============================================================

@app.post(
    "/subjects",
    response_model=SubjectResponse
)
def create_subject(
    subject: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only teachers or admins can create subjects"
        )

    new_subject = models.Subject(
        name=subject.name,
        description=subject.description,
        language=subject.language
    )

    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)

    return new_subject


# ============================================================
# GET ALL SUBJECTS
# ============================================================

@app.get(
    "/subjects",
    response_model=list[SubjectResponse]
)
def get_subjects(
    db: Session = Depends(get_db)
):

    subjects = (
        db.query(models.Subject)
        .filter(models.Subject.is_active == True)
        .all()
    )

    return subjects


# ============================================================
# GET SINGLE SUBJECT
# ============================================================

@app.get(
    "/subjects/{subject_id}",
    response_model=SubjectResponse
)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db)
):

    subject = (
        db.query(models.Subject)
        .filter(models.Subject.id == subject_id)
        .first()
    )

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )

    return subject


# ============================================================
# CREATE LESSON
# ============================================================

@app.post(
    "/lessons",
    response_model=LessonResponse
)
def create_lesson(
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only teachers or admins can create lessons"
        )

    subject = (
        db.query(models.Subject)
        .filter(models.Subject.id == lesson.subject_id)
        .first()
    )

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )

    new_lesson = models.Lesson(
        title=lesson.title,
        description=lesson.description,
        content=lesson.content,
        language=lesson.language,
        subject_id=lesson.subject_id,
        created_by=current_user.id
    )

    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)

    return new_lesson


# ============================================================
# GET ALL LESSONS
# ============================================================

@app.get(
    "/lessons",
    response_model=list[LessonResponse]
)
def get_lessons(
    db: Session = Depends(get_db)
):

    lessons = (
        db.query(models.Lesson)
        .filter(models.Lesson.is_active == True)
        .all()
    )

    return lessons


# ============================================================
# GET SINGLE LESSON
# ============================================================

@app.get(
    "/lessons/{lesson_id}",
    response_model=LessonResponse
)
def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db)
):

    lesson = (
        db.query(models.Lesson)
        .filter(models.Lesson.id == lesson_id)
        .first()
    )

    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    return lesson


# ============================================================
# TRANSLATION API
# ============================================================

@app.post(
    "/translate",
    response_model=TranslationResponse
)
def translate(
    request: TranslationRequest
):

    try:

        translated_text = translate_text(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language
        )

        return {
            "original_text": request.text,
            "translated_text": translated_text,
            "source_language": request.source_language,
            "target_language": request.target_language
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected translation error: {str(e)}"
        )


# ============================================================
# CREATE / UPDATE PROGRESS
# ============================================================

@app.post(
    "/progress",
    response_model=ProgressResponse
)
def create_progress(
    progress: ProgressCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    existing_progress = (
        db.query(models.Progress)
        .filter(
            models.Progress.user_id == current_user.id,
            models.Progress.lesson_id == progress.lesson_id
        )
        .first()
    )

    if existing_progress:

        existing_progress.progress_percentage = (
            progress.progress_percentage
        )

        existing_progress.is_completed = (
            progress.is_completed
        )

        db.commit()
        db.refresh(existing_progress)

        return existing_progress

    new_progress = models.Progress(
        user_id=current_user.id,
        lesson_id=progress.lesson_id,
        progress_percentage=progress.progress_percentage,
        is_completed=progress.is_completed
    )

    db.add(new_progress)
    db.commit()
    db.refresh(new_progress)

    return new_progress


# ============================================================
# GET MY PROGRESS
# ============================================================

@app.get(
    "/progress/me",
    response_model=list[ProgressResponse]
)
def get_my_progress(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    progress = (
        db.query(models.Progress)
        .filter(
            models.Progress.user_id == current_user.id
        )
        .all()
    )

    return progress


# ============================================================
# GET PROGRESS FOR PARTICULAR LESSON
# ============================================================

@app.get(
    "/progress/lesson/{lesson_id}",
    response_model=ProgressResponse
)
def get_lesson_progress(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    progress = (
        db.query(models.Progress)
        .filter(
            models.Progress.user_id == current_user.id,
            models.Progress.lesson_id == lesson_id
        )
        .first()
    )

    if not progress:

        raise HTTPException(
            status_code=404,
            detail="Progress not found"
        )

    return progress


# ============================================================
# QUIZ - CREATE QUESTION
# ============================================================

@app.post(
    "/quiz/questions",
    response_model=QuizQuestionResponse
)
def create_quiz_question(
    question: QuizQuestionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only teachers or admins can create quiz questions"
        )

    lesson = (
        db.query(models.Lesson)
        .filter(models.Lesson.id == question.lesson_id)
        .first()
    )

    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    correct_answer = question.correct_answer.upper()

    if correct_answer not in ["A", "B", "C", "D"]:
        raise HTTPException(
            status_code=400,
            detail="correct_answer must be A, B, C or D"
        )

    new_question = models.QuizQuestion(
        lesson_id=question.lesson_id,
        question=question.question,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        correct_answer=correct_answer,
        explanation=question.explanation
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question


# ============================================================
# QUIZ - GET QUESTIONS FOR LESSON
# ============================================================

@app.get(
    "/quiz/lesson/{lesson_id}",
    response_model=list[QuizQuestionResponse]
)
def get_quiz_questions(
    lesson_id: int,
    db: Session = Depends(get_db)
):

    lesson = (
        db.query(models.Lesson)
        .filter(models.Lesson.id == lesson_id)
        .first()
    )

    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    questions = (
        db.query(models.QuizQuestion)
        .filter(
            models.QuizQuestion.lesson_id == lesson_id,
            models.QuizQuestion.is_active == True
        )
        .all()
    )

    return questions


# ============================================================
# QUIZ - START ATTEMPT
# ============================================================

@app.post(
    "/quiz/attempt",
    response_model=QuizAttemptResponse
)
def start_quiz_attempt(
    attempt: QuizAttemptCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    lesson = (
        db.query(models.Lesson)
        .filter(models.Lesson.id == attempt.lesson_id)
        .first()
    )

    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    total_questions = (
        db.query(models.QuizQuestion)
        .filter(
            models.QuizQuestion.lesson_id == attempt.lesson_id,
            models.QuizQuestion.is_active == True
        )
        .count()
    )

    if total_questions == 0:
        raise HTTPException(
            status_code=404,
            detail="No quiz questions found for this lesson"
        )

    new_attempt = models.QuizAttempt(
        user_id=current_user.id,
        lesson_id=attempt.lesson_id,
        total_questions=total_questions,
        correct_answers=0,
        score=0,
        completed=False
    )

    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    return new_attempt


# ============================================================
# QUIZ - SUBMIT QUIZ + UPDATE PROGRESS
# ============================================================

@app.post(
    "/quiz/submit",
    response_model=QuizAttemptResponse
)
def submit_quiz(
    submission: QuizSubmission,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    questions = (
        db.query(models.QuizQuestion)
        .filter(
            models.QuizQuestion.lesson_id == submission.lesson_id,
            models.QuizQuestion.is_active == True
        )
        .all()
    )

    if not questions:
        raise HTTPException(
            status_code=404,
            detail="No quiz questions found for this lesson"
        )

    question_map = {
        question.id: question
        for question in questions
    }

    total_questions = len(questions)

    # Find latest unfinished attempt
    attempt = (
        db.query(models.QuizAttempt)
        .filter(
            models.QuizAttempt.user_id == current_user.id,
            models.QuizAttempt.lesson_id == submission.lesson_id,
            models.QuizAttempt.completed == False
        )
        .order_by(models.QuizAttempt.id.desc())
        .first()
    )

    if not attempt:

        attempt = models.QuizAttempt(
            user_id=current_user.id,
            lesson_id=submission.lesson_id,
            total_questions=total_questions,
            correct_answers=0,
            score=0,
            completed=False
        )

        db.add(attempt)
        db.flush()

    correct_count = 0

    submitted_question_ids = set()

    for answer in submission.answers:

        if answer.question_id in submitted_question_ids:
            continue

        submitted_question_ids.add(answer.question_id)

        question = question_map.get(answer.question_id)

        if not question:
            continue

        selected_answer = answer.selected_answer.upper()

        if selected_answer not in ["A", "B", "C", "D"]:
            continue

        is_correct = (
            selected_answer == question.correct_answer.upper()
        )

        if is_correct:
            correct_count += 1

        quiz_answer = models.QuizAnswer(
            attempt_id=attempt.id,
            question_id=question.id,
            selected_answer=selected_answer,
            is_correct=is_correct
        )

        db.add(quiz_answer)

    # ========================================================
    # CALCULATE SCORE
    # ========================================================

    score = round(
        (correct_count / total_questions) * 100
    )

    attempt.total_questions = total_questions
    attempt.correct_answers = correct_count
    attempt.score = score
    attempt.completed = True

    # ========================================================
    # QUIZ + PROGRESS INTEGRATION
    # ========================================================

    existing_progress = (
        db.query(models.Progress)
        .filter(
            models.Progress.user_id == current_user.id,
            models.Progress.lesson_id == submission.lesson_id
        )
        .first()
    )

    if score >= 50:

        progress_percentage = 100
        is_completed = True

    else:

        progress_percentage = 50
        is_completed = False

    if existing_progress:

        existing_progress.progress_percentage = progress_percentage
        existing_progress.is_completed = is_completed

    else:

        new_progress = models.Progress(
            user_id=current_user.id,
            lesson_id=submission.lesson_id,
            progress_percentage=progress_percentage,
            is_completed=is_completed
        )

        db.add(new_progress)

    # ========================================================
    # ACHIEVEMENT INTEGRATION
    # ========================================================

    # Unlock achievement when the student completes the quiz
    # with a score of 50% or more.
    if score >= 50:
        existing_achievement = (
            db.query(models.Achievement)
            .filter(
                models.Achievement.user_id == current_user.id,
                models.Achievement.lesson_id == submission.lesson_id,
                models.Achievement.achievement_type == "lesson_completion"
            )
            .first()
        )

        if not existing_achievement:
            lesson = (
                db.query(models.Lesson)
                .filter(models.Lesson.id == submission.lesson_id)
                .first()
            )

            lesson_title = (
                lesson.title
                if lesson
                else f"Lesson {submission.lesson_id}"
            )

            new_achievement = models.Achievement(
                user_id=current_user.id,
                lesson_id=submission.lesson_id,
                achievement_type="lesson_completion",
                title="Lesson Completed",
                description=f"Completed quiz for {lesson_title}"
            )

            db.add(new_achievement)

    # ========================================================
    # CERTIFICATE INTEGRATION
    # ========================================================

    # Generate one certificate when the student completes the quiz
    # with a score of 50% or more.
    if score >= 50:
        existing_certificate = (
            db.query(models.Certificate)
            .filter(
                models.Certificate.user_id == current_user.id,
                models.Certificate.lesson_id == submission.lesson_id
            )
            .first()
        )

        if not existing_certificate:
            lesson = (
                db.query(models.Lesson)
                .filter(models.Lesson.id == submission.lesson_id)
                .first()
            )

            lesson_title = (
                lesson.title
                if lesson
                else f"Lesson {submission.lesson_id}"
            )

            certificate_number = f"CERT-{uuid4().hex[:12].upper()}"

            new_certificate = models.Certificate(
                certificate_id=certificate_number,
                user_id=current_user.id,
                lesson_id=submission.lesson_id,
                title="Certificate of Lesson Completion",
                description=(
                    f"{current_user.name} successfully completed "
                    f"the quiz for {lesson_title} with a score of {score}%."
                ),
                score=score
            )

            db.add(new_certificate)

    # ========================================================
    # SAVE EVERYTHING
    # ========================================================

    db.commit()
    db.refresh(attempt)

    return attempt


# ============================================================
# QUIZ - GET MY ATTEMPTS
# ============================================================

@app.get(
    "/quiz/attempts/me",
    response_model=list[QuizAttemptResponse]
)
def get_my_quiz_attempts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    attempts = (
        db.query(models.QuizAttempt)
        .filter(
            models.QuizAttempt.user_id == current_user.id
        )
        .order_by(models.QuizAttempt.id.desc())
        .all()
    )

    return attempts


# ============================================================
# QUIZ - GET PARTICULAR ATTEMPT
# ============================================================

@app.get(
    "/quiz/attempt/{attempt_id}",
    response_model=QuizAttemptResponse
)
def get_quiz_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    attempt = (
        db.query(models.QuizAttempt)
        .filter(
            models.QuizAttempt.id == attempt_id,
            models.QuizAttempt.user_id == current_user.id
        )
        .first()
    )

    if not attempt:
        raise HTTPException(
            status_code=404,
            detail="Quiz attempt not found"
        )

    return attempt

# ============================================================
# ACHIEVEMENT ENDPOINT
# ============================================================

@app.get(
    "/achievements/me",
    response_model=list[schemas.AchievementResponse]
)
def get_my_achievements(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    achievements = (
        db.query(models.Achievement)
        .filter(
            models.Achievement.user_id == current_user.id
        )
        .order_by(
            models.Achievement.unlocked_at.desc()
        )
        .all()
    )

    return achievements

# ============================================================
# CERTIFICATE ENDPOINT
# ============================================================

@app.get(
    "/certificates/me",
    response_model=list[schemas.CertificateResponse]
)
def get_my_certificates(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    certificates = (
        db.query(models.Certificate)
        .filter(
            models.Certificate.user_id == current_user.id
        )
        .order_by(
            models.Certificate.issued_at.desc()
        )
        .all()
    )

    return certificates

# ============================================================
# CERTIFICATE PDF DOWNLOAD
# ============================================================

@app.get("/certificates/{certificate_id}/download")
def download_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    certificate = (
        db.query(models.Certificate)
        .filter(
            models.Certificate.certificate_id == certificate_id,
            models.Certificate.user_id == current_user.id
        )
        .first()
    )

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    lesson = (
        db.query(models.Lesson)
        .filter(models.Lesson.id == certificate.lesson_id)
        .first()
    )

    lesson_title = (
        lesson.title
        if lesson
        else f"Lesson {certificate.lesson_id}"
    )

    # Create PDF in memory
    pdf_buffer = BytesIO()

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        pdf_buffer,
        pagesize=(page_width, page_height)
    )

    # --------------------------------------------------------
    # PAGE BACKGROUND
    # --------------------------------------------------------

    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.rect(
        0,
        0,
        page_width,
        page_height,
        fill=1,
        stroke=0
    )

    # Outer border
    pdf.setStrokeColor(colors.HexColor("#1E3A8A"))
    pdf.setLineWidth(5)
    pdf.rect(
        25,
        25,
        page_width - 50,
        page_height - 50,
        fill=0,
        stroke=1
    )

    # Inner border
    pdf.setStrokeColor(colors.HexColor("#C9A227"))
    pdf.setLineWidth(2)
    pdf.rect(
        38,
        38,
        page_width - 76,
        page_height - 76,
        fill=0,
        stroke=1
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    pdf.setFillColor(colors.HexColor("#1E3A8A"))
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 90,
        "CERTIFICATE OF COMPLETION"
    )

    pdf.setFillColor(colors.HexColor("#C9A227"))
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 118,
        "VERNACULAR EDUCATION"
    )

    # Decorative line
    pdf.setStrokeColor(colors.HexColor("#C9A227"))
    pdf.setLineWidth(2)
    pdf.line(
        page_width / 2 - 170,
        page_height - 132,
        page_width / 2 + 170,
        page_height - 132
    )

    # --------------------------------------------------------
    # BODY
    # --------------------------------------------------------

    pdf.setFillColor(colors.HexColor("#334155"))
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 175,
        "This certificate is proudly presented to"
    )

    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 220,
        current_user.name
    )

    pdf.setFillColor(colors.HexColor("#334155"))
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 255,
        "for successfully completing the lesson"
    )

    pdf.setFillColor(colors.HexColor("#1E3A8A"))
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 292,
        lesson_title
    )

    # Score
    pdf.setFillColor(colors.HexColor("#166534"))
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 335,
        f"Quiz Score: {certificate.score}%"
    )

    # --------------------------------------------------------
    # CERTIFICATE DETAILS
    # --------------------------------------------------------

    details_y = 125

    pdf.setFillColor(colors.HexColor("#475569"))
    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        75,
        details_y,
        f"Certificate ID: {certificate.certificate_id}"
    )

    issued_date = certificate.issued_at.strftime("%d %B %Y")

    pdf.drawRightString(
        page_width - 75,
        details_y,
        f"Issued on: {issued_date}"
    )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    pdf.setFillColor(colors.HexColor("#1E3A8A"))
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(
        page_width / 2,
        82,
        "AI-Powered Vernacular Education Platform"
    )

    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(
        page_width / 2,
        62,
        "SIH26042 • Mother Tongue-Based Primary Education"
    )

    pdf.showPage()
    pdf.save()

    pdf_buffer.seek(0)

    safe_certificate_id = certificate.certificate_id.replace("/", "_")

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="certificate_{safe_certificate_id}.pdf"'
            )
        }
    )

