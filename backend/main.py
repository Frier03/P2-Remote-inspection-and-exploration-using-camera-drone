#uvicorn main:app --reload
from fastapi import Cookie, FastAPI, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler #https://coderslegacy.com/python/apscheduler-tutorial-advanced-scheduler/
from starlette.responses import Response #https://www.starlette.io/responses/
import json
from time import time

app = FastAPI()
scheduler = BackgroundScheduler()

sessions = {} # Stores all sessions created
scheduler.start()

@app.get("/") #/
def read_root():
    return {"Active sessions": sessions}

@app.get("/auth") #/auth
def authenticate(session_id: str = Cookie(None)):
    # Is user authorized?
    if session_id is None or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    sessions[session_id]['created_at'] = time()
    response = Response(content=json.dumps({"message": "OK", "data": sessions[session_id]}).encode())
    response.set_cookie(key="session_id", value=session_id, secure=True)
    return response

@app.post("/login") #/login
def login(username: str = None, password: str = None, session_id: str = Cookie(None)):
    if session_id is not None and session_id in sessions:
        # User has already logged in before
        sessions[session_id]['created_at'] = time()
        response = Response(content=json.dumps({"message": "OK"}).encode())
        response.set_cookie(key="session_id", value=session_id, secure=True)
        return response
    
    # Username and password validation (default set to None for now)
    if username is None or password is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_id, session = generate_session() # Generates a new session and stores inside sessions
    session['username'] = username
    response = Response(content=json.dumps({"message": "OK"}).encode())
    response.set_cookie(key="session_id", value=session_id, secure=True)

    return response

@app.get("/logout")
def logout(session_id: str = Cookie(None)):
    # Is user authorized?
    if session_id is None or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    del sessions[session_id]
    
    response = Response(content=json.dumps({"message": "OK"}).encode())
    return response
   
def generate_session():
    session_id = str(len(sessions))
    session = {
        'session_id': session_id,
        'username': None,
        'created_at': time(),
    }
    sessions[session_id] = session
    return session_id, session

@scheduler.scheduled_job('interval', seconds=5)
def cleanup_sessions():
    # Remove sessions that has been inactive for < 10 minutes
    now = time()
    for session_id, session in list(sessions.items()):
        if now - session['created_at'] > 600:  # 10 minutes
            del sessions[session_id]