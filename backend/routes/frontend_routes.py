from fastapi import HTTPException, status, APIRouter, Depends
from passlib.context import CryptContext

from token_helper_functions import generate_access_token
from mongodb_handler import get_mongo
from models import UserModel

pwd_context = CryptContext(schemes=["bcrypt_sha256"])
frontend_router = APIRouter()

@frontend_router.get("/protected")
def handle():
    return { "message": "Authorized" }

@frontend_router.post("/logout")
async def handle():
    return { "message": "Logout" }

@frontend_router.post("/login")
async def handle(user: UserModel, mongo: object = Depends(get_mongo)):
    if not authenticate_user(user, mongo):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    # Generate new HS256 access token
    token = generate_access_token(data={"sub": user.name}, minutes=24*60)
    return {"access_token": f"Bearer {token}"}


def authenticate_user(user: UserModel, mongo: object):
    user_exist = mongo.name_exist({ 'name': user.name }, mongo.users_collection)
    if not user_exist:
        return False
    if not verify_password(user.password, user_exist.get('hashed_password')):
        return False
    return True

def verify_password(plain_password: str, hashed_password: str) -> bool: #TODO Make this more secure
    # Placeholder for validating the password
    if len(plain_password) < 3:
        return False
    return pwd_context.verify(plain_password, hashed_password) # True/False depends if both hashes passwords matches
