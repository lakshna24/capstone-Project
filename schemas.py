from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Course Schemas
class CourseBase(BaseModel):
    course_name: str
    credits: int = Field(..., ge=1, le=6, description="Credits must be between 1 and 6 inclusive")

class CourseCreate(CourseBase):
    student_id: int

class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    credits: Optional[int] = Field(None, ge=1, le=6)

class CourseResponse(CourseBase):
    id: int
    student_id: int

    model_config = ConfigDict(from_attributes=True)

# Student Schemas
class StudentBase(BaseModel):
    name: str
    email: str
    age: int = Field(..., gt=0, description="Age must be greater than 0")

    @field_validator("email")
    @classmethod
    def validate_email_contains_at(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Email must contain '@'")
        return v

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = Field(None, gt=0)

    @field_validator("email")
    @classmethod
    def validate_email_contains_at(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and "@" not in v:
            raise ValueError("Email must contain '@'")
        return v

class StudentResponse(StudentBase):
    id: int
    courses: List[CourseResponse] = []

    model_config = ConfigDict(from_attributes=True)
