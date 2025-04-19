import os
import sys
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session
from typing import List, Dict, Any

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from models import Movie, UserRating, Category

class MovieRecommender:
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
        self.movie_features = None
        self.movie_clusters = None
        self.movie_cluster_map = None
        
        
    def prepare_features(self, db: Session):
        movies = db.query(Movie).all()
        
        if not movies:
            raise ValueError("Veritabanında film bulunamadı!")
        
        categories = db.query(Category).order_by(Category.id).all()
        category_map = {category.id: idx for idx, category in enumerate(categories)}
        
        features = []
        movie_ids = []
        
        for movie in movies:
            category_vector = np.zeros(len(categories))
            for category in movie.categories:
                if category.id in category_map:
                    category_vector[category_map[category.id]] = 1
                
            feature_vector = np.concatenate([
                [movie.rating if movie.rating else 0],
                [movie.release_year if movie.release_year else 0],
                category_vector
            ])
            
            features.append(feature_vector)
            movie_ids.append(movie.id)
        
        if not features:
            raise ValueError("Film özellikleri oluşturulamadı!")
            
        self.movie_features = self.scaler.fit_transform(features)
        
        self.movie_clusters = self.kmeans.fit_predict(self.movie_features)
        
        self.movie_cluster_map = dict(zip(movie_ids, self.movie_clusters))
       
        
    def get_user_cluster(self, db: Session, user_id: int) -> int:
        user_ratings = db.query(UserRating).filter(UserRating.user_id == user_id).all()
        
        if not user_ratings:
            return -1  
            
        high_rated_clusters = []
        for rating in user_ratings:
            if rating.rating >= 4.0:  
                cluster = self.movie_cluster_map.get(rating.movie_id)
                if cluster is not None:
                    high_rated_clusters.append(cluster)
        
        if not high_rated_clusters:
            return -1  
            
        
        from collections import Counter
        cluster_counts = Counter(high_rated_clusters)
        preferred_cluster = cluster_counts.most_common(1)[0][0]
        
        return preferred_cluster
        
        
    def recommend_movies(self, db: Session, user_id: int, n_recommendations: int = 5) -> List[Dict[str, Any]]:
        if self.movie_cluster_map is None:
            try:
                self.prepare_features(db)
            except ValueError as e:
                movies = db.query(Movie).order_by(Movie.rating.desc()).limit(n_recommendations).all()
                return [{"movie_id": movie.id, "title": movie.title, "rating": movie.rating or 0} for movie in movies]

        preferred_cluster = self.get_user_cluster(db, user_id)

        if preferred_cluster == -1:
            movies = db.query(Movie).order_by(Movie.rating.desc()).limit(n_recommendations).all()
        else:
            cluster_movie_ids = [movie_id for movie_id, cluster in self.movie_cluster_map.items()
                                 if cluster == preferred_cluster]
            
            rated_movie_ids = db.query(UserRating.movie_id).filter(UserRating.user_id == user_id).all()
            rated_movie_ids = [movie_id for (movie_id,) in rated_movie_ids]
            
            new_movie_ids = [movie_id for movie_id in cluster_movie_ids if movie_id not in rated_movie_ids]
            
            if new_movie_ids:
                movies = db.query(Movie).filter(Movie.id.in_(new_movie_ids))\
                    .order_by(Movie.rating.desc()).limit(n_recommendations).all()
            else:
                movies = db.query(Movie).order_by(Movie.rating.desc()).limit(n_recommendations).all()

        return [{"movie_id": movie.id, "title": movie.title, "rating": movie.rating or 0} for movie in movies]