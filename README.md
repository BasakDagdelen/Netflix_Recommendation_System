# Netflix Style Recommendation System

Bu proje, Netflix tarzı bir film öneri sistemi oluşturmak için FastAPI, PostgreSQL, SQLAlchemy ve K-means kümeleme kullanır.

## Özellikler

- Kullanıcı yönetim sistemi
- Film ve kategori yönetimi
- Kullanıcı derecelendirme sistemi
- K-means kümeleme kullanarak kişiselleştirilmiş film önerileri
- RESTful API

## Gereksinimler

- Python 3.8+
- PostgreSQL
- pip

## Kurulum

1. Projeyi klonlayın
2. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

3. PostgreSQL'de bir veritabanı oluşturun

4. `.env.example` dosyasını `.env` olarak kopyalayın ve veritabanı bağlantı bilgilerinizi güncelleyin:

```
DATABASE_URL=postgresql://kullanici:sifre@localhost:5432/veritabani_adi
```

5. Veritabanı şemasını ve örnek verileri oluşturun:

```bash
python setup_db.py
```

## Kullanım

API'yi çalıştırmak için:

```bash
uvicorn main:app --reload
```

API belgelerine erişmek için:

```
http://localhost:8000/docs
```

## API Uç Noktaları

### Film İşlemleri

- `GET /movies/`: Tüm filmleri listeler
- `GET /movies/{movie_id}`: Belirli bir filmin detaylarını gösterir
- `POST /movies/`: Yeni bir film ekler

### Kategori İşlemleri

- `GET /categories/`: Tüm kategorileri listeler
- `POST /categories/`: Yeni bir kategori ekler

### Kullanıcı İşlemleri

- `GET /users/`: Tüm kullanıcıları listeler
- `GET /users/{user_id}`: Belirli bir kullanıcının detaylarını gösterir
- `POST /users/`: Yeni bir kullanıcı ekler

### Derecelendirme İşlemleri

- `POST /ratings/`: Yeni bir derecelendirme ekler veya var olanı günceller
- `GET /ratings/user/{user_id}`: Bir kullanıcının tüm derecelendirmelerini listeler

### Öneri İşlemleri

- `GET /recommendations/{user_id}`: Belirli bir kullanıcı için film önerileri alır

## Sistem Tasarımı

Bu sistem, kullanıcı tercihlerine dayalı olarak filmleri önermek için makine öğrenimi kullanır:

1. Filmler, kategorileri ve puanlarına göre K-means kümeleme ile gruplara ayrılır
2. Kullanıcının yüksek puan verdiği filmlerin ait olduğu kümeler belirlenir
3. Kullanıcıya, tercih ettiği kümelerdeki henüz izlemediği filmler önerilir
4. Kullanıcı hiç film puanlamadıysa, en popüler filmler önerilir

