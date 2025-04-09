from report_module import (
    Student, Assessment,
    process_assessment,
    generate_report,
    save_report_to_file
)

def main():
    # Öğrenci oluştur
    student = Student(
        student_id="S001",
        name="Zeynep",
        surname="Demir",
        birth_date="2011-03-12",
        grade="5. Sınıf",
        age_group="primary"
    )
    student.interests = ["Resim", "Matematik"]
    student.learning_style = ["Görsel", "Sözel"]

    # Değerlendirme oluştur
    assessment = Assessment(
        assessment_id="A001",
        student_id=student.student_id,
        assessor_name="Mehmet Öğretmen",
        assessor_role="teacher",
        date="2025-04-08"
    )
    # Örnek yanıtlar
    assessment.add_response("academic", "performance", "Beklentilerin çok üzerinde")
    assessment.add_response("skills", "problem_solving", "Yetkin")

    # Değerlendirmeyi işle
    results = process_assessment(assessment, student)

    # Rapor oluştur
    report = generate_report(student, assessment, results)

    # Kaydet (JSON olarak)
    json_path = save_report_to_file(report, "json")

    print(f"\n✅ Rapor oluşturuldu ve kaydedildi: {json_path}\n")
    print("📋 Kısa Özet:")
    print(f"Öğrenci: {report.content['student_name']}")
    print(f"Güçlü Yönler:\n - " + "\n - ".join(report.content["strengths"]))
    print(f"Gelişim Alanları:\n - " + "\n - ".join(report.content["growth_areas"]))

if __name__ == "__main__":
    main()
