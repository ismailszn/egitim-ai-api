from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai_module import generate_student_report
from auth import router as auth_router
from google_auth import router as google_auth_router

# ✅ FastAPI uygulamasını oluştur
app = FastAPI()

# ✅ Router'ları ekle
app.include_router(auth_router)              # e-posta ile giriş
app.include_router(google_auth_router)       # Google ile giriş

# ✅ CORS ayarları (Framer gibi dış bağlantılar için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ API'ye gelen verinin yapısı
class ReportRequest(BaseModel):
    ders_adı: str
    guclu_yonler: str
    gelisim_alanlari: str
    oneriler: str

# ✅ /generate-report endpoint'i
@app.post("/generate-report")
async def generate_report(request: ReportRequest):
    rapor = generate_student_report(
        ders_adı=request.ders_adı,
        guclu_yonler=request.guclu_yonler,
        gelisim_alanlari=request.gelisim_alanlari,
        oneriler=request.oneriler
    )
    return {"rapor": rapor.content}
