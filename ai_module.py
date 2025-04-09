import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# .env dosyasındaki API anahtarını yükle
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# ✅ Güncel model: ChatOpenAI (gpt-3.5 / gpt-4 uyumlu)
llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-3.5-turbo",  # veya "gpt-4"
    openai_api_key=openai_api_key
)

# 1. Report Module için basit çağrı fonksiyonu
def get_ai_response(prompt: str) -> str:
    """
    Yeni API ile uyumlu AI yanıtı döner.
    report_module.py bu fonksiyonu kullanır.
    """
    return llm.invoke(prompt)

# 2. Şablonlu özel rapor üretimi (isteğe bağlı)
student_report_template = """
Öğrencinin {ders_adı} dersi için gelişim raporunu hazırlayın.
Öğrencinin güçlü yönleri: {guclu_yonler}.
Geliştirilmesi gereken alanlar: {gelisim_alanlari}.
Öneriler: {oneriler}.
Ayrıntılı, kapsamlı ve yapılandırılmış bir rapor oluşturun.
"""

prompt_template = PromptTemplate(
    input_variables=["ders_adı", "guclu_yonler", "gelisim_alanlari", "oneriler"],
    template=student_report_template
)

def generate_student_report(ders_adı: str, guclu_yonler: str, gelisim_alanlari: str, oneriler: str):
    """
    Şablonla çalışan özel AI rapor fonksiyonu.
    """
    formatted_prompt = prompt_template.format(
        ders_adı=ders_adı,
        guclu_yonler=guclu_yonler,
        gelisim_alanlari=gelisim_alanlari,
        oneriler=oneriler
    )
    return llm.invoke(formatted_prompt)

# 3. Test amaçlı çalıştırma
if __name__ == "__main__":
    rapor = generate_student_report(
        ders_adı="Fen Bilimleri",
        guclu_yonler="Meraklı, deneylere açık",
        gelisim_alanlari="Kavramları derinlemesine analiz etme",
        oneriler="Daha fazla deney, grup çalışmaları, proje ödevleri"
    )
    print("🧠 Oluşturulan AI Raporu:\n")
    print(rapor)
