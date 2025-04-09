from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict
from uuid import uuid4

from ai_module import generate_student_report
from auth import router as auth_router
from google_auth import router as google_auth_router
from report_module import Student, Assessment, process_assessment, generate_report

app = FastAPI()

# ✅ Router'ları ekle
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(google_auth_router, prefix="/auth/google", tags=["Google Auth"])

# ✅ CORS (Framer için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🎯 Basit AI raporu için endpoint
class ReportRequest(BaseModel):
    ders_adı: str
    guclu_yonler: str
    gelisim_alanlari: str
    oneriler: str

@app.post("/generate-report", tags=["Basit AI Rapor"])
async def generate_report(request: ReportRequest):
    rapor = generate_student_report(
        ders_adı=request.ders_adı,
        guclu_yonler=request.guclu_yonler,
        gelisim_alanlari=request.gelisim_alanlari,
        oneriler=request.oneriler
    )
    return {"rapor": rapor.content}


# 🎓 Tam AI destekli öğrenci değerlendirme formu
class FullReportRequest(BaseModel):
    name: str
    surname: str
    birth_date: str
    grade: str
    age_group: str
    responses: Dict[str, Dict[str, str]]
    assessor_name: str
    assessor_role: str

@app.post("/student-full-report", tags=["AI Raporlama"])
async def student_full_report(request: FullReportRequest):
    student = Student(
        student_id=str(uuid4()),
        name=request.name,
        surname=request.surname,
        birth_date=request.birth_date,
        grade=request.grade,
        age_group=request.age_group
    )

    assessment = Assessment(
        assessment_id=str(uuid4()),
        student_id=student.student_id,
        assessor_name=request.assessor_name,
        assessor_role=request.assessor_role,
        date=datetime.now().strftime("%Y-%m-%d")
    )

    for category, subcats in request.responses.items():
        for subcat, answer in subcats.items():
            assessment.add_response(category, subcat, answer)

    results = process_assessment(assessment, student)
    report = generate_report(student, assessment, results)

    return report.to_dict()
