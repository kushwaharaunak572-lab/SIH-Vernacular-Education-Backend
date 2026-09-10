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


# =========================================================
# USER MODEL
# =========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

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

    # Relationship with lessons created by this user
    lessons = relationship(
        "Lesson",
        back_populates="creator"
    )


# =========================================================
# SUBJECT MODEL
# =========================================================

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

    # Relationship with lessons
    lessons = relationship(
        "Lesson",
        back_populates="subject",
        cascade="all, delete-orphan"
    )


# =========================================================
# LESSON MODEL
# =========================================================

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

    # Relationship with Subject
    subject = relationship(
        "Subject",
        back_populates="lessons"
    )

    # Relationship with User
    creator = relationship(
        "User",
        back_populates="lessons"
    )


# =========================================================
# PROGRESS MODEL
# =========================================================

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)

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