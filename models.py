from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Film-Kategori ilişki tablosu
movie_category = Table('movie_category', Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

# Film izleme geçmişi tablosu
user_movie_watches = Table('user_movie_watches', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('movie_id', Integer, ForeignKey('movies.id')),
    Column('watched_at', DateTime, default=datetime.utcnow)
)

class Movie(Base):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    release_year = Column(Integer)
    rating = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    categories = relationship("Category", secondary=movie_category, back_populates="movies")
    user_ratings = relationship("UserRating", back_populates="movie")
    watched_by = relationship("User", secondary=user_movie_watches, back_populates="watched_movies")

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    movies = relationship("Movie", secondary=movie_category, back_populates="categories")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    watched_movies = relationship("Movie", secondary=user_movie_watches, back_populates="watched_by")
    ratings = relationship("UserRating", back_populates="user")

class UserRating(Base):
    __tablename__ = 'user_ratings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    rating = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="user_ratings")