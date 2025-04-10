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
    student.interests = ["Sanat ve El Becerileri", "Müzik ve Performans"]
    student.learning_style = ["Görsel", "İşitsel"]

    # Değerlendirme oluştur
    assessment = Assessment(
        assessment_id="A001",
        student_id=student.student_id,
        assessor_name="Mehmet Öğretmen",
        assessor_role="teacher",
        date="2025-04-08"
    )

    # Kapsamlı örnek yanıtlar
    assessment.add_response("academic", "performance", "Beklentilerin çok üzerinde")
    assessment.add_response("academic", "learning_speed", "Hızlı")
    assessment.add_response("academic", "learning_depth", "Derin")
    assessment.add_response("skills", "problem_solving", "Yetkin")
    assessment.add_response("skills", "communication", "Etkili")
    assessment.add_response("social_emotional", "peer_relationships", "Güçlü")
    assessment.add_response("social_emotional", "emotional_maturity", "Yüksek")
    assessment.add_response("social_emotional", "collaboration_teamwork", "İyi")
    assessment.add_response("personal_development", "motivation_interest", "Yüksek")
    assessment.add_response("personal_development", "goal_setting", "İyi")
    assessment.add_response("interests", "student_interests", "Sanat ve El Becerileri")

    # Değerlendirmeyi işle
    results = process_assessment(assessment, student)

    # Rapor oluştur
    report = generate_report(student, assessment, results)

    # Kaydet (JSON olarak)
    json_path = save_report_to_file(report, "json")

    # Konsola yazdır
    print(f"\n✅ Rapor oluşturuldu ve kaydedildi: {json_path}\n")
    print("📋 Kısa Özet:")
    print(f"Öğrenci: {report.content['student_reference']}")
    print(f"Güçlü Yönler:\n - " + "\n - ".join(report.content["strengths"]))

    if report.content["growth_areas"]:
        print("Gelişim Alanları:\n - " + "\n - ".join(report.content["growth_areas"]))
    else:
        print("Gelişim Alanları: Henüz tespit edilemedi.")

if __name__ == "__main__":
    main()
