from sqlalchemy.orm import Session
import models, schemas
import os
import numpy as np
import cv2 
from datetime import datetime
import base64
import random
from myutil import decode_base64_image
# 📚 Book 기능
def insert_book(db: Session):
    timestamp = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
    book_path = f"pb_books/pb_book_{timestamp}"  # ✅ 폴더명 형식 설정
    
    while os.path.exists(book_path):
        print("같은시간에 저장된 파일 존재")
        timestamp = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
        book_path = f"pb_books/pb_book_{timestamp}"
    
    os.makedirs(book_path, exist_ok=True)

    new_book = models.Book(book_path=book_path)

    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

def get_books(db: Session):
    return db.query(models.Book).all()
def get_book_by_id(db: Session, book_id)->models.Book|None:
    return db.query(models.Book).filter(models.Book.book_id==book_id).first()

# 📄 Page 기능
def insert_page(db: Session,  book_id: int,  image: np.ndarray,story: str = None):
    
    book = db.query(models.Book)\
        .filter(models.Book.book_id == book_id)\
            .first()
    if not book:
        raise ValueError("Book not found")
    
    # ✅ 현재 book_id에서 가장 높은 page_order 가져오기
    last_page = db.query(models.Page)\
        .filter(models.Page.book_id == book_id)\
        .order_by(models.Page.page_order.desc())\
        .first()
    
    page_order = (last_page.page_order + 1) if last_page else 1  # ✅ 마지막 page_order +1 (없으면 1부터 시작)
    
    image_filename = f"page_{page_order}.png"

    image_path = os.path.join(book.book_path, image_filename)
    #이미지 저장
    cv2.imwrite(image_path, image)

    #페이지 생성
    new_page = models.Page(book_id=book_id, 
                           page_order=page_order, 
                           story=story)
    
    db.add(new_page)
    db.commit()
    db.refresh(new_page)
    
    return new_page
def get_page_by_id(db: Session, page_id: int):
    return db.query(models.Page)\
        .filter(models.Page.page_id == page_id)\
            .first()

def get_pages_by_book(db: Session, book_id: int):
    return db.query(models.Page)\
        .filter(models.Page.book_id == book_id)\
            .all()

def update_page_story(db: Session, page_id: int, story: str):
    """
    ✅ 페이지의 스토리를 나중에 업데이트하는 함수.
    :param db: 데이터베이스 세션
    :param page_id: 업데이트할 페이지 ID
    :param story: 추가할 스토리 내용
    """
    page = db.query(models.Page)\
        .filter(models.Page.page_id == page_id)\
            .first()
    if not page:
        raise ValueError("Page not found")

    # ✅ 스토리 업데이트
    page.story = story
    db.commit()
    db.refresh(page)  # 변경된 데이터 반영

    return page

# 🎭 Character 기능
def insert_character(db: Session,
                     book:models.Book, 
                     page:models.Page,
                     character_index:int, 
                     character_info:dict):
    new_character = models.CharacterInfo(
        page_id=page.page_id,
        #label=charactor_info["label"],
        character_index=character_index,
        x_position=character_info["loc"][0],
        y_position=character_info["loc"][1],
        width=character_info["scale"][0],
        height=character_info["scale"][1]
    )
    db.add(new_character)
    db.commit()
    db.refresh(new_character)

    #분류된 이미지저장
    #페이지와 같은 폴더에 저장
    image_filename = f"page_{page.page_order}_{character_index}.png"
    image_path = os.path.join(book.book_path, image_filename)

    #이부분을 image porcessing.py에 넣어야함

    image=decode_base64_image(character_info["image"],4)
    cv2.imwrite(image_path, image)

    #페이지와 다른 폴더(image_bank)에 저장 # 여기는 폐기 예정 일단 주석 #폐기
    image_filename = f"character_{new_character.character_id}.png"
    image_path = os.path.join("image_bank", image_filename)
    cv2.imwrite(image_path, image)

    return new_character

def get_characters_by_page(db: Session, page_id: int):
    return db.query(models.CharacterInfo)\
        .filter(models.CharacterInfo.page_id == page_id)\
            .all()

def get_character_by_index(db: Session, 
                           page_id: int, 
                           character_index: int):
    """
    ✅ 특정 페이지에서 `character_index`가 일치하는 캐릭터 조회 함수
    :param db: 데이터베이스 세션
    :param page_id: 검색할 페이지 ID
    :param character_index: 찾고자 하는 캐릭터의 순서 (1부터 시작)
    :return: 해당하는 `CharacterInfo` 객체 또는 None
    """
    return db.query(models.CharacterInfo)\
        .filter(models.CharacterInfo.page_id == page_id)\
        .filter(models.CharacterInfo.character_index == character_index)\
        .first()

# 🎭 CharacterAttribute 기능
def insert_character_attribute(db: Session, 
                               character_id:int,
                               attribute_name:str, 
                               attribute_value:str):
    
    new_attr = models.CharacterAttribute(
        character_id=character_id,
        attribute_name=attribute_name, 
        attribute_value=attribute_value
    )
    db.add(new_attr)
    db.commit()
    db.refresh(new_attr)
    return new_attr

def get_character_attributes(db: Session, character_id: int):
    return db.query(models.CharacterAttribute)\
        .filter(models.CharacterAttribute.character_id == character_id)\
            .all()

from sqlalchemy.orm import Session
import models
def get_character_image(book_path: str,page:int,char:int):
    image_filename = f"page_{page}_{char}.png"
    image_path = os.path.join(book_path, image_filename)
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED) 
    _, buffer = cv2.imencode(".png", image)  
    base64_image = base64.b64encode(buffer).decode("utf-8")
    return base64_image
def get_page_image(book_path: str,page:int):
    image_filename = f"page_{page}.png"
    image_path = os.path.join(book_path, image_filename)
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED) 
    _, buffer = cv2.imencode(".png", image)  
    base64_image = base64.b64encode(buffer).decode("utf-8")
    return base64_image

def get_book_story(db: Session, book_id: int):
    book = db.query(models.Book).filter(models.Book.book_id==book_id).first()
    if not book:
        return {"error": "해당하는 book을 찾을 수 없습니다."}

    # ✅ book_id에 해당하는 모든 페이지 가져오기
    pages = db.query(models.Page).filter(models.Page.book_id == book.book_id).all()

    book_data = {
        "book_id": book.book_id,
        "book_path": book.book_path,
        "pages": []
    }

    for page in pages:
        characters = db.query(models.CharacterInfo).filter(models.CharacterInfo.page_id == page.page_id).all()
        pg_image=get_page_image(book_path=book.book_path,page=page.page_order)
        page_data = {
            "page_id": page.page_id,
            "page_order": page.page_order,
            "page_image": pg_image,
            "story": page.story,
            "characters": []
        }

        for char in characters:
            attributes = db.query(models.CharacterAttribute).filter(models.CharacterAttribute.character_id == char.character_id).all()
            image=get_character_image(book_path=book.book_path,page=page.page_order,char=char.character_index)
            character_data = {
                "character_id": char.character_id,
                "character_index": char.character_index,
                "character_image": image,
                #"character_image": "base64로 인코딩된 이미지",
                "x_position": char.x_position,
                "y_position": char.y_position,
                "width": char.width,
                "height": char.height,
                "attributes": [
                    {"attribute_name": attr.attribute_name, "attribute_value": attr.attribute_value}
                    for attr in attributes
                ]  # ✅ 캐릭터 속성을 리스트로 변환
            }
            page_data["characters"].append(character_data)

        book_data["pages"].append(page_data)

    return book_data  # ✅ ORM 객체를 반환하지 않고, JSON 변환된 dict 반환



def get_random_characters(db: Session, folder_path: str):
    """
    ✅ 저장된 캐릭터 이미지 중 랜덤하게 3개 선택하여 특성과 함께 반환.
    :param db: 데이터베이스 세션
    :param folder_path: 캐릭터 이미지가 저장된 폴더 경로 (예: "pb_book_24-02-24-12-30-45")
    :return: 선택된 3개 캐릭터 정보 (이미지 파일명 + 특성 포함)
    """

    # ✅ 해당 폴더에서 "character_{character_id}.png" 형식의 파일 목록 가져오기
    character_files = [f for f in os.listdir(folder_path) if f.startswith("character_") and f.endswith(".png")]

    if not character_files:
        return {"error": "해당 폴더에 캐릭터 이미지가 없습니다."}

    # ✅ 랜덤하게 3개의 캐릭터 선택 (파일명에서 character_id 추출)
    selected_files = random.sample(character_files, min(3, len(character_files)))
    
    character_data_list = []

    for file_name in selected_files:
        # ✅ 파일명에서 character_id 추출
        character_id = int(file_name.replace("character_", "").replace(".png", ""))

        # ✅ DB에서 해당 character_id의 정보 가져오기
        character = db.query(models.CharacterInfo).filter(models.CharacterInfo.character_id == character_id).first()

        if not character:
            continue  # 해당 캐릭터가 DB에 없으면 무시

        image_path=os.path.join(folder_path,file_name)
        #image = cv2.imread(image_path)
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED) 
        _, buffer = cv2.imencode(".png", image)  
        base64_image = base64.b64encode(buffer).decode("utf-8")

        character_data = {
            "image": base64_image,
            "width": character.width,
            "height": character.height
        }
        character_data_list.append(character_data)

    return character_data_list  # ✅ 선택된 캐릭터 정보 리스트 반환