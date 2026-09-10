from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


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
    
class ProgressCreate(BaseModel):
    lesson_id: int
    completed: bool = False
    score: int = 0


class ProgressResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    completed: bool
    score: int

    class Config:
        from_attributes = True
        
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

    class Config:
        from_attributes = True