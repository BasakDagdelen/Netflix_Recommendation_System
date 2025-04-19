"""
Veritabanı ve örnek veriler oluşturmak için script.
Bu script'i çalıştırmak için:
    python setup_db.py
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base, Movie, Category, User
import random


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:12345@localhost:5432/netflix_recommendation")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_sample_data():
    db = SessionLocal()
    try:
        categories = [
            "Aksiyon", "Macera", "Komedi", "Dram", "Bilim Kurgu", 
            "Korku", "Romantik", "Gizem", "Belgesel", "Animasyon"
        ]
        
        db_categories = []
        for cat_name in categories:
            category = Category(name=cat_name)
            db.add(category)
            db_categories.append(category)
        
        db.commit()
        
        movies = [
            {"title": "Yıldızlararası", "description": "Bir grup astronot, insanlığın yeni bir ev bulma umutlarıyla uzay ve zamanın ötesine yolculuk eder.", "release_year": 2014, "rating": 8.6},
            {"title": "Matrix", "description": "Bir bilgisayar korsanı, dünyanın aslında bir simülasyon olduğunu keşfeder.", "release_year": 1999, "rating": 8.7},
            {"title": "Forrest Gump", "description": "Forrest Gump'ın olağanüstü yaşam hikayesi.", "release_year": 1994, "rating": 8.8},
            {"title": "Yeşil Yol", "description": "Bir hapishanedeki doğaüstü olaylar ve etkileyici bir dostluk hikayesi.", "release_year": 1999, "rating": 8.6},
            {"title": "Esaretin Bedeli", "description": "Masum bir adamın hapishane yaşamı ve özgürlük umudu.", "release_year": 1994, "rating": 9.3},
            {"title": "Başlangıç", "description": "Bir hırsız, kurbanlarının rüyalarına girerek fikirlerini çalar.", "release_year": 2010, "rating": 8.8},
            {"title": "Dövüş Kulübü", "description": "Bir ofis çalışanı ve gizemli bir sabun satıcısı yeraltı dövüş kulübü kurar.", "release_year": 1999, "rating": 8.8},
            {"title": "Parazit", "description": "Fakir bir aile, zengin bir ailenin evine sızarak hayatlarını değiştirir.", "release_year": 2019, "rating": 8.5},
            {"title": "Joker", "description": "Başarısız bir komedyenin yavaş yavaş deliliğe sürüklenişi.", "release_year": 2019, "rating": 8.4},
            {"title": "Baba", "description": "Bir mafya ailesinin hikayesi.", "release_year": 1972, "rating": 9.2},
            {"title": "Kara Şövalye", "description": "Batman, Joker'e karşı mücadele eder.", "release_year": 2008, "rating": 9.0},
            {"title": "12 Öfkeli Adam", "description": "Bir jüri üyesi, diğerlerini masum olduğuna ikna etmeye çalışır.", "release_year": 1957, "rating": 9.0},
            {"title": "Schindler'in Listesi", "description": "Bir Alman işadamı, Holokost sırasında Yahudileri kurtarır.", "release_year": 1993, "rating": 8.9},
            {"title": "Pulp Fiction", "description": "Suçlular, boksörler ve gangsterlerin kesişen hikayeleri.", "release_year": 1994, "rating": 8.9},
            {"title": "Yüzüklerin Efendisi", "description": "Bir grup kahraman, kötülüğe karşı savaşır.", "release_year": 2001, "rating": 8.8},
            {"title": "İyi, Kötü ve Çirkin", "description": "Üç silahşör, gömülü bir hazineyi bulmak için yarışır.", "release_year": 1966, "rating": 8.8},
            {"title": "Sıkı Dostlar", "description": "Bir gencin mafya dünyasına girişi.", "release_year": 1990, "rating": 8.7},
            {"title": "Yedi", "description": "İki dedektif, yedi ölümcül günaha dayalı bir seri katili takip eder.", "release_year": 1995, "rating": 8.6},
            {"title": "Sessizliğin Sesi", "description": "Bir işitme engelli kız, zorbalıkla mücadele eder.", "release_year": 2016, "rating": 7.9},
            {"title": "Ayla", "description": "Kore Savaşı'nda Türk askerinin bulduğu küçük kız çocuğuyla kurduğu bağ.", "release_year": 2017, "rating": 8.2}
        ]
        
        for movie_data in movies:
            selected_categories = random.sample(db_categories, random.randint(1, 3))
            
            movie = Movie(
                title=movie_data["title"],
                description=movie_data["description"],
                release_year=movie_data["release_year"],
                rating=movie_data["rating"]
            )
            
            for category in selected_categories:
                movie.categories.append(category)
            
            db.add(movie)
        
        db.commit()
        
        users = [
            {"username": "user1", "email": "user1@example.com"},
            {"username": "user2", "email": "user2@example.com"},
            {"username": "user3", "email": "user3@example.com"},
            {"username": "user4", "email": "user4@example.com"},
            {"username": "user5", "email": "user5@example.com"}
        ]
        
        for user_data in users:
            user = User(
                username=user_data["username"],
                email=user_data["email"]
            )
            db.add(user)
        
        db.commit()
        
        print("Örnek veriler başarıyla oluşturuldu!")
        
    except Exception as e:
        print(f"Hata: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Veritabanı tablolarını oluşturma...")
    Base.metadata.create_all(bind=engine)
    print("Tablolar oluşturuldu!")
    
    print("Örnek veriler oluşturuluyor...")
    create_sample_data()