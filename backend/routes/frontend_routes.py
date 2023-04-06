from fastapi import HTTPException, status, APIRouter, Depends

from helper_functions import generate_access_token
from mongodb_handler import get_mongo
from models import UserModel

frontend_router = APIRouter()

@frontend_router.get("/protected")
def handle():
    return { "message": "Authorized" }

@frontend_router.post("/logout")
async def handle():
    return { "message": "Logout" }

@frontend_router.post("/login")
async def handle(user: UserModel, mongo: object = Depends(get_mongo)):
    if not mongo.authenticate(user, mongo):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    # Generate new HS256 access token
    token = generate_access_token(data={"sub": user.name}, minutes=24*60)
    return {"access_token": f"Bearer {token}"}
