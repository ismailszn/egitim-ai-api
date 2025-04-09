from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from report_module import Student, Assessment, process_assessment, generate_report
from uuid import uuid4
from datetime import datetime

# FastAPI uygulaması
app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Yayın alınca domainle sınırla!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Giriş endpoint'leri (auth, google) ============
from auth import router as auth_router
from google_auth import router as google_auth_router
app.include_router(auth_router)
app.include_router(google_auth_router)

# ============ FRAMER'DAN GELECEK FULL RAPOR VERİSİ ============
class StudentReportRequest(BaseModel):
    name: str
    surname: str
    birth_date: str
    grade: str
    age_group: str
    interests: list[str]
    learning_style: list[str]

    assessor_name: str
    assessor_role: str

    responses: dict

# ============ RAPOR OLUŞTURMA ENDPOINT ============
@app.post("/student-full-report")
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

    # 2. Değerlendirme nesnesi oluştur
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

    # 4. Değerlendirmeyi işle
    results = process_assessment(assessment, student)

    # 5. Raporu oluştur
    report = generate_report(student, assessment, results)

    # 6. Raporu geri döndür
    return {
        "student": student.to_dict(),
        "assessment": assessment.to_dict(),
        "report": report.to_dict()
    }
