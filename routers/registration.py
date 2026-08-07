from fastapi import APIRouter, Depends,File, UploadFile, Form
from sqlalchemy.orm import Session
from dbconnection import get_db
from models.registration import Registration
from services.redis_service import redis_client
from security import hash_password,verify_access_token,rate_limit
from schemas.registration import (
    RegistrationRequest,
    RegistrationResponse,
    RegistrationResponseget
)
from pathlib import Path
import shutil
import uuid
import json
import aiofiles
import asyncio

#value = redis_client.get("my_key")

#print(value)
#print("value: ", value)

router = APIRouter(
    prefix="/registration",
    tags=["Registration"]
)
@router.get(
    "/mobile/{mobile}",
    response_model=RegistrationResponseget
)
def get_user_by_mobile(
    mobile: str,
    db: Session = Depends(get_db)
):
    # 1. Create Redis key
    cache_key = f"user:mobile:{mobile}"
    print("cache_key: ", cache_key)
    # 2. Check Redis
    cached_user = redis_client.get(cache_key)
    if cached_user:
        print("Data coming from Redis")
        return json.loads(cached_user)


    user = db.query(Registration).filter(Registration.mobile == mobile).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "mobile": user.mobile,
        "photo": user.photo
    }

    # 3. Cache the user data in Redis
    redis_client.setex(
        cache_key,
        300,
        json.dumps(user_data)
    )
        
    return user_data

@router.post("/", response_model=RegistrationResponse)
def register(
    #user: RegistrationRequest, //this used when pass data from json body but now we are passing data from form-data so we need to use Form and Filebelow is the code for that
     name: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    password: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    UPLOAD_DIR = Path("uploads/photos")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
 # Generate unique filename
    extension = Path(photo.filename).suffix
    filename = f"{uuid.uuid4()}{extension}"
    
    # Physical location
    file_path = UPLOAD_DIR / filename

    # Save image physically
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)
    #hashed_password = hash_password(user.password)
    hashed_password = hash_password(password)
    new_user = Registration(
        #name=user.name,
        #email=user.email,
        #mobile=user.mobile,
        #password=hashed_password
        name=name,
        email=email,
        mobile=mobile,
        password=hashed_password,
        photo=filename
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registration successful",
        "id": new_user.id
    }

@router.get(
    "/redis_cache",
    response_model=list[RegistrationResponseget]
)
async def get_user_using_redis(
     user_id: int = Depends(rate_limit(5)),
   
     cache_key = "all_users",
     db: Session = Depends(get_db)
):
    
    
    # 2. Check Redis
    #cached_user = redis_client.get(cache_key)
    
    # 2. Check Redis
    cached_user = redis_client.get(cache_key)
    if cached_user:
        print("cached_user: ", cached_user)
        return json.loads(cached_user)


    
    users =  await db.query(Registration).all()
    
    if not users:
        raise HTTPException(status_code=404, detail="User not found")

    user_data =[ {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "mobile": user.mobile,
        "photo": user.photo
    }
     for user in users
    ]
  #  print("user_data: ", user_data)
    # 3. Cache the user data in Redis
    redis_client.setex(
        cache_key,
        300,
        json.dumps(user_data)
    )
        
    return user_data
#
@router.get(
    "/redis_cache",
    response_model=list[RegistrationResponseget]
)
@router.get("/async_sys")
async def async_sys():
        import asyncio
        await asyncio.sleep(5)
        return {"message": "This is an async endpoint."}

@router.get("/file_system")
async def file_system():    
      file_path = "uploads/photos/python_doc.txt"
      async with aiofiles.open(file_path, mode='r') as file:
        content = await file.read()
        return {"message": "File read successfully.", "content": content}

@router.put("/update_login/{user_id}",
           response_model=RegistrationResponseget)    
async def update_login(user_id:int, db: Session = Depends(get_db)):
    try:
        user = db.query(Registration).filter(Registration.id == user_id).first()
        if not user:
         raise HTTPException(status_code=404, detail="User not found")
    # Update the login timestamp
        user.name = "sinku2"
        db.commit()
    #db.refresh(user)
    except Exception:
     db.rollback()
     raise
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "mobile": user.mobile,
        "photo": user.photo
    }