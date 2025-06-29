from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import random

import models, schemas, auth
from database import SessionLocal, engine

# Buat tabel database saat aplikasi dimulai
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency untuk mendapatkan sesi database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Tanam Rawat API"}

@app.post("/identify")
async def identify_plant(file: UploadFile = File(...), current_user: schemas.User = Depends(auth.get_current_user)):
    """
    Endpoint untuk identifikasi tanaman berdasarkan gambar yang diunggah.
    
    CATATAN IMPLEMENTASI SAAT INI:
    - Ini adalah implementasi simulasi/dummy untuk fase MVP
    - Endpoint menerima file gambar dan mengembalikan hasil identifikasi acak
    - File temporary dibersihkan setelah diproses untuk mencegah penumpukan data
    - Pada implementasi final, akan diganti dengan model AI yang sesungguhnya
    
    Args:
        file (UploadFile): File gambar tanaman yang akan diidentifikasi
        current_user: User yang sedang login (untuk autentikasi)
        
    Returns:
        dict: Hasil identifikasi dengan nama tanaman, confidence score, dan tips perawatan
        
    Raises:
        HTTPException: Jika file yang diunggah bukan gambar atau terlalu besar
    """
    import tempfile
    import os
    
    # Validasi tipe file untuk memastikan hanya gambar yang diterima
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File harus berupa gambar")
    
    # Validasi ukuran file (maksimal 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(status_code=400, detail="Ukuran file terlalu besar (maksimal 10MB)")
    
    # Reset file pointer untuk pembacaan ulang jika diperlukan
    await file.seek(0)
    
    temp_file_path = None
    try:
        # Simpan file temporary untuk processing
        # Menggunakan tempfile untuk keamanan dan pembersihan otomatis
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(file_content)
        
        # Daftar nama tanaman untuk simulasi - akan diganti dengan database tanaman nyata
        # Dipilih tanaman hias populer yang mudah dikenali untuk testing UI
        plant_names = [
            "Monstera Deliciosa",
            "Sansevieria Trifasciata", 
            "Pothos Aureus",
            "Ficus Lyrata",
            "Aloe Vera",
            "Philodendron Hederaceum",
            "Dracaena Marginata",
            "Zamioculcas Zamiifolia"
        ]
        
        # SIMULASI: Pilih tanaman acak dan generate confidence score realistis
        # Pada implementasi nyata, di sini akan ada:
        # 1. Preprocessing gambar (resize, normalize)
        # 2. Inference dengan model AI
        # 3. Post-processing hasil prediksi
        identified_plant = random.choice(plant_names)
        
        # Generate confidence score antara 75-95% untuk simulasi yang realistis
        # Score di bawah 75% biasanya dianggap tidak reliable untuk identifikasi tanaman
        confidence = round(random.uniform(0.75, 0.95), 2)
        
        # Return format yang konsisten dengan schema frontend
        # Format ini dirancang untuk mudah diperluas dengan informasi tambahan
        return {
            "plant_name": identified_plant,
            "confidence": confidence,
            "description": f"Tanaman ini teridentifikasi sebagai {identified_plant} dengan tingkat kepercayaan {confidence*100}%",
            "care_tips": [
                "Letakkan di tempat dengan cahaya tidak langsung",
                "Siram ketika tanah terasa kering", 
                "Berikan pupuk setiap 2-4 minggu sekali"
            ]
        }
    
    finally:
        # Pembersihan file temporary untuk mencegah penumpukan data
        # Penting untuk keamanan dan efisiensi storage
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass  # File mungkin sudah terhapus, tidak masalah

# User Registration and Authentication

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.get_user(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

# CRUD Endpoints for Plants

@app.post("/plants/", response_model=schemas.Plant)
def create_plant(plant: schemas.PlantCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_plant = models.Plant(**plant.dict())
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant

@app.get("/plants/", response_model=List[schemas.Plant])
def read_plants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    plants = db.query(models.Plant).offset(skip).limit(limit).all()
    return plants

@app.get("/plants/{plant_id}", response_model=schemas.Plant)
def read_plant(plant_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    plant = db.query(models.Plant).filter(models.Plant.id == plant_id).first()
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant

@app.put("/plants/{plant_id}", response_model=schemas.Plant)
def update_plant(plant_id: int, plant: schemas.PlantCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_plant = db.query(models.Plant).filter(models.Plant.id == plant_id).first()
    if db_plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    for key, value in plant.dict().items():
        setattr(db_plant, key, value)
    db.commit()
    db.refresh(db_plant)
    return db_plant

@app.delete("/plants/{plant_id}")
def delete_plant(plant_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_plant = db.query(models.Plant).filter(models.Plant.id == plant_id).first()
    if db_plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    db.delete(db_plant)
    db.commit()
    return {"message": "Plant deleted successfully"}

# CRUD Endpoints for Schedules

@app.post("/schedules/", response_model=schemas.Schedule)
def create_schedule(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_schedule = models.Schedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@app.get("/schedules/", response_model=List[schemas.Schedule])
def read_schedules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    schedules = db.query(models.Schedule).offset(skip).limit(limit).all()
    return schedules

@app.get("/schedules/{schedule_id}", response_model=schemas.Schedule)
def read_schedule(schedule_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@app.put("/schedules/{schedule_id}", response_model=schemas.Schedule)
def update_schedule(schedule_id: int, schedule: schemas.ScheduleCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    for key, value in schedule.dict().items():
        setattr(db_schedule, key, value)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@app.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.delete(db_schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}

# CRUD Endpoints for PestDiseases

@app.post("/pest_diseases/", response_model=schemas.PestDisease)
def create_pest_disease(pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = models.PestDisease(**pest_disease.dict())
    db.add(db_pest_disease)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.get("/pest_diseases/", response_model=List[schemas.PestDisease])
def read_pest_diseases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_diseases = db.query(models.PestDisease).offset(skip).limit(limit).all()
    return pest_diseases

@app.get("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def read_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    return pest_disease

@app.put("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def update_pest_disease(pest_disease_id: int, pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    for key, value in pest_disease.dict().items():
        setattr(db_pest_disease, key, value)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.delete("/pest_diseases/{pest_disease_id}")
def delete_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    db.delete(db_pest_disease)
    db.commit()
    return {"message": "PestDisease deleted successfully"}

# CRUD Endpoints for Posts

@app.post("/posts/", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = models.Post(**post.dict(), owner_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return posts

@app.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    for key, value in post.dict().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

# CRUD Endpoints for Comments

@app.post("/comments/", response_model=schemas.Comment)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = models.Comment(**comment.dict(), owner_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/comments/", response_model=List[schemas.Comment])
def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).offset(skip).limit(limit).all()
    return comments

@app.get("/comments/{comment_id}", response_model=schemas.Comment)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@app.put("/comments/{comment_id}", response_model=schemas.Comment)
def update_comment(comment_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    for key, value in comment.dict().items():
        setattr(db_comment, key, value)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

# CRUD Endpoints for PestDiseases

@app.post("/pest_diseases/", response_model=schemas.PestDisease)
def create_pest_disease(pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = models.PestDisease(**pest_disease.dict())
    db.add(db_pest_disease)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.get("/pest_diseases/", response_model=List[schemas.PestDisease])
def read_pest_diseases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_diseases = db.query(models.PestDisease).offset(skip).limit(limit).all()
    return pest_diseases

@app.get("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def read_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    return pest_disease

@app.put("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def update_pest_disease(pest_disease_id: int, pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    for key, value in pest_disease.dict().items():
        setattr(db_pest_disease, key, value)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.delete("/pest_diseases/{pest_disease_id}")
def delete_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    db.delete(db_pest_disease)
    db.commit()
    return {"message": "PestDisease deleted successfully"}

# CRUD Endpoints for Posts

@app.post("/posts/", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = models.Post(**post.dict(), owner_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return posts

@app.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    for key, value in post.dict().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

# CRUD Endpoints for Comments

@app.post("/comments/", response_model=schemas.Comment)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = models.Comment(**comment.dict(), owner_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/comments/", response_model=List[schemas.Comment])
def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).offset(skip).limit(limit).all()
    return comments

@app.get("/comments/{comment_id}", response_model=schemas.Comment)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@app.put("/comments/{comment_id}", response_model=schemas.Comment)
def update_comment(comment_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    for key, value in comment.dict().items():
        setattr(db_comment, key, value)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

# CRUD Endpoints for PestDiseases

@app.post("/pest_diseases/", response_model=schemas.PestDisease)
def create_pest_disease(pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = models.PestDisease(**pest_disease.dict())
    db.add(db_pest_disease)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.get("/pest_diseases/", response_model=List[schemas.PestDisease])
def read_pest_diseases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_diseases = db.query(models.PestDisease).offset(skip).limit(limit).all()
    return pest_diseases

@app.get("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def read_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    return pest_disease

@app.put("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def update_pest_disease(pest_disease_id: int, pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    for key, value in pest_disease.dict().items():
        setattr(db_pest_disease, key, value)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.delete("/pest_diseases/{pest_disease_id}")
def delete_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    db.delete(db_pest_disease)
    db.commit()
    return {"message": "PestDisease deleted successfully"}

# CRUD Endpoints for Posts

@app.post("/posts/", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = models.Post(**post.dict(), owner_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return posts

@app.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    for key, value in post.dict().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

# CRUD Endpoints for Comments

@app.post("/comments/", response_model=schemas.Comment)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = models.Comment(**comment.dict(), owner_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/comments/", response_model=List[schemas.Comment])
def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).offset(skip).limit(limit).all()
    return comments

@app.get("/comments/{comment_id}", response_model=schemas.Comment)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@app.put("/comments/{comment_id}", response_model=schemas.Comment)
def update_comment(comment_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    for key, value in comment.dict().items():
        setattr(db_comment, key, value)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

# CRUD Endpoints for PestDiseases

@app.post("/pest_diseases/", response_model=schemas.PestDisease)
def create_pest_disease(pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = models.PestDisease(**pest_disease.dict())
    db.add(db_pest_disease)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.get("/pest_diseases/", response_model=List[schemas.PestDisease])
def read_pest_diseases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_diseases = db.query(models.PestDisease).offset(skip).limit(limit).all()
    return pest_diseases

@app.get("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def read_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    return pest_disease

@app.put("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def update_pest_disease(pest_disease_id: int, pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    for key, value in pest_disease.dict().items():
        setattr(db_pest_disease, key, value)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.delete("/pest_diseases/{pest_disease_id}")
def delete_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    db.delete(db_pest_disease)
    db.commit()
    return {"message": "PestDisease deleted successfully"}

# CRUD Endpoints for Posts

@app.post("/posts/", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = models.Post(**post.dict(), owner_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return posts

@app.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    for key, value in post.dict().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

# CRUD Endpoints for Comments

@app.post("/comments/", response_model=schemas.Comment)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = models.Comment(**comment.dict(), owner_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/comments/", response_model=List[schemas.Comment])
def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).offset(skip).limit(limit).all()
    return comments

@app.get("/comments/{comment_id}", response_model=schemas.Comment)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@app.put("/comments/{comment_id}", response_model=schemas.Comment)
def update_comment(comment_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    for key, value in comment.dict().items():
        setattr(db_comment, key, value)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

# CRUD Endpoints for PestDiseases

@app.post("/pest_diseases/", response_model=schemas.PestDisease)
def create_pest_disease(pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = models.PestDisease(**pest_disease.dict())
    db.add(db_pest_disease)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.get("/pest_diseases/", response_model=List[schemas.PestDisease])
def read_pest_diseases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_diseases = db.query(models.PestDisease).offset(skip).limit(limit).all()
    return pest_diseases

@app.get("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def read_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    return pest_disease

@app.put("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def update_pest_disease(pest_disease_id: int, pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    for key, value in pest_disease.dict().items():
        setattr(db_pest_disease, key, value)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.delete("/pest_diseases/{pest_disease_id}")
def delete_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    db.delete(db_pest_disease)
    db.commit()
    return {"message": "PestDisease deleted successfully"}

# CRUD Endpoints for Posts

@app.post("/posts/", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = models.Post(**post.dict(), owner_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return posts

@app.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    for key, value in post.dict().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

# CRUD Endpoints for Comments

@app.post("/comments/", response_model=schemas.Comment)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = models.Comment(**comment.dict(), owner_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/comments/", response_model=List[schemas.Comment])
def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).offset(skip).limit(limit).all()
    return comments

@app.get("/comments/{comment_id}", response_model=schemas.Comment)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@app.put("/comments/{comment_id}", response_model=schemas.Comment)
def update_comment(comment_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    for key, value in comment.dict().items():
        setattr(db_comment, key, value)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

# CRUD Endpoints for PestDiseases

@app.post("/pest_diseases/", response_model=schemas.PestDisease)
def create_pest_disease(pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = models.PestDisease(**pest_disease.dict())
    db.add(db_pest_disease)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.get("/pest_diseases/", response_model=List[schemas.PestDisease])
def read_pest_diseases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_diseases = db.query(models.PestDisease).offset(skip).limit(limit).all()
    return pest_diseases

@app.get("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def read_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    return pest_disease

@app.put("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def update_pest_disease(pest_disease_id: int, pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    for key, value in pest_disease.dict().items():
        setattr(db_pest_disease, key, value)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.delete("/pest_diseases/{pest_disease_id}")
def delete_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    db.delete(db_pest_disease)
    db.commit()
    return {"message": "PestDisease deleted successfully"}

# CRUD Endpoints for Posts

@app.post("/posts/", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = models.Post(**post.dict(), owner_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return posts

@app.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    for key, value in post.dict().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

# CRUD Endpoints for Comments

@app.post("/comments/", response_model=schemas.Comment)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = models.Comment(**comment.dict(), owner_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/comments/", response_model=List[schemas.Comment])
def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).offset(skip).limit(limit).all()
    return comments

@app.get("/comments/{comment_id}", response_model=schemas.Comment)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@app.put("/comments/{comment_id}", response_model=schemas.Comment)
def update_comment(comment_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    for key, value in comment.dict().items():
        setattr(db_comment, key, value)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

# CRUD Endpoints for PestDiseases

@app.post("/pest_diseases/", response_model=schemas.PestDisease)
def create_pest_disease(pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = models.PestDisease(**pest_disease.dict())
    db.add(db_pest_disease)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.get("/pest_diseases/", response_model=List[schemas.PestDisease])
def read_pest_diseases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_diseases = db.query(models.PestDisease).offset(skip).limit(limit).all()
    return pest_diseases

@app.get("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def read_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    return pest_disease

@app.put("/pest_diseases/{pest_disease_id}", response_model=schemas.PestDisease)
def update_pest_disease(pest_disease_id: int, pest_disease: schemas.PestDiseaseCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    for key, value in pest_disease.dict().items():
        setattr(db_pest_disease, key, value)
    db.commit()
    db.refresh(db_pest_disease)
    return db_pest_disease

@app.delete("/pest_diseases/{pest_disease_id}")
def delete_pest_disease(pest_disease_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_pest_disease = db.query(models.PestDisease).filter(models.PestDisease.id == pest_disease_id).first()
    if db_pest_disease is None:
        raise HTTPException(status_code=404, detail="PestDisease not found")
    db.delete(db_pest_disease)
    db.commit()
    return {"message": "PestDisease deleted successfully"}

# CRUD Endpoints for Posts

@app.post("/posts/", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = models.Post(**post.dict(), owner_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return posts

@app.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    for key, value in post.dict().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

# CRUD Endpoints for Comments

@app.post("/comments/", response_model=schemas.Comment)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_comment = models.Comment(**comment.dict(), owner_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/comments/", response_model=List[schemas.Comment])
def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).offset(skip).limit(limit).all()
    return comments

@app.get("/comments/{comment_id}", response_model=schemas.Comment)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@app.put("/comments/{comment_id}", response_model=schemas.
