from sqlalchemy import Column, Integer, String
from dbconnection import Base


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(150), unique=True, nullable=False)
    mobile = Column(String(20), unique=True, nullable=False)
    password = Column(String(255))
    photo = Column(String(255))