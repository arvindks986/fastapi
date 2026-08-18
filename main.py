from fastapi import FastAPI,Depends
from pydantic import BaseModel
from dbconnection import engine,Base
from sqlalchemy.orm import Session
from sqlalchemy import text
from dbconnection import get_db
from routers.registration import router as registration_router
from services.redis_service import redis_client
from routers.auth import router as auth_router
#app = FastAPI()
app = FastAPI(root_path="/python")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(registration_router)
app.include_router(auth_router)


@app.get("/redis-test")
def redis_test():
    # Set a value in Redis
    redis_client.set("my_key", "Hello, Redis!")

    # Get the value from Redis
    value = redis_client.get("my_key")

    return {"value": value}







@app.get("/")
def home():
    return {"message": "Hello Arvind"}

@app.get("/firstapi")
def first_api():
     return {"message":"Let's Start"}   

class User(BaseModel):
    name: str
    age: int     

@app.get("/postapi")
def post_api(db: Session = Depends(get_db)):
    query = text("SELECT * FROM officer_login")
    result = db.execute(query)

    return result.mappings().all()
     