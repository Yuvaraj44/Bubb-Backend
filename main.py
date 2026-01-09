from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import easyocr
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reader = easyocr.Reader(['en'], gpu=False)


def evaluate_expression(expr):
    try:
        expr = expr.replace("×", "*")
        return eval(expr)
    except:
        return None


@app.post("/scan")
async def scan_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Read entire image (SINGLE expression)
    text = reader.readtext(gray, detail=0)

    if not text:
        return {}

    match = re.findall(r"[0-9+\-*/]+", text[0])
    if not match:
        return {}

    expr = match[0]
    value = evaluate_expression(expr)

    if value is None:
        return {}

    return {
        "expression": expr,
        "result": value
    }
