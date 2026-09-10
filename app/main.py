from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import models
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import (ProgressCreate,
    ProgressResponse,)
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
    # OAuth2 uses "username" field.
    # We are using email as username.
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
        
@app.post("/progress", response_model=ProgressResponse)
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
        existing_progress.progress_percentage = progress.progress_percentage
        existing_progress.is_completed = progress.is_completed

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