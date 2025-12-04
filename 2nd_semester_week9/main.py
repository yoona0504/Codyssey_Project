from fastapi import FastAPI

from database import Base
from database import engine
from models import Question  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI()
