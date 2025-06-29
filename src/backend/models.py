from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# Model untuk tabel users - menyimpan data pengguna aplikasi
class User(Base):
    """
    Model pengguna aplikasi dengan sistem otentikasi berbasis email.
    
    Relasi:
    - One-to-Many dengan Post (pengguna bisa membuat banyak postingan)
    - One-to-Many dengan Comment (pengguna bisa membuat banyak komentar)
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # Email sebagai username unik
    hashed_password = Column(String)  # Password di-hash dengan bcrypt untuk keamanan
    is_active = Column(Boolean, default=True)  # Flag untuk soft delete/deaktivasi akun

    # Relasi ke tabel lain - memungkinkan akses mudah ke data terkait
    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="owner")

# Model untuk master data tanaman - ensiklopedia tanaman dalam aplikasi
class Plant(Base):
    """
    Master data tanaman dengan informasi lengkap untuk perawatan.
    
    Tabel ini berfungsi sebagai ensiklopedia tanaman yang dapat digunakan untuk:
    - Referensi identifikasi AI
    - Panduan perawatan pengguna
    - Database untuk jadwal perawatan otomatis
    
    Relasi:
    - One-to-Many dengan Schedule (satu tanaman bisa punya banyak jadwal perawatan)
    """
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    nama_ilmiah = Column(String, unique=True, index=True)  # Nama latin untuk identifikasi akurat
    nama_lokal = Column(String, index=True)  # Nama umum dalam bahasa Indonesia
    deskripsi = Column(Text)  # Deskripsi lengkap karakteristik tanaman
    
    # Informasi perawatan - digunakan untuk generate jadwal otomatis
    kebutuhan_air = Column(String)  # Frekuensi penyiraman (misal: "2-3 hari sekali")
    intensitas_cahaya = Column(String)  # Kebutuhan cahaya (misal: "Cahaya tidak langsung")
    jenis_media_tanam = Column(String)  # Jenis tanah/media yang cocok
    jadwal_pemupukan = Column(String)  # Frekuensi pemupukan (misal: "2 minggu sekali")

    # Relasi ke jadwal perawatan
    schedules = relationship("Schedule", back_populates="plant")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"))
    tipe_perawatan = Column(String)
    tanggal_waktu = Column(DateTime)
    status = Column(String, default="terjadwal") # terjadwal, selesai, dilewati

    plant = relationship("Plant", back_populates="schedules")

class PestDisease(Base):
    __tablename__ = "pest_diseases"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, unique=True, index=True)
    deskripsi = Column(Text)
    gejala = Column(Text)
    solusi_organik = Column(Text)
    solusi_kimia = Column(Text)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    post_id = Column(Integer, ForeignKey("posts.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="comments")
    owner = relationship("User", back_populates="comments")
