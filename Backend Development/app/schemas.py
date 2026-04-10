"""Pydantic v2 schemas for course and knowledge point workflows."""

from __future__ import annotations

from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class InputSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ResourceCreate(InputSchema):
    title: str = Field(min_length=1, max_length=255)
    url: AnyHttpUrl
    resource_type: str = Field(default="link", min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=5000)
    order_index: int = Field(default=0, ge=0)


class ResourceRead(ReadSchema):
    id: int
    chapter_id: int
    title: str
    url: AnyHttpUrl
    resource_type: str
    description: str | None
    order_index: int
    created_at: datetime
    updated_at: datetime


class NestedKnowledgePointCreate(InputSchema):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    order_index: int = Field(ge=0)


class KnowledgePointCreate(NestedKnowledgePointCreate):
    chapter_id: int = Field(gt=0)


class KnowledgePointUpdate(InputSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    order_index: int | None = Field(default=None, ge=0)


class KnowledgePointRead(ReadSchema):
    id: int
    chapter_id: int
    title: str
    description: str | None
    order_index: int
    created_at: datetime
    updated_at: datetime


class ChapterCreate(InputSchema):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    order_index: int = Field(ge=0)
    knowledge_points: list[NestedKnowledgePointCreate] = Field(default_factory=list)
    resources: list[ResourceCreate] = Field(default_factory=list)


class ChapterRead(ReadSchema):
    id: int
    course_id: int
    title: str
    description: str | None
    order_index: int
    created_at: datetime
    updated_at: datetime
    knowledge_points: list[KnowledgePointRead] = Field(default_factory=list)
    resources: list[ResourceRead] = Field(default_factory=list)


class CourseVersionRead(ReadSchema):
    id: int
    course_id: int
    version_tag: str
    snapshot_data: dict | None
    published_at: datetime


class CourseCreate(InputSchema):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    is_public: bool = False
    chapters: list[ChapterCreate] = Field(default_factory=list)


class CourseUpdate(InputSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    is_public: bool | None = None


class CourseRead(ReadSchema):
    id: int
    author_id: int
    forked_from_id: int | None
    title: str
    description: str | None
    is_public: bool
    created_at: datetime
    updated_at: datetime
    versions: list[CourseVersionRead] = Field(default_factory=list)
    chapters: list[ChapterRead] = Field(default_factory=list)
