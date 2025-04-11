from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import os
import requests
import jwt
from dotenv import load_dotenv
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

load_dotenv()

router = APIRouter(tags=["Google Auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://egitim-ai-api.onrender.com/auth/google/callback")  # canlıya göre güncel
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

FRONTEND_REDIRECT_URL = "https://egitim-ai-frontend.onrender.com/google-success"

@router.get("/login")
def google_login():
    query_params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(query_params)}"
    return RedirectResponse(url)

@router.get("/callback")
def google_callback(request: Request, code: str):
    # 1. Google'dan access token al
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    print("🔍 Google token JSON:", token_json)
    id_token_str = token_json.get("id_token")

    if not id_token_str:
        raise HTTPException(status_code=400, detail="Google token alınamadı.")

    # 2. Token'ı doğrula
    user_info = google_id_token.verify_oauth2_token(
        id_token_str, google_requests.Request(), GOOGLE_CLIENT_ID
    )

    email = user_info.get("email")
    payload = {"sub": email}
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # 3. Kullanıcıyı frontend'e yönlendir (token ile)
    return RedirectResponse(
        url=f"{FRONTEND_REDIRECT_URL}?token={access_token}"
    )
