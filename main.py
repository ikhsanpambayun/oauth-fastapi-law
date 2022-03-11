from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Form, status
from sqlalchemy.orm import Session

import crud, models, schemas

from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.User, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.post("/users/check-password/")
def check_password( 
    response:Response, 
    username:str = Form(...),
    password:str = Form(...),
    db: Session = Depends(get_db),
    ):
    db_user = crud.get_user(db, username)
    return crud.check_password_hash(db_user.hashed_password, password)

@app.post("/oauth/token/")
def create_token( 
    response:Response, 
    username:str = Form(...),
    password:str = Form(...),
    grant_type:str = "password",
    client_id:str = Form(...),
    client_secret:str = Form(...),

    db: Session = Depends(get_db),
    ):
    context = {}
    user = crud.get_user(db, username)
    if user and crud.check_password_hash(user.hashed_password, password) and user.client_id == client_id and user.client_secret == client_secret:
        crud.delete_token(db, username)
        token = crud.create_token(db, username)
        context["access_token"] = token.access_token
        context["expires_in"] = 300
        context["token_type"] = token.token_type
        context["scope"] = "null"
        context["refresh_token"] = token.refresh_token
        return context
    else:
        context["error"] = "invalid_request"
        context["Error_description"] = "ada kesalahan masbro!"
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return context

@app.post("/oauth/resource")
def get_resource(request: Request,response: Response, db: Session = Depends(get_db)):
    context = {}
    authorization: str = request.headers.get("Authorization")
    if not authorization == None:
        type, token = authorization.split()
        if type == "Bearer" and token:
            db_token = crud.get_token(db, token)
            if db_token:
                expire = (datetime.now() - db_token.timestamp).total_seconds()
                if expire <= 300:
                    db_user = crud.get_user(db, username=db_token.owner_username)
                    context["access_token"] = db_token.access_token
                    context["client_id"] = db_user.username
                    context["full_name"] = db_user.full_name
                    context["npm"] = db_user.npm
                    context["expires"] = 300 - expire
                    context["refresh_token"] = db_token.refresh_token
                    return context
    context["error"] = "invalid_request"
    context["Error_description"] = "Token Salah masbro"
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return context