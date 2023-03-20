#uvicorn main:app --reload
from fastapi import FastAPI, Request, Cookie
from fastapi.middleware.cors import CORSMiddleware


import jwt #jwt & pyjwt
import datetime


app = FastAPI()

origins = [ # Which request the API will allow
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {} # Use MongoDB instead
SECRET_KEY = "somethingsomethingxx" # use env instead

@app.get("/")
def root(request: Request):
    
    return { "sessions": request.cookies }

@app.post("/api/auth/login")
async def handle(request: Request = None):
    if request is None:
        return { "error": "BAD" }

    # Get JSON data from request body
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    # Do some validation on the credentials.
    if username == "" or password == "":
        return {"error": "Invalid username or password"}
    
    # Generate new jwt token and store it
    token = generate_jwt_token(username)
    sessions[token] = username

    # return the token in the response
    return {"token": token}

def generate_jwt_token(username: str):
    payload = {
        'username': username
    }

    # set the expiration time to 1 hour from now
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    # encode the token using the HS256 algorithm and the secret key
    token = jwt.encode({'exp': expiration, **payload}, SECRET_KEY, algorithm='HS256')

    return token

def is_user_authorized(token: str = None) -> bool:
    if token is None | token is "undefined" | token not in sessions:
        return False
    return True