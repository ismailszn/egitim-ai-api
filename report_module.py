from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from typing import Dict, List

# FastAPI uygulaması
app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Yayına geçince domain ile sınırla
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth router'ları ekle
from auth import router as auth_router
from google_auth import router as google_auth_router

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(google_auth_router, prefix="/auth/google", tags=["Google Auth"])

# Rapor modülleri (circular import'u önlemek için fonksiyonla çağıracağız)
from report_module import Student, Assessment, process_assessment

# AI açıklama fonksiyonunu doğrudan burada içeri al
def generate_report(student, assessment, results):
    from report_module import generate_report as real_generate_report
    return real_generate_report(student, assessment, results)

# ========= FULL RAPOR TALEBİ MODELI =========
class StudentReportRequest(BaseModel):
    name: str
    surname: str
    birth_date: str
    grade: str
    age_group: str
    interests: List[str]
    learning_style: List[str]

    assessor_name: str
    assessor_role: str
    responses: Dict[str, Dict[str, str]]

# ========= ENDPOINT: AI Destekli Rapor Oluştur =========
@app.post("/student-full-report", tags=["AI Raporlama"])
async def student_full_report(request: StudentReportRequest):
    # 1. Öğrenci nesnesi oluştur
    student = Student(
        student_id=str(uuid4()),
        name=request.name,
        surname=request.surname,
        birth_date=request.birth_date,
        grade=request.grade,
        age_group=request.age_group
    )
    student.interests = request.interests
    student.learning_style = request.learning_style

    # 2. Değerlendirme oluştur
    assessment = Assessment(
        assessment_id=str(uuid4()),
        student_id=student.student_id,
        assessor_name=request.assessor_name,
        assessor_role=request.assessor_role,
        date=datetime.now().strftime("%Y-%m-%d")
    )

    # 3. Yanıtları ekle
    for category, subcats in request.responses.items():
        for subcat, response in subcats.items():
            assessment.add_response(category, subcat, response)

    # 4. Analiz ve Rapor oluştur
    results = process_assessment(assessment, student)
    report = generate_report(student, assessment, results)

    # 5. Raporu döndür
    return {
        "student": student.to_dict(),
        "assessment": assessment.to_dict(),
        "report": report.to_dict()
    }
