import requests
import random
import json

BASE_URL = "http://localhost:8000"

def test_create_user():
    user_id = random.randint(1000, 9999)
    user_data = {
        "username": f"test_user_{user_id}",
        "email": f"test{user_id}@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print(f"Kullanıcı oluşturma: {response.status_code}")
    
    if response.status_code == 201:
        print(f"Kullanıcı oluşturuldu: {response.json()}")
        return response.json()["id"]
    else:
        print(f"Hata: {response.text}")
        return None

def test_create_category():
    cat_id = random.randint(1000, 9999)
    category_data = {
        "name": f"Test Kategori {cat_id}"
    }
    
    response = requests.post(f"{BASE_URL}/categories/", json=category_data)
    print(f"Kategori oluşturma: {response.status_code}")
    
    if response.status_code == 201:
        print(f"Kategori oluşturuldu: {response.json()}")
        return response.json()["id"]
    else:
        print(f"Hata: {response.text}")
        return None

def test_create_movie(category_ids):
    movie_id = random.randint(1000, 9999)
    movie_data = {
        "title": f"Test Film {movie_id}",
        "description": f"Bu bir test filmidir #{movie_id}",
        "release_year": 2023,
        "rating": random.uniform(3.0, 9.0),
        "category_ids": category_ids
    }
    
    response = requests.post(f"{BASE_URL}/movies/", json=movie_data)
    print(f"Film oluşturma: {response.status_code}")
    
    if response.status_code == 201:
        print(f"Film oluşturuldu: {response.json()}")
        return response.json()["id"]
    else:
        print(f"Hata: {response.text}")
        return None

def test_create_rating(user_id, movie_id):
    rating_data = {
        "user_id": user_id,
        "movie_id": movie_id,
        "rating": random.uniform(0.0, 5.0)
    }
    
    response = requests.post(f"{BASE_URL}/ratings/", json=rating_data)
    print(f"Puanlama oluşturma: {response.status_code}")
    
    if response.status_code == 201:
        print(f"Puanlama oluşturuldu: {response.json()}")
        return True
    else:
        print(f"Hata: {response.text}")
        return False

def test_get_recommendations(user_id):
    response = requests.get(f"{BASE_URL}/recommendations/{user_id}")
    print(f"Öneriler alınıyor: {response.status_code}")
    
    if response.status_code == 200:
        recommendations = response.json()
        print(f"Öneriler: {json.dumps(recommendations, indent=2)}")
        return recommendations
    else:
        print(f"Hata: {response.text}")
        return None

def run_tests():
    print("====== Netflix Öneri Sistemi Test Senaryoları ======")
    
    # 1. Kategori oluştur
    category_ids = []
    for _ in range(2):
        category_id = test_create_category()
        if category_id:
            category_ids.append(category_id)
    
    if not category_ids:
        print("Kategori oluşturulamadı, test durduruluyor.")
        return
    
    # 2. Film oluştur
    movie_ids = []
    for _ in range(3):
        movie_id = test_create_movie(category_ids)
        if movie_id:
            movie_ids.append(movie_id)
    
    if not movie_ids:
        print("Film oluşturulamadı, test durduruluyor.")
        return
    
    # 3. Kullanıcı oluştur
    user_id = test_create_user()
    if not user_id:
        print("Kullanıcı oluşturulamadı, test durduruluyor.")
        return
    
    # 4. Puanlama yap
    for movie_id in movie_ids:
        test_create_rating(user_id, movie_id)
    
    # 5. Önerileri al
    test_get_recommendations(user_id)
    
    print("====== Testler tamamlandı ======")

if __name__ == "__main__":
    run_tests()