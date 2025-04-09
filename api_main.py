from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_module import generate_student_report

# ✅ FastAPI uygulamasını oluştur
app = FastAPI()

# ✅ CORS (dış bağlantı) ayarları — Framer gibi platformlar için gerekli
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # "*": her yerden istek kabul edilir. Yayına alırken alan adını sınırlayabilirsin.
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

# ✅ /generate-report endpoint'i — Framer buraya POST isteği gönderir
@app.post("/generate-report")
async def generate_report(request: ReportRequest):
    rapor = generate_student_report(
        ders_adı=request.ders_adı,
        guclu_yonler=request.guclu_yonler,
        gelisim_alanlari=request.gelisim_alanlari,
        oneriler=request.oneriler
    )
    return {"rapor": rapor.content}
