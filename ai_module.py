import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# .env dosyasındaki API anahtarını yükle
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# GPT-4o modelini tanımla
llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-4o",  
    openai_api_key=openai_api_key
)

# -------------------------------------------------------------------------
# 1. Temel AI çağrı fonksiyonu (string döndürür)
# -------------------------------------------------------------------------
def get_ai_response(prompt: str) -> str:
    return llm.invoke(prompt).content  # ✨ HATA BURADAYDI

# -------------------------------------------------------------------------
# 2. Basit Rapor Şablonu (Örnek)
# -------------------------------------------------------------------------
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

def generate_student_report(ders_adı: str, guclu_yonler: str, gelisim_alanlari: str, oneriler: str) -> str:
    formatted_prompt = prompt_template.format(
        ders_adı=ders_adı,
        guclu_yonler=guclu_yonler,
        gelisim_alanlari=gelisim_alanlari,
        oneriler=oneriler
    )
    return llm.invoke(formatted_prompt).content

# -------------------------------------------------------------------------
# 3. Zenginleştirilmiş Rapor Şablonu
# -------------------------------------------------------------------------
enriched_report_template = """
Sen bir eğitim uzmanısın. Elinde bir öğrencinin farklı alanlarda değerlendirme verileri bulunuyor. 
Bu verileri kullanarak, öğrenciye dair kapsamlı, pedagojik ve yapıcı bir rapor hazırlayacaksın.

Değerlendirme, öğrencinin akademik, sosyal, duygusal ve kişisel gelişimiyle ilgili verileri içeriyor.
Bu verileri kullanarak öğrencinin güçlü yanlarını, gelişim fırsatlarını ve geleceğe dönük önerileri belirt.

Öncelikli Pedagojik İlkeler:
- Öğrencinin adı geçmeyecek.
- Negatif alanları ‘gelişime açık yönler’ olarak ifade et; aşırı övgü veya kesin yargılardan kaçın.
- Vereceğin öneriler somut, gerçekçi ve eğitim bilimine uygun olsun.

Rapor Formatı:
1) Genel Durum Özeti (kısa bir giriş)
2) Akademik Değerlendirme
3) Sosyal ve Duygusal Gelişim
4) Beceri Değerlendirmesi
5) Kişisel Gelişim ve Motivasyon
6) Öğrencinin İlgi Alanları
7) Öneriler ve Sonuç (hem öğrenci hem de gerektiğinde öğretmen/veli için)

Her önerinin neden faydalı olduğunu, mümkün olduğunca kısa bir açıklamayla belirt.
Akademik fakat anlaşılır bir dil kullan; terminoloji gerekiyorsa tanımlayarak açıkla.

---
Elimizdeki veriler:
- Akademik Performans: {akademik_veri}
- Sosyal ve Duygusal Gelişim: {sosyal_veri}
- Beceri Değerlendirmesi: {beceri_veri}
- Kişisel Gelişim/Motivasyon: {kisisel_veri}
- İlgi Alanları: {ilgi_veri}

Lütfen yukarıdaki maddeleri dikkate alarak kapsamlı bir rapor hazırla.
"""

enriched_prompt_template = PromptTemplate(
    input_variables=["akademik_veri", "sosyal_veri", "beceri_veri", "kisisel_veri", "ilgi_veri"],
    template=enriched_report_template
)

def generate_enriched_student_report(
    akademik_veri: str,
    sosyal_veri: str,
    beceri_veri: str,
    kisisel_veri: str,
    ilgi_veri: str
) -> str:
    formatted_prompt = enriched_prompt_template.format(
        akademik_veri=akademik_veri,
        sosyal_veri=sosyal_veri,
        beceri_veri=beceri_veri,
        kisisel_veri=kisisel_veri,
        ilgi_veri=ilgi_veri
    )
    return llm.invoke(formatted_prompt).content

# -------------------------------------------------------------------------
# 4. Test amaçlı çalıştırma
# -------------------------------------------------------------------------
if __name__ == "__main__":
    rapor_basit = generate_student_report(
        ders_adı="Fen Bilimleri",
        guclu_yonler="Meraklı, deneylere açık",
        gelisim_alanlari="Kavramları derinlemesine analiz etme",
        oneriler="Daha fazla deney, grup çalışmaları, proje ödevleri"
    )
    print("🧠 Basit Rapor:\n", rapor_basit)

    rapor_zengin = generate_enriched_student_report(
        akademik_veri="Genel akademik başarı beklentilerin üzerinde",
        sosyal_veri="Arkadaşlarıyla işbirliği yapıyor ancak bazen çekingen davranıyor",
        beceri_veri="Problem çözme ve analitik düşünmede güçlü, sunum becerileri orta seviyede",
        kisisel_veri="Yeni deneyimlere açık, motivasyonu dalgalanabiliyor",
        ilgi_veri="Müzik ve spor faaliyetlerine ilgili"
    )
    print("\n🧠 Zenginleştirilmiş Rapor:\n", rapor_zengin)
