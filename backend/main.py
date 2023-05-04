'''Set up a FastAPI application with two routers and various middleware.

This Python file sets up a FastAPI application with two routers: `relay_router` and `frontend_router`. It creates a MongoDB instance and connects to it. The `relay_router` is prefixed with "/v1/api/relay" and the `frontend_router` is prefixed with "/v1/api/frontend". 

The CORS middleware is configured to allow requests from any origin and with any method or header. 

Attributes:
    mongo (MongoDB): A MongoDB instance that connects to a database with the provided credentials.
    app (FastAPI): The FastAPI application instance.
    
Note:
    The `middleware` function is imported from middleware.py. See it for more details.
    Some functionality from Starlette is needed because FastAPI does not have it. FastAPI is build on
    top of Starlette. Therefore we use Starlette in some places.

'''

# FastAPI.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FastAPI routes (This is our own routes).
from routes.relay_routes import relay_router
from routes.frontend_routes import frontend_router

# Database MongoDB.
from mongodb_handler import MongoDB

# Own middleware.
from middleware import middleware

# Create new instance of mongoDB class and connect to it.
mongo = MongoDB()
mongo.connect(mongodb_username="admin", mongodb_password="kmEuqHYeiWydyKpc")

# Create a new instance of FastAPI class and includes relay and frontend routes.
app = FastAPI()
app.include_router(relay_router, prefix="/v1/api/relay")
app.include_router(frontend_router, prefix="/v1/api/frontend")

# Update app instance with our own middleware.
app.middleware("http")(middleware)

# Update app instance with CORS middleware.
app.add_middleware( # This is from Starlette. We cannot use FastAPI for this.
    CORSMiddleware, # We add FastAPI CORSMiddleware policy.
    allow_origins=["*"], # Allow all origins (host).
    allow_credentials=True, # Allow all and every type of credentials.
    allow_methods=["*"], # Allow all methods (GET, POST, PUT...).
    allow_headers=["*"], # Allow all headers. 
)

# Serve FastAPI app.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="main:app", # What Python file to serve. In our case it is ´main´.
        host="", # The host that the backend will run on
        port=8000, # The port that the backend will run on
        reload=True # For debugging.
    )