from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")  

    
    company = relationship("Company", back_populates="owner", uselist=False)

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tax_number = Column(String, unique=True, index=True)

    #AI
    toplam_borc = Column(String, default="0 TL")
    toplam_limit = Column(String, default="0 TL")
    risk_skoru = Column(String, default="Belirsiz")
    uzman_gorusu = Column(String, default="")

    #MANUEL
    bilanco_toplami = Column(String, default="0 TL")
    gelir_tablosu = Column(String, default="0 TL")
    banka_limit = Column(String, default="0 TL")
    nakit_akis = Column(String, default="Dengeli")

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="company")

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, index=True) 
    details = Column(String)            
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
