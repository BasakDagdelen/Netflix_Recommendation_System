"""
import os
import sys
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import models
from models import Movie, User, UserRating, Category, get_db
from recommender import MovieRecommender

app = FastAPI(
    title="Netflix Recommendation System",
    description="An API that provides movie recommendations based on user preferences.",
    version="1.0.0"
)

# Pydantic modelleri
class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_year: Optional[int] = None
    rating: Optional[float] = None
    category_ids: Optional[List[int]] = []

class MovieResponse(MovieBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    categories: List[str]

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    user_id: int
    movie_id: int
    rating: float

class RatingResponse(RatingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Öneri sistemi örneği
recommender = MovieRecommender()

@app.on_event("startup")
async def startup_event():
    models.init_db()
    db = next(get_db())
    try:
        recommender.prepare_features(db)
    except ValueError as e:
        print(f"Uyarı: {e}")

@app.get("/")
def read_root():
    return {"message": "Netflix Recommendation System API"}

@app.post("/movies/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(movie: MovieBase, db: Session = Depends(get_db)):
    # Kategorilerin var olup olmadığını kontrol et
    if movie.category_ids:
        for category_id in movie.category_ids:
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ID {category_id} olan kategori bulunamadı"
                )
    
    db_movie = Movie(
        title=movie.title,
        description=movie.description,
        release_year=movie.release_year,
        rating=movie.rating
    )
    
    # Kategorileri ekle
    if movie.category_ids:
        for category_id in movie.category_ids:
            category = db.query(Category).filter(Category.id == category_id).first()
            db_movie.categories.append(category)
    
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.get("/movies/", response_model=List[MovieResponse])
def list_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movies = db.query(Movie).offset(skip).limit(limit).all()
    return movies

@app.get("/movies/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Film bulunamadı")
    return movie

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserBase, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı adı veya email zaten kullanımda"
        )
    
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return user

@app.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryBase, db: Session = Depends(get_db)):
    existing_category = db.query(Category).filter(Category.name == category.name).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kategori zaten mevcut"
        )
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[CategoryResponse])
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

@app.post("/ratings/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def create_rating(rating: RatingBase, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == rating.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {rating.user_id} olan kullanıcı bulunamadı"
        )
    
    movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {rating.movie_id} olan film bulunamadı"
        )
    
    if not 0 <= rating.rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Puan 0 ile 5 arasında olmalıdır"
        )
    
    # Var olan rating'i güncelle veya yeni oluştur
    existing_rating = db.query(UserRating).filter(
        UserRating.user_id == rating.user_id,
        UserRating.movie_id == rating.movie_id
    ).first()
    
    if existing_rating:
        existing_rating.rating = rating.rating
    else:
        existing_rating = UserRating(
            user_id=rating.user_id,
            movie_id=rating.movie_id,
            rating=rating.rating
        )
        db.add(existing_rating)
    
    db.commit()
    db.refresh(existing_rating)
    return existing_rating

@app.get("/ratings/", response_model=List[RatingResponse])
def list_ratings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ratings = db.query(UserRating).offset(skip).limit(limit).all()
    return ratings

@app.get("/recommendations/{user_id}")
def get_recommendations(
    user_id: int,
    n_recommendations: int = 5,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {user_id} olan kullanıcı bulunamadı"
        )
    
    recommendations = recommender.recommend_movies(db, user_id, n_recommendations)
    
    return {
        "user_id": user_id,
        "recommendations": recommendations
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)"""
    
    
import os
import sys
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

# Proje dizinini Python path'ine ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Yerel modülleri import et
from models import Movie, User, UserRating, Category
from database import get_db, engine, Base
from schemas import (
    MovieCreate, MovieResponse, UserCreate, UserResponse,
    CategoryCreate, CategoryResponse, RatingCreate, RatingResponse,
    RecommendationResponse
)
from recommender import MovieRecommender

# FastAPI uygulaması oluştur
app = FastAPI(
    title="Netflix Recommendation System",
    description="An API that provides movie recommendations based on user preferences.",
    version="1.0.0"
)

# Öneri sistemi örneği
recommender = MovieRecommender()

@app.on_event("startup")
async def startup_event():
    # Veritabanı tablolarını oluştur
    Base.metadata.create_all(bind=engine)
    
    # Öneri modeli için özellikleri hazırla
    db = next(get_db())
    try:
        recommender.prepare_features(db)
    except ValueError as e:
        print(f"Uyarı: {e}")

# Film işlemleri
@app.post("/movies/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    # Kategorilerin var olup olmadığını kontrol et
    for category_id in movie.category_ids:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {category_id} olan kategori bulunamadı"
            )
    
    # Yeni film oluştur
    db_movie = Movie(
        title=movie.title,
        description=movie.description,
        release_year=movie.release_year,
        rating=movie.rating
    )
    
    # Kategorileri ekle
    for category_id in movie.category_ids:
        category = db.query(Category).filter(Category.id == category_id).first()
        db_movie.categories.append(category)
    
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.get("/movies/", response_model=List[MovieResponse])
def get_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movies = db.query(Movie).offset(skip).limit(limit).all()
    return movies

@app.get("/movies/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film bulunamadı"
        )
    return movie

# Kullanıcı işlemleri
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Kullanıcı adı veya email'in benzersiz olduğunu kontrol et
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı adı veya email zaten kullanımda"
        )
    
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    return user

# Kategori işlemleri
@app.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    existing_category = db.query(Category).filter(Category.name == category.name).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kategori zaten mevcut"
        )
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[CategoryResponse])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

# Puanlama işlemleri
@app.post("/ratings/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def create_rating(rating: RatingCreate, db: Session = Depends(get_db)):
    # Kullanıcı ve filmin var olup olmadığını kontrol et
    user = db.query(User).filter(User.id == rating.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {rating.user_id} olan kullanıcı bulunamadı"
        )
    
    movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {rating.movie_id} olan film bulunamadı"
        )
    
    # Puanın 0-5 arasında olduğunu kontrol et
    if not 0 <= rating.rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Puan 0 ile 5 arasında olmalıdır"
        )
    
    # Daha önce puanlama yapılmış mı kontrol et
    existing_rating = db.query(UserRating).filter(
        UserRating.user_id == rating.user_id,
        UserRating.movie_id == rating.movie_id
    ).first()
    
    if existing_rating:
        # Varolan puanı güncelle
        existing_rating.rating = rating.rating
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    else:
        # Yeni puanlama oluştur
        db_rating = UserRating(
            user_id=rating.user_id,
            movie_id=rating.movie_id,
            rating=rating.rating
        )
        db.add(db_rating)
        db.commit()
        db.refresh(db_rating)
        return db_rating

@app.get("/ratings/user/{user_id}", response_model=List[RatingResponse])
def get_user_ratings(user_id: int, db: Session = Depends(get_db)):
    # Kullanıcının var olup olmadığını kontrol et
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {user_id} olan kullanıcı bulunamadı"
        )
    
    ratings = db.query(UserRating).filter(UserRating.user_id == user_id).all()
    return ratings

# Film önerileri
@app.get("/recommendations/{user_id}", response_model=RecommendationResponse)
def get_recommendations(
    user_id: int,
    n_recommendations: int = 5,
    db: Session = Depends(get_db)
):
    # Kullanıcının var olup olmadığını kontrol et
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {user_id} olan kullanıcı bulunamadı"
        )
    
    # Önerileri al
    recommendations = recommender.recommend_movies(db, user_id, n_recommendations)
    
    return {
        "user_id": user_id,
        "recommendations": recommendations
    }

# Uygulama başlat
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)