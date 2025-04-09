"""
Öğrenci Rapor Sistemi - report_module.py

Bu modül, öğrenci değerlendirmelerini işleyip, güçlü yönler ve gelişim alanlarını tespit ederek
rapor oluşturmak için kullanılır. Yapay zeka destekli açıklama üretimi için ai_module ile birlikte çalışır.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

from ai_module import get_ai_response  # OpenAI entegrasyonu

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
        self.age_group = age_group  # "early_childhood", "primary", "middle", "high"
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

    def get_response(self, category: str, subcategory: str) -> Any:
        return self.responses.get(category, {}).get(subcategory)

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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Report':
        report = cls(data["report_id"], data["student_id"], data["assessment_id"], data["date"])
        report.content = data.get("content", {})
        report.recommendations = data.get("recommendations", {})
        return report

# ============================================================================
# SORU SEÇENEKLERİ (KISALTILMIŞ)
# ============================================================================

def load_question_definitions() -> Dict[str, Any]:
    return {
        "academic": {
            "performance": {
                "options": [
                    "Beklentilerin çok üzerinde",
                    "Beklentilerin üzerinde",
                    "Beklentileri karşılıyor",
                    "Beklentileri kısmen karşılıyor",
                    "Beklentilerin altında"
                ]
            }
        },
        "skills": {
            "problem_solving": {
                "options": [
                    "Çok yetkin",
                    "Yetkin",
                    "Orta",
                    "Gelişmekte",
                    "Başlangıç aşamasında"
                ]
            }
        }
    }

# ============================================================================
# DEĞERLENDİRME ANALİZ
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
            if options and response in options[:2]:  # İlk 2 seçenek güçlü sayılır
                strengths.append({"category": category, "subcategory": subcat, "response": response})
    return strengths


def identify_growth_areas(assessment: Assessment) -> List[Dict[str, Any]]:
    growth_areas = []
    for category, subcats in assessment.responses.items():
        for subcat, response in subcats.items():
            options = load_question_definitions().get(category, {}).get(subcat, {}).get("options", [])
            if options and response in options[-2:]:  # Son 2 seçenek gelişim alanı sayılır
                growth_areas.append({"category": category, "subcategory": subcat, "response": response})
    return growth_areas

# ============================================================================
# YAPAY ZEKA DESTEKLİ METİN ÜRETİMİ
# ============================================================================

def generate_description_ai(student: Student, category: str, subcategory: str, response: str) -> str:
    prompt = f"""
    Öğrenci: {student.full_name()}
    Yaş grubu: {student.age_group}
    Kategori: {category}
    Alt kategori: {subcategory}
    Yanıt: {response}

    Bu bilgilere göre öğrenciyi tanımlayan kısa, pozitif ve eğitici bir açıklama yaz.
    """
    return get_ai_response(prompt)

# ============================================================================
# RAPOR OLUŞTURMA
# ============================================================================

def generate_report(student: Student, assessment: Assessment, assessment_results: Dict[str, Any]) -> Report:
    report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    report = Report(
        report_id=report_id,
        student_id=student.student_id,
        assessment_id=assessment.assessment_id,
        date=datetime.now().strftime("%Y-%m-%d")
    )

    # AI destekli açıklamaları ekle
    descriptions = []
    for item in assessment_results["strengths"]:
        desc = generate_description_ai(student, item["category"], item["subcategory"], item["response"])
        descriptions.append(desc)

    growth_descriptions = []
    for item in assessment_results["growth_areas"]:
        desc = generate_description_ai(student, item["category"], item["subcategory"], item["response"])
        growth_descriptions.append(desc)

    report.content = {
        "student_name": student.full_name(),
        "grade": student.grade,
        "assessment_date": assessment.date,
        "assessor": assessment.assessor_name,
        "strengths": descriptions,
        "growth_areas": growth_descriptions,
        "summary": assessment_results["summary"]
    }

    return report

# ============================================================================
# DOSYA KAYIT
# ============================================================================

def save_report_to_file(report: Report, format: str = "json") -> str:
    directory = "reports"
    os.makedirs(directory, exist_ok=True)

    file_path = f"{directory}/{report.report_id}.{format}"
    try:
        if format == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        elif format == "html":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("<html><body><h1>Rapor Oluşturuldu</h1></body></html>")
        return file_path
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return ""

