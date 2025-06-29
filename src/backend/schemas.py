from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class CommentBase(BaseModel):
    content: str
    post_id: int

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Post(PostBase):
    id: int
    owner_id: int
    created_at: datetime
    comments: List[Comment] = []

    class Config:
        orm_mode = True

class User(UserBase):
    id: int
    is_active: bool
    posts: List[Post] = []
    comments: List[Comment] = []

    class Config:
        orm_mode = True

class PlantBase(BaseModel):
    nama_ilmiah: str
    nama_lokal: str
    deskripsi: Optional[str] = None
    kebutuhan_air: Optional[str] = None
    intensitas_cahaya: Optional[str] = None
    jenis_media_tanam: Optional[str] = None
    jadwal_pemupukan: Optional[str] = None

class PlantCreate(PlantBase):
    pass

class ScheduleBase(BaseModel):
    plant_id: int
    tipe_perawatan: str
    tanggal_waktu: datetime
    status: Optional[str] = "terjadwal"

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int

    class Config:
        orm_mode = True

class PestDiseaseBase(BaseModel):
    nama: str
    deskripsi: Optional[str] = None
    gejala: Optional[str] = None
    solusi_organik: Optional[str] = None
    solusi_kimia: Optional[str] = None

class PestDiseaseCreate(PestDiseaseBase):
    pass

class PestDisease(PestDiseaseBase):
    id: int

    class Config:
        orm_mode = True

class Plant(PlantBase):
    id: int
    schedules: List[Schedule] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
