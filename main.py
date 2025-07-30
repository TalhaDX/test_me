from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get the PostgreSQL URL from the .env file
DATABASE_URL = os.getenv("POSTGRES_URL")

if not DATABASE_URL:
    raise RuntimeError("POSTGRES_URL not found in .env")

# Set up SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define database model
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

# Create the table
Base.metadata.create_all(bind=engine)

# Pydantic schema for request and response
class ItemCreate(BaseModel):
    name: str

class ItemRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# Create FastAPI app
app = FastAPI()

# POST: Add new item
@app.post("/items", response_model=ItemRead)
def create_item(item: ItemCreate):
    db = SessionLocal()
    db_item = Item(name=item.name)
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# GET: Read all items
@app.get("/items", response_model=list[ItemRead])
def read_items():
    db = SessionLocal()
    try:

        items = db.query(Item).all()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
