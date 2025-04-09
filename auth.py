from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import jwt
import os
from dotenv import load_dotenv
from database import users_collection  # Mongo bağlantısı

load_dotenv()
router = APIRouter(prefix="/auth", tags=["Email Auth"])

# Şifreleme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Ortam değişkenleri
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# -------------------------------
# ŞEMA TANIMLARI
# -------------------------------

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# -------------------------------
# KAYIT – MongoDB’ye Kayıt
# -------------------------------

@router.post("/register", status_code=201)
async def register(user: UserRegister):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Bu e-posta zaten kayıtlı.")
    
    hashed_pw = pwd_context.hash(user.password)
    user_dict = {"email": user.email, "hashed_password": hashed_pw}
    await users_collection.insert_one(user_dict)

    return {"message": "Kayıt başarılı."}

# -------------------------------
# GİRİŞ – MongoDB’den Doğrulama
# -------------------------------

@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    user_record = await users_collection.find_one({"email": user.email})
    if not user_record:
        raise HTTPException(status_code=400, detail="Kullanıcı bulunamadı.")
    
    if not pwd_context.verify(user.password, user_record["hashed_password"]):
        raise HTTPException(status_code=400, detail="Şifre hatalı.")

    token_data = {"sub": user.email}
    access_token = create_access_token(token_data)

    return {"access_token": access_token}

# -------------------------------
# JWT Token Oluştur
# -------------------------------

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
