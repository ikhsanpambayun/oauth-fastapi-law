from datetime import datetime
from secrets import token_hex
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
import models, schemas


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.User):
    hashed_password = generate_password_hash(user.hashed_password, 'sha256')
    db_user = models.User(
        username = user.username,
        hashed_password = hashed_password,
        full_name = user.full_name,
        npm = user.npm,
        client_id = user.client_id,
        client_secret = user.client_secret
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_token(db: Session, token: str):
    return db.query(models.Token).filter(models.Token.access_token == token).first()


def get_tokens(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Token).offset(skip).limit(limit).all()


def create_token(db: Session, username: str):
    db_token = models.Token(
        access_token = token_generator(),
        refresh_token = token_generator(),
        timestamp = datetime.now(),
        owner_username = username
        )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def delete_token(db: Session, username:str):
    return db.query(models.Token).filter(models.Token.owner_username == username).delete()


def pasword_checker(password: str, hashed: str):
    check = check_password_hash(hashed, password)
    return check

def token_generator():
    return token_hex(40)