from app.main import UPLOAD_DIR, app, BASE_DIR, get_settings
from fastapi.testclient import TestClient
import shutil
import time
from PIL import Image, ImageChops, ImageStat
import io
import numpy as np

client = TestClient(app)

def test_get_home():
    response = client.get("/")   # requests.get("") # python requests
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']
    assert response.text != "<h1>Hello World</h1>"


# def test_invalid_file_upload():
#     response = client.post("/")   # requests.get("") # python requests
#     assert response.status_code == 422
#     assert "application/json" in response.headers['content-type']
#     assert response.json() == {"hello": "world"}


# VALID_IMAGE_EXT = ['png' 'jpeg', 'jpg']

def test_img_echo_view():
    image_saved_path = BASE_DIR / "images"
    for path in image_saved_path.glob("*"):
        try:
            image = Image.open(path)#.convert('RGB')
        except:
            image = None
    # path = list((BASE_DIR / "images").glob("*"))[0] # glob gets all the images in the images folder
        response = client.post("/img-view/", files={'file': open(path, 'rb')})   # requests.get("") # python requests
        # fext = str(path.suffix).replace('.', '')
        # if fext in VALID_IMAGE_EXT:
        # assert fext in response.headers['content-type']
        # print(response.headers)
        if image is None:
            # assert fext in response.headers['content-type']
            assert response.status_code == 400
        else:
            assert response.status_code == 200
            r_stream = io.BytesIO(response.content)   # returning a valid image
            echo_img = Image.open(r_stream)
            difference = ImageChops.difference(echo_img, image).getbbox()
            assert echo_img.im.bands == image.im.bands
            assert echo_img.mode == image.mode
            assert echo_img.size == image.size
            # assert difference is None

    time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)


def test_prediction_upload():
    settings = get_settings()
    image_saved_path = BASE_DIR / "images"
    for path in image_saved_path.glob("*"):
        try:
            image = Image.open(path)#.convert('RGB')
        except:
            image = None
        response = client.post("/", files={'file': open(path, 'rb')}, headers={"Authorization": f'JWT {settings.app_auth_token}'})   # requests.get("") # python requests
        if image is None:
            assert response.status_code == 400
        else:
            assert response.status_code == 200
            data = response.json()
            assert len(data.keys()) == 2


def test_prediction_upload_missing_header():
    settings = get_settings()
    image_saved_path = BASE_DIR / "images"
    for path in image_saved_path.glob("*"):
        try:
            image = Image.open(path)#.convert('RGB')
        except:
            image = None
        response = client.post("/", files={'file': open(path, 'rb')})   # requests.get("") # python requests
        assert response.status_code == 400