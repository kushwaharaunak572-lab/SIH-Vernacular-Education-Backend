from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime


# ============================================================
# USER SCHEMAS
# ============================================================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "student"
    language: str = "Hindi"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    language: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# SUBJECT SCHEMAS
# ============================================================

class SubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    language: str = "Hindi"


class SubjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    language: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# LESSON SCHEMAS
# ============================================================

class LessonCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content: str
    language: str = "Hindi"
    subject_id: int


class LessonResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    content: str
    language: str
    subject_id: int
    created_by: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# TRANSLATION SCHEMAS
# ============================================================

class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str


# ============================================================
# PROGRESS SCHEMAS
# ============================================================

class ProgressCreate(BaseModel):
    lesson_id: int
    progress_percentage: int = 0
    is_completed: bool = False


class ProgressResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    progress_percentage: int
    is_completed: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# QUIZ QUESTION SCHEMAS
# ============================================================

class QuizQuestionCreate(BaseModel):
    lesson_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: Optional[str] = None


class QuizQuestionResponse(BaseModel):
    id: int
    lesson_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# QUIZ ANSWER SCHEMAS
# ============================================================

class QuizAnswerCreate(BaseModel):
    question_id: int
    selected_answer: str


class QuizAnswerResponse(BaseModel):
    id: int
    attempt_id: int
    question_id: int
    selected_answer: str
    is_correct: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# QUIZ ATTEMPT SCHEMAS
# ============================================================

class QuizAttemptCreate(BaseModel):
    lesson_id: int


class QuizAttemptResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    total_questions: int
    correct_answers: int
    score: int
    completed: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# QUIZ SUBMISSION SCHEMA
# ============================================================

class QuizSubmission(BaseModel):
    lesson_id: int
    answers: List[QuizAnswerCreate]


# ============================================================
# ACHIEVEMENT SCHEMAS
# ============================================================

class AchievementResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: Optional[int] = None
    achievement_type: str
    title: str
    description: Optional[str] = None
    unlocked_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CERTIFICATE SCHEMAS
# ============================================================

class CertificateResponse(BaseModel):
    id: int
    certificate_id: str
    user_id: int
    lesson_id: int
    title: str
    description: Optional[str] = None
    score: int
    issued_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)