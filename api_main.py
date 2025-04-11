from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List
from uuid import uuid4

# Auth ve Google giriş
from auth import router as auth_router
from google_auth import router as google_auth_router

# Rapor modelleri ve işleyiciler
from report_module import Student, Assessment, process_assessment

# FastAPI uygulaması
app = FastAPI()

# CORS ayarları (Framer için açık)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Giriş endpoint'lerini ekle
app.include_router(auth_router)
app.include_router(google_auth_router, prefix="/auth/google", tags=["Google Auth"])


# =============================
# Basit AI destekli rapor
# =============================
from ai_module import generate_student_report

class SimpleReportRequest(BaseModel):
    ders_adı: str
    guclu_yonler: str
    gelisim_alanlari: str
    oneriler: str

@app.post("/generate-report", tags=["Basit AI Rapor"])
async def generate_simple_report(request: SimpleReportRequest):
    rapor = generate_student_report(
        ders_adı=request.ders_adı,
        guclu_yonler=request.guclu_yonler,
        gelisim_alanlari=request.gelisim_alanlari,
        oneriler=request.oneriler
    )
    return {"rapor": rapor.content}


# =============================
# Tam AI destekli öğrenci değerlendirmesi
# =============================
class FullReportRequest(BaseModel):
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

@app.post("/student-full-report", tags=["AI Raporlama"])
async def student_full_report(request: FullReportRequest):
    # Öğrenci nesnesi oluştur
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

    # Değerlendirme nesnesi oluştur
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

    # Circular import'u önlemek için burada çağırıyoruz
    from report_module import generate_report
    report = generate_report(student, assessment, results)

    return {
        "student": student.to_dict(),
        "assessment": assessment.to_dict(),
        "report": report.to_dict()
    }
