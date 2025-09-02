import numpy as np
import base64
import cv2
from image_generator import dall_e_generater, chatgpt_wisper_stt

def decode_base64_image(image_data: str, channels:int):
    # Base64 데이터를 받아 numpy array로 변환
    decoded_data = base64.b64decode(image_data)
    image_array = np.frombuffer(decoded_data, dtype=np.uint8)
    if channels == 3:
        image_array = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    else:    
        image_array = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)
    return image_array


def speech_to_text(wav:str):
    text=chatgpt_wisper_stt(wav)
    return text

def text_to_image_url(text:str):
    # text = "A cute cat"
    image_url=dall_e_generater(text)
    return image_url

