from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, Text, Integer,DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped
from datetime import datetime

Base = declarative_base()

class Users(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = Column(Integer,primary_key=True)
    name: Mapped[str] = Column(String(1024),nullable=False)
    phone: Mapped[str] = Column(String(12),nullable=False)
    flat_number: Mapped[int] = Column(Integer,nullable=True)
    created_at = Column(DateTime(),default=datetime.now)

class Dog(Base):
    __tablename__ = "dog"
    dog_id: Mapped[int] = Column(Integer,primary_key=True)
    dog_name: Mapped[int] = Column(String(1024),nullable=False)
    dog_description: Mapped[str] = Column(Text)
    created_at = Column(DateTime(),default=datetime.now)

class User_x_dog(Base):
    __tablename__ = "user_x_dog"
    rel_id: Mapped[int] = Column(Integer,primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.user_id"),nullable=False)
    dog_id: Mapped[int] = Column(Integer, ForeignKey("dog.dog_id"),nullable=False)

class Time_price(Base):
    __tablename__ = "time_price"
    time_id: Mapped[int] = Column(Integer,primary_key=True)
    hour_minute: Mapped[str] = Column(String(5),nullable=False)
    price: Mapped[float] = Column(Float,nullable=False)

class Walk(Base):
    __tablename__ = "walk"
    walk_id: Mapped[int] = Column(Integer,primary_key=True)
    start_date = Column(DateTime(),nullable=False)
    end_date = Column(DateTime(),nullable=False)
    dog_id: Mapped[int] = Column(Integer, ForeignKey("dog.dog_id"),nullable=False)
    status: Mapped[str] = Column(String(4),nullable=False)
    created_at = Column(DateTime(),default=datetime.now)
    

