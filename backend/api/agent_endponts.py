import os

import bcrypt
from fastapi import FastAPI, Depends, HTTPException
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only. Use your domain in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base = declarative_base()


class LoginRequest(BaseModel):
    username: str
    password: str


class User(Base):
    __tablename__ = 'users'
    username = Column(String(50), primary_key=True)
    password_hash = Column(String(100))


DB_USER = os.getenv("AWS_RDS_MySQL_USERNAME")
DB_PASSWORD = os.getenv("AWS_RDS_MySQL_PASSWORD")
DB_HOST = os.getenv("AWS_RDS_MySQL_HOST")
DB_PORT = os.getenv("AWS_RDS_MySQL_PORT")
DB_NAME = os.getenv("AWS_RDS_MySQL_NAME")
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not bcrypt.checkpw(data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful"}


@app.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(data: LoginRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt())

    new_user = User(username=data.username, password_hash=hashed_password.decode('utf-8'))
    db.add(new_user)
    db.commit()

    return {"message": "User created successfully"}
