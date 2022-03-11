from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True)
    hashed_password = Column(String)
    full_name = Column(String)
    npm = Column(String)
    client_id = Column(String)
    client_secret = Column(String)

    token = relationship("Token", back_populates="owner", uselist=False)


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String)
    refresh_token = Column(String)
    timestamp = Column(TIMESTAMP)
    token_type = "Bearer"
    owner_username = Column(Integer, ForeignKey("users.username"))

    owner = relationship("User", back_populates="token")