from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
)

from sqlalchemy.orm import relationship

from app.database import Base


# ============================================================
# USER MODEL
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        default="student",
        nullable=False
    )

    language = Column(
        String(50),
        default="Hindi",
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    lessons = relationship(
        "Lesson",
        back_populates="creator"
    )

    quiz_attempts = relationship(
        "QuizAttempt",
        back_populates="user"
    )

    achievements = relationship(
        "Achievement",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    certificates = relationship(
        "Certificate",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ============================================================
# SUBJECT MODEL
# ============================================================

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    language = Column(
        String(50),
        default="Hindi",
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    lessons = relationship(
        "Lesson",
        back_populates="subject",
        cascade="all, delete-orphan"
    )


# ============================================================
# LESSON MODEL
# ============================================================

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    content = Column(
        Text,
        nullable=True
    )

    language = Column(
        String(50),
        default="Hindi",
        nullable=False
    )

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    subject = relationship(
        "Subject",
        back_populates="lessons"
    )

    creator = relationship(
        "User",
        back_populates="lessons"
    )

    quiz_questions = relationship(
        "QuizQuestion",
        back_populates="lesson",
        cascade="all, delete-orphan"
    )


# ============================================================
# PROGRESS MODEL
# ============================================================

class Progress(Base):
    __tablename__ = "progress"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=False
    )

    progress_percentage = Column(
        Integer,
        default=0,
        nullable=False
    )

    is_completed = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# ============================================================
# QUIZ QUESTION MODEL
# ============================================================

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=False
    )

    question = Column(
        Text,
        nullable=False
    )

    option_a = Column(
        Text,
        nullable=False
    )

    option_b = Column(
        Text,
        nullable=False
    )

    option_c = Column(
        Text,
        nullable=False
    )

    option_d = Column(
        Text,
        nullable=False
    )

    correct_answer = Column(
        String(1),
        nullable=False
    )

    explanation = Column(
        Text,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    lesson = relationship(
        "Lesson",
        back_populates="quiz_questions"
    )

    answers = relationship(
        "QuizAnswer",
        back_populates="question"
    )


# ============================================================
# QUIZ ATTEMPT MODEL
# ============================================================

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=False
    )

    total_questions = Column(
        Integer,
        default=0,
        nullable=False
    )

    correct_answers = Column(
        Integer,
        default=0,
        nullable=False
    )

    score = Column(
        Integer,
        default=0,
        nullable=False
    )

    completed = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="quiz_attempts"
    )

    answers = relationship(
        "QuizAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan"
    )


# ============================================================
# QUIZ ANSWER MODEL
# ============================================================

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    attempt_id = Column(
        Integer,
        ForeignKey("quiz_attempts.id"),
        nullable=False
    )

    question_id = Column(
        Integer,
        ForeignKey("quiz_questions.id"),
        nullable=False
    )

    selected_answer = Column(
        String(1),
        nullable=False
    )

    is_correct = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    attempt = relationship(
        "QuizAttempt",
        back_populates="answers"
    )

    question = relationship(
        "QuizQuestion",
        back_populates="answers"
    )


# ============================================================
# ACHIEVEMENT MODEL
# ============================================================

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=True
    )

    achievement_type = Column(
        String(50),
        default="lesson_completion",
        nullable=False
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    unlocked_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="achievements"
    )


# ============================================================
# CERTIFICATE MODEL
# ============================================================

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    certificate_id = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=False
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    score = Column(
        Integer,
        default=0,
        nullable=False
    )

    issued_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="certificates"
    )