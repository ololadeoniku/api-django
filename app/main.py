from fastapi import (
                        FastAPI, Request, Depends, File, UploadFile, HTTPException,  Header
                    )
import pathlib
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os
import io
import uuid
from pydantic import BaseSettings
from functools import lru_cache
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'

class Settings(BaseSettings):
    app_auth_token: str
    debug: bool = False
    echo_active: bool = False
    app_auth_token_prod: str = None
    skip_auth: bool = False

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
DEBUG=settings.debug

BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
def home_view(request: Request, settings:Settings=Depends(get_settings)):
    # return "<h1>Hello World</h1>"
    return templates.TemplateResponse("home.html", {"request":request, "guest":"Guest"})


# @app.post("/")
# def home_detail_view():
#     return {"hello": "world"}

def verify_auth(authorization=Header(None), settings:Settings=Depends(get_settings)):
    if settings.debug and settings.skip_auth:
        return
    if authorization is None:
        raise HTTPException(detail="Invalid endpoint", status_code=400)
    label, token = authorization.split()
    if token != settings.app_auth_token:
        raise HTTPException(detail="Invalid image", status_code=401)



@app.post("/")
async def prediction_view(file:UploadFile=File(""), authorization=Header(None), settings:Settings=Depends(get_settings)):
    verify_auth(authorization, settings)
    bytes_str = io.BytesIO(await file.read())
    try:
        image = Image.open(bytes_str)     # alternatives are openCV, CV2
    except:
        raise HTTPException(detail="Invalid image", status_code=400)
    preds = pytesseract.image_to_string(image)
    predictions = [x for x in preds.split('\n')]
    return {'results': predictions, 'original':preds}


@app.post("/img-view/", response_class=FileResponse)
async def image_view(file:UploadFile=File(""), settings:Settings=Depends(get_settings)):
    if not settings.echo_active:
        raise HTTPException(detail="Invalid endpoint", status_code=400)
    UPLOAD_DIR.mkdir(exist_ok=True)
    bytes_str = io.BytesIO(await file.read())
    try:
        image = Image.open(bytes_str)     # alternatives are openCV, CV2
    except:
        raise HTTPException(detail="Invalid image", status_code=400)
    fname = pathlib.Path(file.filename)
    fext = fname.suffix # .jpg .etc...
    dest = UPLOAD_DIR / f'{uuid.uuid1()}{fext}'
    # with open(str(dest), 'wb') as out:
    #     out.write(bytes_str.read())
    image.save(dest)
    return dest


# uvicorn app.main:app --reload
# import secrets
# secrets.token_urlsafe(32)