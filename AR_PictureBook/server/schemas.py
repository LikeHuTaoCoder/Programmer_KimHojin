# from pydantic import BaseModel
# from typing import List, Optional

# # 🎭 Character 속성 스키마
# class CharacterAttributeBase(BaseModel):
#     attribute_name: str
#     attribute_value: str

# class CharacterAttributeCreate(CharacterAttributeBase):
#      character_id: int

# class CharacterAttribute(CharacterAttributeBase):
#     attribute_id: int
#     character_id: int

#     class Config:
#         orm_mode = True

# # 🎭 CharacterInfo 스키마 (🔹 변경됨)
# class CharacterInfoBase(BaseModel):  # 🔹 클래스명 변경됨
#     x_position: int
#     y_position: int
#     width: int
#     height: int

# class CharacterInfoCreate(CharacterInfoBase):  # 🔹 클래스명 변경됨
#     page_id: int

# class CharacterInfo(CharacterInfoBase):  # 🔹 클래스명 변경됨
#     character_id: int
#     page_id: int
#     attributes: List[CharacterAttribute] = []

#     class Config:
#         orm_mode = True

# # 📄 Page 스키마
# class PageBase(BaseModel):
#     page_order: int
#     story: Optional[str] = None

# class PageCreate(PageBase):
#     book_id: int

# class Page(PageBase):
#     page_id: int
#     book_id: int
#     characters: List[CharacterInfo] = []

#     class Config:
#         orm_mode = True

# # 📚 Book 스키마
# class BookBase(BaseModel):
#     book_path: str

# class BookCreate(BookBase):
#     pass

# class Book(BookBase):
#     book_id: int
#     pages: List[Page] = []

#     class Config:
#         orm_mode = True
