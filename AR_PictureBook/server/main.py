from fastapi import FastAPI, HTTPException,WebSocket,WebSocketDisconnect
from pydantic import BaseModel
from langchain.chains import LLMChain
import base64
import cv2
from sqlalchemy.orm import Session
from fastapi import Depends
import numpy as np
import ssl
import json
import dotenv

app = FastAPI()
dotenv.load_dotenv() # 먼저해야 이후 참조할때 쓸수 있음

from crud import insert_page,insert_character,insert_book,insert_character_attribute,update_page_story
from crud import get_character_by_index,get_book_story,get_random_characters,get_book_by_id,get_character_image,get_characters_by_page,get_page_by_id
from image_captioning import generate_caption,caption_init,story_init,generate_story
from image_processing import generate_story_and_caption
from myutil import decode_base64_image, speech_to_text, text_to_image_url
from make_sentence import make_sentence
from yolo_model import YOLOModel
import schemas
from database import get_db




#llm을 yolo이미지 하나에 박는 거 준비


# YOLO 모델 초기화 (모델 경로를 적절히 수정하세요)
yolo_model = YOLOModel("pic10_yolo11m.pt")

class ImageData(BaseModel):
    image: str  # Base64 인코딩된 이미지 데이터
    book_id: int

class BranchImageData(BaseModel):
    chara: str
    bg:str
    charaPosX: int
    charaPosY: int
    book_id: int
    reversed: bool = False

class WavData(BaseModel):
    wav: str
    book_id: int

class TextData(BaseModel):
    text: str
    #book_id: int
class SentenceData(BaseModel):
    name: str
    status: str
story_chains=[]
caption_chains=[]

saved_chain_story=[]
saved_chain_caption=[]
page_id=0

just_use_image=True

@app.get("/")
def check():
    return "나다"
cnt=0

@app.post("/upload")
def upload_image(data: ImageData,db:Session=Depends(get_db)):
    
    global cnt
    cnt+=1
    
    #여기 구조 수정필요 id가 -1인 book이 없으면 book생성으로 바꿔야함
    if data.book_id==-1:
        book=insert_book(db=db)
        caption_chains.append(caption_init())
        story_chains.append(story_init())
    else:
        book=get_book_by_id(db=db,book_id=data.book_id)
    
    #이어하기 기능이라 데베에서 가져오면 좋을듯듯
    if len(story_chains) == 0:
        caption_chains.append(caption_init())
        story_chains.append(story_init())
        
    print("요청1")
    # Base64 인코딩 -> 디코딩하여 numpy 배열로 변환
    if just_use_image:
        image_array = decode_base64_image(data.image,3)
    else:
        #image_array = cv2.imread(f"./images/{cnt}.jpg", cv2.IMREAD_COLOR)
        image_array = cv2.imread("./results/orig_image.png", cv2.IMREAD_COLOR)
    
    print(image_array.shape)
    #웹캠이 달라질걸 염려하면 사이즈를 imageData에서 받아서 조정하는게 좋을듯
    
    # if image_array.shape[0] == 480 and image_array.shape[1] == 640:
    #     image_array=image_array[80:480,:]
    # else:
    #     image_array = cv2.resize(image_array, (640, 400))
    #image_array = cv2.resize(image_array, (640, 360))  # YOLO 모델에 맞게 이미지 크기 조정
    #image_array = cv2.resize(image_array, (640, 400))  # 이건 이미지 사이즈를 줄이는거지 자르는게 아님
    #image_array=image_array[120:480,:]#16:9 로 자름
    #16:10 로 자름
    image_array = cv2.resize(image_array, (1920, 1200))  # YOLO 모델에 맞게 이미지 크기 조정
    print(image_array.shape)
    # YOLO 모델을 사용하여 예측 수행
    pred_results = yolo_model.predict(image_array)
    
    # 이미지 처리 후 결과 반환
    return_results = yolo_model.process_results(pred_results, image_array)
    
    result=return_results[0]
    
    new_image_array= decode_base64_image(result["image_with_contour"],4)
    #캐릭터를 담을페이지 추가
    page=insert_page(db=db,book_id=book.book_id,image=image_array)
    global page_id
    page_id=page.page_id

    for index,res in enumerate(result["yolo_images"]):
        insert_character(db=db,book=book,page=page,character_index=index,character_info=res)
    
    result["book_id"]=book.book_id
    return result

@app.post("/storyMaker")
def story_make(data: ImageData, db: Session = Depends(get_db)):
    print("요청2")
    global page_id
    global cnt #이미지를 폴더에서 가져오기위한 임의 변수 평소엔 사용 X

    #??? 어차피 욜로 단계에서 책 아이디랑 페이지랑 다 확인하는데 그냥 페이지 id하나만 넘겨주면 되는 부분이 아닌지 이미지 왜 보냄
    if just_use_image:
        image_array = decode_base64_image(data.image,3)
    else:
        #image_array = cv2.imread(f"./images/{cnt}.jpg", cv2.IMREAD_COLOR)
        image_array = cv2.imread("./results/orig_image.png", cv2.IMREAD_COLOR)

    _, buffer = cv2.imencode(".png", image_array)  # PNG로 메모리 버퍼에 저장
    base64_image = base64.b64encode(buffer).decode("utf-8")  # Base64로 인코딩  
    
    
    print(len(caption_chains))
    
    #print(story_chains[-1].memory.chat_memory.messages)
    # 안녕하세오 저는 챗지피띠에오 메모리를 꺼내는 방법을 찾아와서 알려주고 갈게오 수고하세오
    메1모2리 = story_chains[-1].memory.load_memory_variables({})['chat_history']
    print(메1모2리)
    print(type(메1모2리))
    if len(메1모2리) > 0:
        print(메1모2리[0].content)
    else:
        print("지금 내 메모리 텅텅")

    #언젠간 동시에 하게 수정해야함

    book=get_book_by_id(db=db,book_id=data.book_id)
    page=get_page_by_id(db=db,page_id=page_id)
    characters=get_characters_by_page(db=db,page_id=page_id)

    result=generate_story_and_caption(base64_image=base64_image,
                                      book=book,
                                      page=page,
                                      characters=characters,
                                      story_chain=story_chains[-1],
                                      caption_chain=caption_chains[-1])
    
    update_page_story(db=db,page_id=page_id,story=result["story"])
    if not result["characterInfo"] == "null":
        for index,res in enumerate(result["characterInfo"]):
            character=get_character_by_index(db=db,page_id=page_id,character_index=index)
            if character is None:
                continue
            else:
                character_id=character.character_id
            for attribute_name,attribute_value in res.items():
                if attribute_name == "id":
                    continue
                if attribute_name == "color":
                    attribute_value=",".join(attribute_value)
                insert_character_attribute(db=db, character_id=character_id, attribute_name=attribute_name, attribute_value=attribute_value)
    
    #텍스트화
    result=json.dumps(result,ensure_ascii=False)
    return result


def overlay_images(background, overlay, center_x, center_y):
    h_s, w_s, _ = overlay.shape
    h_b, w_b, _ = background.shape

    x_tl = max(0, min(int(center_x - w_s / 2), w_b - w_s))
    y_tl = max(0, min(int(center_y - h_s / 2), h_b - h_s))

    # 분리: overlay RGBA
    overlay_rgb = overlay[..., :3].astype(float)
    overlay_alpha = overlay[..., 3].astype(float) / 255.0
    overlay_alpha = np.expand_dims(overlay_alpha, axis=2)  # (H, W, 1)

    # background RGB만 사용 (4채널일 수 있음)
    background_region = background[y_tl:y_tl + h_s, x_tl:x_tl + w_s, :3].astype(float)

    # 알파 블렌딩
    blended_region = overlay_rgb * overlay_alpha + background_region * (1 - overlay_alpha)

    # 결과 합치기
    result = background.copy()
    result[y_tl:y_tl + h_s, x_tl:x_tl + w_s, :3] = blended_region.astype(np.uint8)

    return result

@app.post("/branch")
def change_story(data: BranchImageData):
    print("요청3")
    print(data.charaPosX,data.charaPosY)
    chara_array = decode_base64_image(data.chara,4)
    chara_array = cv2.resize(chara_array, (300, 300))
    
    if data.reversed:
        chara_array = cv2.flip(chara_array, 1)
    bg_array = decode_base64_image(data.bg,4)
    print(chara_array.shape)
    print(bg_array.shape)
    bg_array = cv2.resize(bg_array, (1920, 1200))  # 배경 이미지 크기 조정
    #만약 좌표 수정이 필요할시 여기서 뒤에 저 두 값만 조정하면됨(x,y)
    
    result_image = overlay_images(bg_array, chara_array, data.charaPosX, data.charaPosY)

    _, buffer = cv2.imencode(".png", result_image)  # PNG로 메모리 버퍼에 저장
    base64_image = base64.b64encode(buffer).decode("utf-8")  # Base64로 인코딩
    #print(data.charaPosX-imgshp[1]//2,data.charaPosX+imgshp[1]//2,data.charaPosY-imgshp[0]//2,data.charaPosY+imgshp[0]//2)
    result = {
                "image": base64_image,
                "book_id": data.book_id
            }
    return result
@app.get("/book_load/{book_id}")
def load_book_story(book_id: int, db: Session = Depends(get_db)):
    book_data = get_book_story(db, book_id)
    
    if not book_data:
        return {"error": "해당하는 book을 찾을 수 없습니다."}
    return book_data
@app.get("/random_characters")
def random_characters(db: Session = Depends(get_db)):
    return get_random_characters(db,"image_bank" )
    
@app.post("/stt")
def stt(data: WavData):

    wavText = speech_to_text(data.wav)
    
    result = {
                "text": wavText
            }
    return result
@app.post("/generate")
def create_new_picture(data: TextData):

    imageUri = text_to_image_url(data.text)
    
    result = {
                "b64image": imageUri
            }
    return result
@app.post("/sentence")
def generate_sentence(data: SentenceData):
    sentence = ""
    print(data.name, data.status)
    # 여기서 sentence를 생성하는 로직을 추가해야 합니다.
    sentence=make_sentence(data.name,data.status)
    return{
        "sentence": sentence
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",  # main.py의 app 객체
        host="0.0.0.0",  
        port=8000,  # HTTPS 기본 포트
        ssl_certfile="important/cert.pem",  # 인증서 파일 경로
        ssl_keyfile="important/key.pem",  # 키 파일 경로
    )

