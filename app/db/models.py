"""SQLAlchemy models for the STAR learning community."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin, TimestampMixin


class User(IDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean(),
        nullable=False,
        default=True,
        server_default=sa.true(),
    )

    authored_courses: Mapped[list["Course"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Course(IDMixin, TimestampMixin, Base):
    __tablename__ = "courses"
    __table_args__ = (sa.Index("ix_courses_author_id_is_public", "author_id", "is_public"),)

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    forked_from_id: Mapped[int | None] = mapped_column(
        ForeignKey("courses.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    is_public: Mapped[bool] = mapped_column(
        sa.Boolean(),
        nullable=False,
        default=False,
        server_default=sa.false(),
    )

    author: Mapped["User"] = relationship(back_populates="authored_courses")
    forked_from: Mapped["Course | None"] = relationship(
        back_populates="forks",
        remote_side="Course.id",
    )
    forks: Mapped[list["Course"]] = relationship(back_populates="forked_from")
    versions: Mapped[list["CourseVersion"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="CourseVersion.published_at",
    )
    chapters: Mapped[list["Chapter"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Chapter.order_index",
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course")


class CourseVersion(IDMixin, Base):
    __tablename__ = "course_versions"
    __table_args__ = (UniqueConstraint("course_id", "version_tag"),)

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    snapshot_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    published_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )

    course: Mapped["Course"] = relationship(back_populates="versions")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course_version")


class Chapter(IDMixin, TimestampMixin, Base):
    __tablename__ = "chapters"
    __table_args__ = (UniqueConstraint("course_id", "order_index"),)

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    order_index: Mapped[int] = mapped_column(nullable=False)

    course: Mapped["Course"] = relationship(back_populates="chapters")
    knowledge_points: Mapped[list["KnowledgePoint"]] = relationship(
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="KnowledgePoint.order_index",
    )
    resources: Mapped[list["Resource"]] = relationship(
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="Resource.order_index",
    )


class KnowledgePoint(IDMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_points"
    __table_args__ = (UniqueConstraint("chapter_id", "order_index"),)

    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    order_index: Mapped[int] = mapped_column(nullable=False)

    chapter: Mapped["Chapter"] = relationship(back_populates="knowledge_points")
    progress_records: Mapped[list["KnowledgePointProgress"]] = relationship(
        back_populates="knowledge_point",
        cascade="all, delete-orphan",
    )


class Resource(IDMixin, TimestampMixin, Base):
    __tablename__ = "resources"
    __table_args__ = (UniqueConstraint("chapter_id", "order_index"),)

    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="link",
        server_default="link",
    )
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    order_index: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        server_default=sa.text("0"),
    )

    chapter: Mapped["Chapter"] = relationship(back_populates="resources")


class Enrollment(IDMixin, Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id"),
        CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name="progress_percent_range",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    course_version_id: Mapped[int] = mapped_column(
        ForeignKey("course_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    progress_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default=sa.text("0.00"),
    )
    joined_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")
    course_version: Mapped["CourseVersion"] = relationship(back_populates="enrollments")
    knowledge_point_progress: Mapped[list["KnowledgePointProgress"]] = relationship(
        back_populates="enrollment",
        cascade="all, delete-orphan",
    )


class KnowledgePointProgress(IDMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_point_progress"
    __table_args__ = (UniqueConstraint("enrollment_id", "knowledge_point_id"),)

    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("enrollments.id", ondelete="CASCADE"),
        nullable=False,
    )
    knowledge_point_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_points.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_completed: Mapped[bool] = mapped_column(
        sa.Boolean(),
        nullable=False,
        default=False,
        server_default=sa.false(),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )

    enrollment: Mapped["Enrollment"] = relationship(back_populates="knowledge_point_progress")
    knowledge_point: Mapped["KnowledgePoint"] = relationship(back_populates="progress_records")
