from database.database import engine, Session
from models.database_models import Base

def init_sample_testimonials(db: Session):
    """Initialize sample testimonials"""
    from models.testimonial import Testimonial
    
    sample_testimonials = [
        {
            "teacher_id": 1,
            "author_name": "Əli Məmmədov",
            "content": "Bu kurslar sayəsində data analitikası sahəsində professional səviyyəyə çatdım. Müəllimlərin peşəkarlığı və praktiki tapşırıqlar çox faydalı oldu.",
            "rating": 5
        },
        {
            "teacher_id": 1,
            "author_name": "Aynur Hüseynova",
            "content": "Python proqramlaşdırma dilini sıfırdan öyrəndim. Dərslər çox aydın və başa düşülən formada keçirilir.",
            "rating": 5
        },
        {
            "teacher_id": 2,
            "author_name": "Rəşad Əliyev",
            "content": "Data Science kursunu bitirdikdən sonra iş tapmaqda heç bir çətinlik çəkmədim. Təcrübəli müəllimlərdən öyrənmək böyük üstünlükdür.",
            "rating": 5
        },
        {
            "teacher_id": 2,
            "author_name": "Leyla Əhmədova",
            "content": "Machine Learning kursları real layihələr üzərində qurulub. İndi süni intellekt sahəsində özümü daha inamlı hiss edirəm.",
            "rating": 5
        },
        {
            "teacher_id": 1,
            "author_name": "Nicat Hüseynli",
            "content": "SQL və verilənlər bazası kursunu bitirdikdən sonra iş təklifləri almağa başladım. Praktiki tapşırıqlar real iş mühitinə hazırlaşmaqda çox kömək etdi.",
            "rating": 4
        },
        {
            "teacher_id": 2,
            "author_name": "Səbinə Məmmədli",
            "content": "Deep Learning və Computer Vision kursları çox əhatəlidir. Layihə portfolio yaratmaqda böyük köməyi oldu.",
            "rating": 5
        },
        {
            "teacher_id": 1,
            "author_name": "Tural Əlizadə",
            "content": "Big Data texnologiyaları kursunda öyrəndiklərim sayəsində şirkətimizdə yeni analitika sistemləri qurduq. Təşəkkür edirəm!",
            "rating": 5
        },
        {
            "teacher_id": 2,
            "author_name": "Günel Hüseynova",
            "content": "Web Development kursu tam başlanğıc səviyyəsindən professional səviyyəyə qədər olan yolu əhatə edir. Artıq freelancer kimi işləyirəm.",
            "rating": 5
        },
        {
            "teacher_id": 1,
            "author_name": "Kamran Əliyev",
            "content": "DevOps və Cloud Computing kursları praktiki yönümlüdür. AWS və Docker texnologiyalarını dərindən öyrəndim.",
            "rating": 4
        }
    ]
    
    for testimonial_data in sample_testimonials:
        testimonial = Testimonial(**testimonial_data)
        db.add(testimonial)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error adding sample testimonials: {e}")

def init_db(db: Session):
    """Initialize the database with sample data"""
    Base.metadata.create_all(bind=engine)
    init_sample_users(db)
    init_sample_courses(db)
    init_sample_testimonials(db)

if __name__ == "__main__":
    with Session(bind=engine) as db:
        init_db(db)
