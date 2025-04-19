from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Movie schemas
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Movie schemas
class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_year: Optional[int] = None
    rating: Optional[float] = Field(None, ge=0, le=10)

class MovieCreate(MovieBase):
    category_ids: List[int] = []

class MovieResponse(MovieBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    categories: List[CategoryResponse] = []

    class Config:
        from_attributes = True

# Rating schemas
class RatingBase(BaseModel):
    user_id: int
    movie_id: int
    rating: float = Field(..., ge=0, le=5)

class RatingCreate(RatingBase):
    pass

class RatingResponse(RatingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Recommendation schemas
class MovieRecommendation(BaseModel):
    movie_id: int
    title: str
    rating: float
    
class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[MovieRecommendation]