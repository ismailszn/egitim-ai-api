import json
import os
from datetime import datetime
from typing import Dict, List, Any

from ai_module import get_ai_response  # OpenAI API çağrısı

# ============================================================================
# VERİ MODELLERİ
# ============================================================================

class Student:
    def __init__(self, student_id: str, name: str, surname: str, birth_date: str, grade: str, age_group: str):
        self.student_id = student_id
        self.name = name
        self.surname = surname
        self.birth_date = birth_date
        self.grade = grade
        self.age_group = age_group
        self.interests: List[str] = []
        self.learning_style: List[str] = []

    def full_name(self) -> str:
        return f"{self.name} {self.surname}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "surname": self.surname,
            "birth_date": self.birth_date,
            "grade": self.grade,
            "age_group": self.age_group,
            "interests": self.interests,
            "learning_style": self.learning_style
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        student = cls(**{k: data[k] for k in ["student_id", "name", "surname", "birth_date", "grade", "age_group"]})
        student.interests = data.get("interests", [])
        student.learning_style = data.get("learning_style", [])
        return student


class Assessment:
    def __init__(self, assessment_id: str, student_id: str, assessor_name: str, assessor_role: str, date: str):
        self.assessment_id = assessment_id
        self.student_id = student_id
        self.assessor_name = assessor_name
        self.assessor_role = assessor_role
        self.date = date
        self.responses: Dict[str, Dict[str, Any]] = {}
        self.comments = ""

    def add_response(self, category: str, subcategory: str, response: Any) -> None:
        if category not in self.responses:
            self.responses[category] = {}
        self.responses[category][subcategory] = response

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "student_id": self.student_id,
            "assessor_name": self.assessor_name,
            "assessor_role": self.assessor_role,
            "date": self.date,
            "responses": self.responses,
            "comments": self.comments
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Assessment':
        assessment = cls(**{k: data[k] for k in ["assessment_id", "student_id", "assessor_name", "assessor_role", "date"]})
        assessment.responses = data.get("responses", {})
        assessment.comments = data.get("comments", "")
        return assessment


class Report:
    def __init__(self, report_id: str, student_id: str, assessment_id: str, date: str):
        self.report_id = report_id
        self.student_id = student_id
        self.assessment_id = assessment_id
        self.date = date
        self.content: Dict[str, Any] = {}
        self.recommendations: Dict[str, List[str]] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "student_id": self.student_id,
            "assessment_id": self.assessment_id,
            "date": self.date,
            "content": self.content,
            "recommendations": self.recommendations
        }

# ============================================================================
# SORU TANIMLARI
# ============================================================================

def load_question_definitions() -> Dict[str, Any]:
    with open("question_definitions.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ============================================================================
# ANALİZ VE YAPAY ZEKA
# ============================================================================

def process_assessment(assessment: Assessment, student: Student) -> Dict[str, Any]:
    results = {
        "strengths": identify_strengths(assessment),
        "growth_areas": identify_growth_areas(assessment),
        "summary": {cat: f"{len(sub)} yanıt" for cat, sub in assessment.responses.items()}
    }
    return results


def identify_strengths(assessment: Assessment) -> List[Dict[str, Any]]:
    strengths = []
    for category, subcats in assessment.responses.items():
        for subcat, response in subcats.items():
            options = load_question_definitions().get(category, {}).get(subcat, {}).get("options", [])
            if options and response in options[:2]:
                strengths.append({"category": category, "subcategory": subcat, "response": response})
    return strengths


def identify_growth_areas(assessment: Assessment) -> List[Dict[str, Any]]:
    growth_areas = []
    for category, subcats in assessment.responses.items():
        for subcat, response in subcats.items():
            options = load_question_definitions().get(category, {}).get(subcat, {}).get("options", [])
            if options and response in options[-2:]:
                growth_areas.append({"category": category, "subcategory": subcat, "response": response})
    return growth_areas


def generate_description_ai(student: Student, category: str, subcategory: str, response: str) -> str:
    prompt = f"""
Sen bir eğitim uzmanısın. Aşağıdaki öğrenci gözlem verilerini kullanarak, kısa ve pedagojik bir açıklama yaz:

Kurallar:
1. Öğrencinin adını tekrar etme.
2. Açıklama 1-2 cümle uzunluğunda olsun.
3. Abartıdan kaçın, açık ve dengeli bir üslup kullan.
4. Yanıt değeri olumsuzsa yapıcı ve teşvik edici dil kullan.
5. Uygunsuz ya da alakasız ifadeleri dikkate alma.
6. Başlık, giriş cümlesi veya sonuç paragrafı yazma — sadece net açıklama ver.

Bilgiler:
- Kategori: {category}
- Alt kategori: {subcategory}
- Yanıt: {response}
- Yaş grubu: {student.age_group}

Cevap:
"""
    return get_ai_response(prompt)

# ============================================================================
# RAPOR OLUŞTURMA
# ============================================================================

def generate_report(student: Student, assessment: Assessment, results: Dict[str, Any]) -> Report:
    report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    report = Report(
        report_id=report_id,
        student_id=student.student_id,
        assessment_id=assessment.assessment_id,
        date=datetime.now().strftime("%Y-%m-%d")
    )

    strengths = results["strengths"]
    growth_areas = results["growth_areas"]

    report.content = {
        "student_name": student.full_name(),
        "grade": student.grade,
        "assessment_date": assessment.date,
        "assessor": assessment.assessor_name,
        "strengths": [generate_description_ai(student, i["category"], i["subcategory"], i["response"]).content for i in strengths],
        "growth_areas": [generate_description_ai(student, i["category"], i["subcategory"], i["response"]).content for i in growth_areas],
        "summary": results["summary"]
    }

    return report


def save_report_to_file(report: Report, file_format: str = "json") -> str:
    output_dir = "raporlar"
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, f"{report.report_id}.{file_format}")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)

    return file_path
