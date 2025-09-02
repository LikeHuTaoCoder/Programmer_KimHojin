from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# 📚 Book 테이블
class Book(Base):
    __tablename__ = "book"

    book_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_path = Column(String(255), nullable=False)

    pages = relationship("Page", back_populates="book", cascade="all, delete", lazy="joined")  # ✅ 변경

# 📄 Page 테이블
class Page(Base):
    __tablename__ = "page"

    page_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("book.book_id", ondelete="CASCADE"), nullable=False)
    page_order = Column(Integer, nullable=False)
    story = Column(Text, nullable=True)

    book = relationship("Book", back_populates="pages", lazy="joined")  # ✅ 변경
    characters = relationship("CharacterInfo", back_populates="page", cascade="all, delete", lazy="joined")  # ✅ 변경

# 🎭 CharacterInfo 테이블
class CharacterInfo(Base):
    __tablename__ = "character_info"

    character_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey("page.page_id", ondelete="CASCADE"), nullable=False)
    character_index = Column(Integer, nullable=False)
    x_position = Column(Integer, nullable=False)
    y_position = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)

    page = relationship("Page", back_populates="characters", lazy="joined")  # ✅ 변경
    attributes = relationship("CharacterAttribute", back_populates="character_info", cascade="all, delete", lazy="joined")  # ✅ 변경

# 🎭 CharacterAttribute 테이블
class CharacterAttribute(Base):
    __tablename__ = "character_attribute"

    attribute_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("character_info.character_id", ondelete="CASCADE"), nullable=False)
    attribute_name = Column(String(50), nullable=False)
    attribute_value = Column(String(100), nullable=False)

    character_info = relationship("CharacterInfo", back_populates="attributes", lazy="joined")  # ✅ 변경
