import os
import sys
from pathlib import Path

# Add backend directory to sys.path for relative imports resolution
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel


import database
import models
import schemas
import crud
import seed_data
import algorithms
import ai_service

# Initialize Database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="StudyTrack — Unified Study Management Platform",
    description="Full-Stack Study Management Platform with Integrated Algorithms Engine and Offline AI Assistant",
    version="1.0.0"
)

# Startup event for automatic database seeding
@app.on_event("startup")
def startup_db_seed():
    db = database.SessionLocal()
    try:
        seed_data.seed_db(db)
    finally:
        db.close()

# Explicit CORS configuration for http://localhost:5500
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for summarize endpoint
class SummarizeRequest(BaseModel):
    text: str

# ==========================================
# STUDENT ALGORITHM & REPORT STATIC ROUTES
# (Must be defined BEFORE dynamic /students/{student_id})
# ==========================================

@app.get("/students/sorted", response_model=List[schemas.StudentResponse])
def get_sorted_students(by: str = Query("age", description="Sort by 'age' or 'name'"), db: Session = Depends(database.get_db)):
    if by not in ["age", "name"]:
        raise HTTPException(status_code=400, detail="Query parameter 'by' must be 'age' or 'name'")
    students = crud.get_students(db)
    # Convert ORM to Pydantic responses first to sort in memory smoothly
    student_schemas = [schemas.StudentResponse.model_validate(s) for s in students]
    sorted_students = algorithms.insertion_sort_by_field(student_schemas, by)
    return sorted_students

@app.get("/students/search")
def search_student_by_name(name: str = Query(..., description="Student name to binary search"), db: Session = Depends(database.get_db)):
    students = crud.get_students(db)
    student_schemas = [schemas.StudentResponse.model_validate(s) for s in students]
    # Create name-sorted list using Python's built-in sorted() as required before binary search
    sorted_by_name = sorted(student_schemas, key=lambda s: s.name)
    result = algorithms.binary_search_by_name(sorted_by_name, name)
    if result == -1:
        raise HTTPException(status_code=404, detail=f"Student '{name}' not found")
    return result

@app.get("/students/report")
def get_roster_report(min_age: int = Query(21, description="Minimum age filter for report count"), db: Session = Depends(database.get_db)):
    students = crud.get_students(db)
    student_schemas = [schemas.StudentResponse.model_validate(s) for s in students]
    report_text = algorithms.format_roster_report(student_schemas)
    meeting_count = algorithms.count_students_meeting_min_age(student_schemas, min_age)
    return {
        "report": report_text,
        "count_meeting_min_age": meeting_count
    }

# ==========================================
# STUDENT CRUD ROUTES
# ==========================================

@app.post("/students/", response_model=schemas.StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(database.get_db)):
    # Check for duplicate email to avoid 500 unhandled DB exception
    existing = crud.get_student_by_email(db, student.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return crud.create_student(db, student)

@app.get("/students/", response_model=List[schemas.StudentResponse])
def read_students(min_age: Optional[int] = Query(None, description="Filter students with age >= min_age"), db: Session = Depends(database.get_db)):
    return crud.get_students(db, min_age=min_age)

@app.get("/students/{student_id}", response_model=schemas.StudentResponse)
def read_student(student_id: int, db: Session = Depends(database.get_db)):
    db_student = crud.get_student_by_id(db, student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return db_student

@app.patch("/students/{student_id}", response_model=schemas.StudentResponse)
def update_student(student_id: int, student_update: schemas.StudentUpdate, db: Session = Depends(database.get_db)):
    db_student = crud.get_student_by_id(db, student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    if student_update.email and student_update.email != db_student.email:
        existing = crud.get_student_by_email(db, student_update.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    updated = crud.update_student(db, student_id, student_update)
    return updated

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(database.get_db)):
    db_student = crud.get_student_by_id(db, student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    crud.delete_student(db, student_id)
    return {"message": f"Student {student_id} deleted successfully"}

@app.get("/students/{student_id}/course-count")
def get_student_course_count(student_id: int, db: Session = Depends(database.get_db)):
    db_student = crud.get_student_by_id(db, student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    count = crud.get_student_course_count(db, student_id)
    return {"student_id": student_id, "course_count": count}

# ==========================================
# COURSE CRUD ROUTES
# ==========================================

@app.post("/courses/", response_model=schemas.CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course: schemas.CourseCreate, db: Session = Depends(database.get_db)):
    db_student = crud.get_student_by_id(db, course.student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return crud.create_course(db, course)

@app.get("/courses/", response_model=List[schemas.CourseResponse])
def read_courses(db: Session = Depends(database.get_db)):
    return crud.get_courses(db)

@app.get("/courses/{course_id}", response_model=schemas.CourseResponse)
def read_course(course_id: int, db: Session = Depends(database.get_db)):
    db_course = crud.get_course_by_id(db, course_id)
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return db_course

@app.patch("/courses/{course_id}", response_model=schemas.CourseResponse)
def update_course(course_id: int, course_update: schemas.CourseUpdate, db: Session = Depends(database.get_db)):
    db_course = crud.get_course_by_id(db, course_id)
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return crud.update_course(db, course_id, course_update)

@app.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(database.get_db)):
    db_course = crud.get_course_by_id(db, course_id)
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    crud.delete_course(db, course_id)
    return {"message": f"Course {course_id} deleted successfully"}

# ==========================================
# ASSISTANT OFFLINE AI ROUTES
# ==========================================

@app.post("/assistant/summarize")
def summarize_text(request: SummarizeRequest):
    return ai_service.summarize_notes(request.text)

@app.get("/assistant/search")
def search_notes_api(query: str = Query("", description="Query for semantic note search")):
    return ai_service.search_notes(query)

# ==========================================
# STATIC FILE MOUNT
# (Mount frontend directory for single-process mode)
# ==========================================

frontend_path = Path(__file__).resolve().parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")
