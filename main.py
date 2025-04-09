from fastapi import FastAPI, HTTPException, Depends, Request
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database import users_collection
from models import User, UserInDB
from schemas import UserCreate, UserResponse
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
import os
import logging

# .env dosyasını yükle
load_dotenv()

# FastAPI uygulaması
app = FastAPI()

# SessionMiddleware: Google login için şart (SECRET_KEY .env'den alınır)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

# Logger ayarı
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Şifreleme context'i
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# .env'den gelen ayarlar
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# OAuth - Google yapılandırması
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Şifreyi hash’leme fonksiyonu
def get_password_hash(password):
    return pwd_context.hash(password)

# /register endpoint'i: Normal kullanıcı kaydı
@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_password = get_password_hash(user.password)
    users_collection.insert_one({
        "email": user.email,
        "hashed_password": hashed_password,
        "google_login": False
    })
    return UserResponse(email=user.email)

# /login endpoint'i: Normal kullanıcı girişi
@app.post("/login")
async def login(user: UserCreate):
    db_user = users_collection.find_one({"email": user.email, "google_login": False})
    if not db_user or not pwd_context.verify(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": user.email, "exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# /auth/google/login endpoint'i: Google login için yönlendirme
@app.get('/auth/google/login')
async def google_login(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

# /auth/google/callback endpoint'i: Google login'in dönüşü
@app.get('/auth/google/callback')
async def google_callback(request: Request):
    try:
        # OAuth2 tokenını al
        token = await oauth.google.authorize_access_token(request)
        logger.info(f"🔑 Google Token: {token}")
        
        # Kullanıcı bilgilerini almak için doğrudan userinfo endpoint'ini kullan:
        userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
        resp = await oauth.google.get(userinfo_url, token=token)
        user_info = resp.json()
        logger.info(f"👤 Google User Info: {user_info}")
    except Exception as e:
        logger.error(f"❌ Google login failed: {e}")
        raise HTTPException(status_code=400, detail=f"Google login failed: {str(e)}")
    
    email = user_info.get('email')
    if not email:
        raise HTTPException(status_code=400, detail="Email bilgisi alınamadı")
    
    existing_user = users_collection.find_one({"email": email})
    if not existing_user:
        users_collection.insert_one({
            "email": email,
            "google_login": True,
            "name": user_info.get("name", ""),
            "picture": user_info.get("picture", "")
        })
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": email, "exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": email,
        "name": user_info.get("name", ""),
        "picture": user_info.get("picture", "")
    }
